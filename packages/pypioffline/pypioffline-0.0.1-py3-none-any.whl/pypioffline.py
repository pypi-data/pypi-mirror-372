#!/usr/bin/env python
#
# download packages from https://pypi.python.org
#

from typing import cast, TypedDict, Optional, List, Dict
from typing import Any
from collections.abc import Generator
from pathlib import Path
import argparse
import sys
import os
import time
import logging
import json
import re

import asyncio
import aiofiles
import aiohttp

from lxml import html
from aiohttp import ClientSession, ClientTimeout
from tqdm.asyncio import tqdm_asyncio
from wheel_filename import parse_wheel_filename, InvalidFilenameError


TIMEOUT: ClientTimeout = aiohttp.ClientTimeout(
    total=300,  # maximum total request time
    connect=60,  # time to establish connection
    sock_connect=60,  # time to wait before socket connect
    sock_read=100,  # time to wait between reads
)

WORKERS = 10  # number of concurrent download workers

CONFIG_PATH = os.path.expanduser(os.environ.get("PYPIOFFLINE_CONFIG", "~/.pypioffline"))

DEFAULT_CONFIG = {
    "repository": os.path.expanduser("~/pypioffline"),
    "python_versions": ["cp310", "py3", "py2.py3", "py3.10", "py310", "any"],
    "package_types": [
        "bdist_wheel",
    ],
    "extensions": [
        "whl",
    ],
    "platforms": ["win_amd64", "any"],
}


class MinifiedMetaDict(TypedDict):
    info: Dict[str, str]
    releases: Dict[str, List[Dict[str, Optional[str]]]]
    urls: List["PackageUrlDict"]


class PackageUrlDict(TypedDict):
    url: str
    filename: str
    packagetype: str
    python_version: str
    size: int
    name: str


def chain_generators(urls, *filters) -> Any:
    """Apply a series of generator filters to the list of URLs."""

    for f in filters:
        urls = f(urls)
    return urls


async def fetch_and_parse(url: str):
    """Fetch a URL and parse the HTML to extract all links."""

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            total_size = int(resp.headers.get("Content-Length", 0))

            # Accumulate chunks in memory (PyPI index is ~20–30 MB, fits fine)
            content = bytearray()
            with tqdm_asyncio(
                total=total_size, unit="B", unit_scale=True, desc="Downloading"
            ) as pbar:
                async for chunk in resp.content.iter_chunked(65536):
                    content.extend(chunk)
                    pbar.update(len(chunk))

    # Parse once after full download
    tree = html.fromstring(bytes(content))
    links = [a.text for a in tree.xpath("//a")]
    return links


async def get_names():
    """Fetch the list of package names from PyPI simple index."""
    return await fetch_and_parse("https://pypi.org/simple/")


def load_cache(cache_path, ttl):
    """Load cached data if it exists and is fresh."""
    if not cache_path.exists():
        return None
    try:
        with open(cache_path, "r") as f:
            cached = json.load(f)
        if time.time() - cached["timestamp"] > ttl:
            return None
        return cached["data"]
    except Exception:
        return None


def save_cache(cache_path, data) -> None:
    """Save data to cache with current timestamp."""
    with open(cache_path, "w") as f:
        json.dump({"timestamp": time.time(), "data": data}, f)


async def get_names_cached(ttl, cache_path, clear_cache=False):
    """Get package names with caching."""
    if clear_cache:
        cache_path.unlink(missing_ok=True)
    else:
        cached = load_cache(cache_path, ttl)
        if cached is not None:
            logging.info("Loaded package names from cache")
            return cached
    # Fallback to fetch
    names = await fetch_and_parse("https://pypi.org/simple/")
    save_cache(cache_path, names)
    return names


def minify_meta(json: dict) -> MinifiedMetaDict:
    """Minify the package metadata to only include necessary fields."""

    info: Dict[str, str] = {
        "name": json.get("info", {}).get("name"),
        "version": json.get("info", {}).get("version"),
    }

    releases: Dict[str, List[Dict[str, Optional[str]]]] = {}
    for version, files in json.get("releases", {}).items():
        releases[version] = [{"filename": file.get("filename")} for file in files]

    urls: List[PackageUrlDict] = []
    for url in json.get("urls", []):
        urls.append(
            {
                "url": url.get("url"),
                "filename": url.get("filename"),
                "packagetype": url.get("packagetype"),
                "python_version": url.get("python_version"),
                "size": url.get("size"),
                "name": info["name"],
            }
        )

    return {
        "info": info,
        "releases": releases,
        "urls": urls,
    }


async def fetch(url: str, session: ClientSession):
    """Download a single URL using aiohttp with concurrency limit."""

    try:
        async with session.get(url, timeout=TIMEOUT) as response:
            if response.status != 200:
                logging.debug(f"Failed to fetch {url}: {response.status}")
                return None
            json = await response.json()
            return minify_meta(json)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}", exc_info=True)


def sanitize_json(obj):
    """Recursively replace newlines in all string values in a dict."""
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json(v) for v in obj]
    elif isinstance(obj, str):
        return obj.replace("\n", "\\n")
    else:
        return obj


async def fetch_meta_data(
    names, num_workers, cache_path, url="https://pypi.python.org/pypi"
):
    """Fetch metadata for a list of package names and stream to a file."""

    urls = [f"{url}/{name}/json" for name in names]
    queue = asyncio.Queue()

    for u in urls:
        await queue.put(u)

    cache_path.write_text("")

    async with (
        aiohttp.ClientSession() as session,
        aiofiles.open(cache_path, "w") as out_file,
    ):
        write_lock = asyncio.Lock()
        terminate = False
        with tqdm_asyncio(
            total=len(urls),
            unit="pkg",
            unit_scale=True,
            desc="Fetching metadata",
        ) as pbar:

            async def worker():
                nonlocal terminate
                while True and not terminate:
                    try:
                        u = queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
                    try:
                        meta = await fetch(u, session)
                        if meta is not None:
                            meta = sanitize_json(meta)
                            async with write_lock:
                                await out_file.write(
                                    json.dumps(meta, ensure_ascii=True) + "\n"
                                )
                    except (KeyboardInterrupt, SystemExit, asyncio.CancelledError):
                        terminate = True
                        raise
                    finally:
                        pbar.update(1)
                        queue.task_done()

            tasks = [asyncio.create_task(worker()) for _ in range(num_workers)]
            try:
                await queue.join()
            except:
                logging.error("Exception whilst running tasks...", exc_info=True)

            for t in tasks:
                t.cancel()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(
                    result, (KeyboardInterrupt, SystemExit, asyncio.CancelledError)
                ):
                    raise result

    return cache_path


def stream_metadata_rows_filtered_by_package_name(
    names, path
) -> Generator[MinifiedMetaDict]:
    """Stream metadata rows filtered by package names."""
    return (
        meta
        for meta in stream_metadata_rows(path=path)
        if meta.get("info", {}).get("name") in names
    )


async def fetch_meta_data_cached(
    names,
    ttl,
    cache_path,
    clear_cache=False,
    num_workers=WORKERS,
    url="https://pypi.python.org/pypi",
) -> Generator[MinifiedMetaDict]:
    """Fetch package metadata with caching."""
    if clear_cache:
        cache_path.unlink(missing_ok=True)
    if cache_path.exists():
        mtime = cache_path.stat().st_mtime
        if time.time() - mtime < ttl:
            logging.info("Loaded package metadata from cache")
            return stream_metadata_rows_filtered_by_package_name(
                names=names, path=cache_path
            )

    # Fallback to fetch
    try:
        cache_path = await fetch_meta_data(
            names, cache_path=cache_path, num_workers=num_workers, url=url
        )
    except (asyncio.CancelledError, KeyboardInterrupt, SystemExit) as e:
        if cache_path.exists():
            cache_path.unlink(missing_ok=True)
            logging.error("Interrupted! Metadata cache cleared.")
        raise
    except Exception as e:
        if cache_path.exists():
            cache_path.unlink(missing_ok=True)
            logging.error("Exception during metadata fetch, cache cleared")
        raise

    return stream_metadata_rows_filtered_by_package_name(names=names, path=cache_path)


def filter_packages(packages, config) -> Generator[PackageUrlDict]:
    """Return a filtered generator."""

    filtered = filter_paths_exist(packages, repository=config["repository"])
    filtered = filter_in_platforms(filtered, platforms=config["platforms"])
    filtered = filter_in_extensions(filtered, extensions=config["extensions"])
    filtered = filter_in_package_types(filtered, package_types=config["package_types"])
    filtered = filter_in_python_versions(
        filtered, python_versions=config["python_versions"]
    )

    return filtered


def unsanitize_json(obj):
    """Recursively convert '\\n' back to '\n' in all string values."""
    if isinstance(obj, dict):
        return {k: unsanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [unsanitize_json(v) for v in obj]
    elif isinstance(obj, str):
        return obj.replace("\\n", "\n")
    else:
        return obj


def stream_metadata_rows(path) -> Generator[MinifiedMetaDict]:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                obj = json.loads(line)
                yield cast(MinifiedMetaDict, unsanitize_json(obj))
            except json.JSONDecodeError as e:
                logging.warning(f"Skipping invalid JSON line: {e}: content={line}")
                continue


def prune_to_latest_version(package_metadata, repository, dry_run=False):
    """
    For each package, keep only files for the latest version.
    Removes files for older versions.
    """
    pruned = []
    for pkg in package_metadata:
        latest_version = pkg.get("info", {}).get("version")
        releases = pkg.get("releases", [])
        # Only keep URLs matching the latest version
        try:
            logging.debug(
                f"Pruning package {pkg.get('info', {}).get('name')} to version {latest_version}"
            )
            filtered_releases = [
                (version, releases[version])
                for version in releases
                if version != latest_version
            ]
            logging.debug(f"Found {len(filtered_releases)} old version URLs to prune")
            old_versions = [version for version, release in filtered_releases]
            logging.debug(f"Old version URLs: {old_versions}")
            filtered_filenames = []
            for version, releases in filtered_releases:
                for release in releases:
                    if (
                        release.get("filename")
                        and Path(repository).joinpath(release.get("filename")).exists()
                    ):
                        filtered_filenames.append(release.get("filename"))
            logging.debug(f"Filtered filenames to remove: {filtered_filenames}")
            if not dry_run:
                for file_name in filtered_filenames:
                    path = Path(repository) / file_name
                    if path.exists():
                        logging.debug(f"Removing old version file: {path}")
                        path.unlink(missing_ok=True)
            pruned.extend(filtered_filenames)
        except InvalidFilenameError as e:
            logging.warning(f"Invalid wheel filename while pruning: {e}")
            continue
    return pruned


async def fetch_file(url: PackageUrlDict, session: ClientSession, repository):
    """Download a single URL using aiohttp with concurrency limit."""

    filename = Path(url["filename"]).name
    package_path = Path(repository) / url["name"]
    package_path.mkdir(parents=True, exist_ok=True)

    file_path = Path(repository) / package_path / filename

    logging.debug(f"Writing to: {file_path}")
    try:
        async with session.get(url["url"], timeout=TIMEOUT) as response:
            if response.status != 200:
                logging.debug(f"Failed to fetch {url['url']}: {response.status}")
                return None

            # Write to file in chunks
            async with aiofiles.open(file_path, "wb") as f:
                async for chunk in response.content.iter_chunked(
                    1024 * 1024
                ):  # 1 MB chunks
                    await f.write(chunk)

            return str(file_path)

    except Exception as e:
        logging.error(f"Error fetching {url}: {e}", exc_info=True)
        return None


async def fetch_urls(
    total_bytes, urls: Generator[PackageUrlDict], repository, num_workers=WORKERS
):
    """Fetch multiple URLs concurrently using a fixed number of worker tasks and a queue."""

    results = []
    queue = asyncio.Queue()

    for url in urls:
        await queue.put(url)

    async with aiohttp.ClientSession() as session:
        with tqdm_asyncio(
            total=total_bytes,
            unit="GB",
            unit_scale=1 / 1e9,
            unit_divisor=1,
            bar_format="{l_bar}{bar} {n:.2f}/{total:.2f} {unit} "
            "[{elapsed}<{remaining}, {rate_fmt}]",
            desc="Downloading",
        ) as pbar:

            async def worker():
                while True:
                    try:
                        url = queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
                    filename = await fetch_file(url, session, repository=repository)
                    if filename is not None:
                        pbar.update(url["size"])
                        results.append(filename)
                    queue.task_done()

            tasks = [asyncio.create_task(worker()) for _ in range(num_workers)]
            await queue.join()
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

    return results


def filter_in_python_versions(urls, python_versions) -> Generator[PackageUrlDict]:
    """Filter URLs by Python versions."""
    for url in urls:
        if url["python_version"] in python_versions:
            yield url


def filter_in_package_types(urls, package_types) -> Generator[PackageUrlDict]:
    """Filter URLs by package types."""
    for url in urls:
        if url["packagetype"] in package_types:
            yield url


def filter_in_extensions(urls, extensions) -> Generator[PackageUrlDict]:
    """Filter URLs by file extensions."""
    for url in urls:
        filename = url["filename"]
        suffixes = "".join(Path(filename).suffixes)  # e.g. '.tar.gz'
        for ext in extensions:
            # allow extensions with or without leading dot
            ext = ext if ext.startswith(".") else f".{ext}"
            if suffixes.endswith(ext):
                yield url
                break


def filter_in_platforms(urls, platforms) -> Generator[PackageUrlDict]:
    """Filter URLs by platform tags (for wheels)."""
    for url in urls:
        if url["packagetype"] == "bdist_wheel":
            try:
                pkg = parse_wheel_filename(url["filename"])
                for p in pkg.platform_tags:
                    if p in platforms:
                        yield url
                        break
            except InvalidFilenameError:
                logging.warning(f"Invalid wheel filename: {url['filename']}")
                continue
        else:
            yield url  # non-wheel packages are always included


def filter_paths_exist(urls, repository) -> Generator[PackageUrlDict]:
    """Filter out URLs whose files already exist in the repository."""
    for url in urls:
        filename = url["filename"]
        path = f"{repository}/{filename}"
        if not os.path.exists(path):
            yield url


def check_available_disk_space(path, total_size) -> bool:
    """Check if there is enough available disk space at the given path."""
    statvfs = os.statvfs(path)
    available_bytes = statvfs.f_frsize * statvfs.f_bavail
    if available_bytes < total_size:
        logging.error(
            f"Not enough disk space in {path}. Required: {total_size} bytes, Available: {available_bytes} bytes"
        )
        return False
    return True


def get_config(config_file, cli_args, skip_file_load=False) -> dict[str, Any]:
    config = DEFAULT_CONFIG.copy()
    if not skip_file_load:
        try:
            with open(config_file, "r") as f:
                config.update(json.load(f))
        except FileNotFoundError:
                logging.warning(f"Config file ({config_file}) not found, using defaults")

    # CLI overrides
    if getattr(cli_args, "repository", None):
        config["repository"] = cli_args.repository
    if getattr(cli_args, "python_versions", None):
        config["python_versions"] = cli_args.python_versions
    if getattr(cli_args, "package_types", None):
        config["package_types"] = cli_args.package_types
    if getattr(cli_args, "extensions", None):
        config["extensions"] = cli_args.extensions
    if getattr(cli_args, "platforms", None):
        config["platforms"] = cli_args.platforms

    config["repository"] = os.path.expanduser(config["repository"])
    config["repository"] = Path(config["repository"])
    if not config["repository"].parts[-1] == "simple":
        config["repository"] = config["repository"] / "simple"

    for c in sorted(config):
        logging.debug(f"{c:<15} = {config[c]}")

    logging.debug(f"Using config file {config_file}")

    return config


async def command_sync(cli_args) -> None:
    config = get_config(cli_args.config, cli_args)

    config["repository"].mkdir(parents=True, exist_ok=True)

    logging.info("starting Pypioffline mirror...")

    # Use package file if provided, else --package, else fetch all names
    if getattr(cli_args, "package_file", None):
        with open(cli_args.package_file, "r") as f:
            names = [line.strip() for line in f if line.strip()]
        logging.info(
            f"Syncing packages from file: {cli_args.package_file} ({len(names)} packages)"
        )
    elif cli_args.packages:
        names = cli_args.packages
        logging.info(f"Syncing specified packages: {names}")
    else:
        logging.info("getting packages names...")
        names = await get_names_cached(
            ttl=cli_args.names_cache_ttl,
            cache_path=Path(config["repository"]) / ".names_cache",
            clear_cache=cli_args.clear_names_cache,
        )
        logging.info(f"Got {len(names)} names")

    if cli_args.limit:
        names = names[: cli_args.limit]
        logging.info(f"Limiting to first {len(names)} names")

    # We need to parse the metadata twice:
    # 1. First to get the total size of all filtered packages for the progress bar
    # 2. Second to get the actual filtered packages to download

    # Fetch package meta data - first pass to get total size
    package_metadata: Generator[MinifiedMetaDict, None, None] = (
        await fetch_meta_data_cached(
            names,
            num_workers=cli_args.num_workers,
            ttl=cli_args.metadata_cache_ttl,
            cache_path=Path(config["repository"]) / ".metadata_cache",
            clear_cache=cli_args.clear_metadata_cache,
        )
    )

    urls: Generator[PackageUrlDict] = (
        url for pkg in package_metadata for url in pkg["urls"]
    )
    filtered: Generator[PackageUrlDict] = filter_packages(urls, config)

    total_bytes = sum(url["size"] for url in filtered)

    if check_available_disk_space(config["repository"], total_bytes):
        logging.info(
            f"Starting download of {total_bytes / 1e9:.2f} GB to {config['repository']}"
        )
    else:
        logging.error("Aborting due to insufficient disk space")
        sys.exit(1)

    # Fetch package meta data - second pass to get actual packages to download
    # We can't reuse the previous generator as it has been exhausted
    # So we fetch the metadata again (this time from the cache)

    package_metadata: Generator[MinifiedMetaDict, None, None] = (
        await fetch_meta_data_cached(
            names=names,
            ttl=cli_args.metadata_cache_ttl,
            clear_cache=False,
            cache_path=Path(config["repository"]) / ".metadata_cache",
        )
    )

    urls: Generator[PackageUrlDict] = (
        url for pkg in package_metadata for url in pkg["urls"]
    )
    filtered: Generator[PackageUrlDict] = filter_packages(urls, config)

    # Download the filtered packages
    await fetch_urls(
        total_bytes=total_bytes,
        urls=filtered,
        repository=config["repository"],
        num_workers=cli_args.num_workers,
    )

    if cli_args.prune:
        await command_prune(cli_args)

    logging.info("Generating Simple API indexes...")
    generate_simple_api_indexes(config["repository"])


async def command_prune(cli_args) -> None:
    config = get_config(cli_args.config, cli_args)

    names = await get_names_cached(
        ttl=cli_args.names_cache_ttl,
        cache_path=Path(config["repository"]) / ".names_cache",
        clear_cache=False,
    )

    # Prune old package versions if requested
    package_metadata: Generator[MinifiedMetaDict, None, None] = (
        await fetch_meta_data_cached(
            names=names,
            ttl=cli_args.metadata_cache_ttl,
            clear_cache=False,
            cache_path=Path(config["repository"]) / ".metadata_cache",
        )
    )

    logging.info("Pruning old package versions...")
    pruned_files = prune_to_latest_version(
        package_metadata, repository=config["repository"], dry_run=cli_args.dry_run
    )
    logging.info(
        f"Pruned {len(pruned_files)} old package files (dry_run={cli_args.dry_run})"
    )


async def command_search(cli_args) -> None:
    query = cli_args.query
    config = get_config(cli_args.config, cli_args)

    names = await get_names_cached(
        ttl=cli_args.names_cache_ttl,
        cache_path=Path(config["repository"]) / ".names_cache",
        clear_cache=False,
    )

    if getattr(cli_args, "regex", False):
        matched_names = [
            name for name in names if re.search(query, name, re.IGNORECASE)
        ]
    else:
        matched_names = [name for name in names if query.lower() == name.lower()]

    if not matched_names:
        logging.info(f"No packages found matching query '{query}'")
        return

    logging.info(f"Found {len(matched_names)} packages matching query '{query}'")

    for name in matched_names[: cli_args.limit]:
        print(name)


def generate_simple_api_indexes(simple_dir: Path) -> None:
    """
    Walks the simple_dir and generates index.html files for the Simple API.
    - simple_dir/index.html: links to all packages
    - simple_dir/<package>/index.html: links to all files for that package
    """

    package_names = []
    # Find all package directories
    for pkg_dir in sorted(simple_dir.iterdir()):
        if pkg_dir.is_dir():
            package_names.append(pkg_dir.name)
            files = [f.name for f in pkg_dir.iterdir() if f.is_file()]
            # Write package index.html
            pkg_index = pkg_dir / "index.html"
            with open(pkg_index, "w") as f:
                f.write("<html><body>\n")
                for filename in sorted(files):
                    f.write(f'<a href="{filename}">{filename}</a><br>\n')
                f.write("</body></html>\n")

    # Write root index.html
    root_index = simple_dir / "index.html"
    with open(root_index, "w") as f:
        f.write("<html><body>\n")
        for pkg in package_names:
            f.write(f'<a href="{pkg}/">{pkg}</a><br>\n')
        f.write("</body></html>\n")


async def command_serve(cli_args) -> None:

    config = get_config(cli_args.config, cli_args)

    from aiohttp import web

    app = web.Application()
    app.router.add_static("/simple/", path=config["repository"], show_index=True)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=cli_args.host, port=cli_args.port)
    logging.info(
        f"Serving {config['repository']} at http://{cli_args.host}:{cli_args.port}"
    )
    await site.start()

    try:
        while True:
            await asyncio.sleep(3600)  # Run forever
    except (KeyboardInterrupt, SystemExit):
        logging.info("Shutting down server...")
    finally:
        await runner.cleanup()


async def command_config(cli_args) -> None:
    config = get_config(cli_args.config, cli_args, skip_file_load=True)
    if config['repository'].parts[-1] == "simple":
        config['repository'] = config['repository'].parent
    config['repository'] = str(config['repository'])

    if not cli_args.full:
        print(json.dumps(config, indent=4))
        return

    # Parse the package_meta data to get all available platforms, package types, and python versions
    names = await get_names_cached(
        ttl=cli_args.names_cache_ttl,
        cache_path=Path(config["repository"]) / ".names_cache",
        clear_cache=cli_args.clear_names_cache,
    )
    package_metadata: Generator[MinifiedMetaDict, None, None] = (
        await fetch_meta_data_cached(
            names=names,
            ttl=cli_args.metadata_cache_ttl,
            clear_cache=cli_args.clear_metadata_cache,
            cache_path=Path(config["repository"]) / ".metadata_cache",
        )
    )
    urls: Generator[PackageUrlDict] = (
        url for pkg in package_metadata for url in pkg["urls"]
    )
    platforms = set()
    package_types = set()
    python_versions = set()
    for url in urls:
        package_types.add(url["packagetype"])
        python_versions.add(url["python_version"])
        if url["packagetype"] == "bdist_wheel":
            try:
                pkg = parse_wheel_filename(url["filename"])
                for p in pkg.platform_tags:
                    platforms.add(p)
            except InvalidFilenameError:
                logging.warning(f"Invalid wheel filename: {url['filename']}")
                continue
        else:
            platforms.add("any")
    config["platforms"] = sorted(platforms)
    config["package_types"] = sorted(package_types)
    config["python_versions"] = sorted(python_versions)

    print(json.dumps(config, indent=4))


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(description="Pypioffline downloader")

    # Global options
    parser.add_argument(
        "-c",
        "--config",
        default=CONFIG_PATH,
        help="Path to config file (default: ~/.pypioffline)",
    )
    parser.add_argument(
        "-r", "--repository", help="Repository folder (overrides config)"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v = INFO, -vv = DEBUG, default = WARNING)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging (overrides --log-level)",
    )
    parser.add_argument(
        "--names-cache-ttl",
        type=int,
        default=86400,
        help="Cache TTL for package names (seconds)",
    )
    parser.add_argument(
        "--metadata-cache-ttl",
        type=int,
        default=86400,
        help="Cache TTL for metadata (seconds)",
    )
    parser.add_argument(
        "--clear-names-cache", action="store_true", help="Clear the names cache"
    )
    parser.add_argument(
        "--clear-metadata-cache", action="store_true", help="Clear the metadata cache"
    )
    parser.add_argument(
        "--limit", type=int, default=0, help="Limit to first N packages (for testing)"
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=10,
        help="Number of concurrent workers (default=10)",
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Subcommand to run"
    )

    # sync subcommand
    sync_parser = subparsers.add_parser("sync", help="Sync packages from PyPI")
    sync_parser.add_argument(
        "-p", "--python-versions", nargs="+", help="Python versions to include"
    )
    sync_parser.add_argument(
        "-t", "--package-types", nargs="+", help="Package types to include"
    )
    sync_parser.add_argument(
        "-e", "--extensions", nargs="+", help="Extensions to include"
    )
    sync_parser.add_argument(
        "-P", "--platforms", nargs="+", help="Platforms to include"
    )
    sync_parser.add_argument(
        "--prune", action="store_true", help="Prune old package versions after download"
    )
    sync_parser.add_argument(
        "--package",
        dest="packages",
        action="append",
        help="Specify package name(s) to sync (can be used multiple times)",
    )
    sync_parser.add_argument(
        "--package-file",
        dest="package_file",
        help="Path to file containing package names (one per line)",
    )

    # search subcommand
    search_parser = subparsers.add_parser("search", help="Search for packages")
    search_parser.add_argument("query", help="Search query string")
    search_parser.add_argument(
        "--limit", type=int, default=10, help="Limit number of results"
    )
    search_parser.add_argument(
        "--regex",
        action="store_true",
        help="Treat the search query as a regular expression",
    )

    # prune subcommand
    prune_parser = subparsers.add_parser("prune", help="Prune old package versions")
    prune_parser.add_argument(
        "-p", "--python-versions", nargs="+", help="Python versions to include"
    )
    prune_parser.add_argument(
        "-t", "--package-types", nargs="+", help="Package types to include"
    )
    prune_parser.add_argument(
        "-e", "--extensions", nargs="+", help="Extensions to include"
    )
    prune_parser.add_argument(
        "-P", "--platforms", nargs="+", help="Platforms to include"
    )
    prune_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be pruned without deleting",
    )

    # serve subcommand
    serve_parser = subparsers.add_parser("serve", help="Serve the repository via HTTP")
    serve_parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind the server"
    )
    serve_parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind the server"
    )

    # create config subcommand
    prune_parser = subparsers.add_parser("config", help="Print sample config")
    prune_parser.add_argument(
        "--full",
        action="store_true",
        help="Include all platforms, package types, and python versions",
    )

    return parser.parse_args()


def main() -> None:
    args: argparse.Namespace = parse_args()

    # Set log level
    if args.verbose >= 2:
        log_level = logging.DEBUG
    elif args.verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    if args.debug:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level, format="%(asctime)s:%(levelname)s: %(message)s"
    )

    if args.command == "sync":
        asyncio.run(main=command_sync(args))
    elif args.command == "search":
        asyncio.run(main=command_search(args))
    elif args.command == "prune":
        asyncio.run(main=command_prune(args))
    elif args.command == "serve":
        asyncio.run(main=command_serve(args))
    elif args.command == "config":
        asyncio.run(main=command_config(args))
    else:
        raise ValueError(f"Unknown command: {args.command}")

    sys.exit(0)


if __name__ == "__main__":
    main()
