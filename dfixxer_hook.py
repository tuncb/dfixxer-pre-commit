#!/usr/bin/env python3
"""Pre-commit hook for dfixxer - Delphi/Pascal code formatter."""

import argparse
import json
import platform
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import List, Optional

DFIXXER_RELEASE_TAG = "v0.9.2"
DFIXXER_RELEASE_API_URL = f"https://api.github.com/repos/tuncb/dfixxer/releases/tags/{DFIXXER_RELEASE_TAG}"


def get_cache_dir() -> Path:
    """Get the cache directory for dfixxer binary."""
    cache_dir = Path.home() / ".cache" / "dfixxer-pre-commit" / DFIXXER_RELEASE_TAG
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_platform_info() -> tuple[str, str]:
    """Get platform and architecture information."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        return "windows", "x86_64"
    elif system == "darwin":
        return "macos", "x86_64"
    elif system == "linux":
        return "linux", "x86_64"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def get_binary_name(platform_name: str) -> str:
    """Get the expected binary name for the platform."""
    if platform_name == "windows":
        return "dfixxer.exe"
    else:
        return "dfixxer"


def find_download_asset(release_data: dict, platform_name: str, arch: str) -> tuple[Optional[str], Optional[str], bool]:
    """Find the preferred download URL for a platform (binary first, then zip)."""
    assets = release_data.get("assets", [])
    base_name = f"dfixxer-{platform_name}-{arch}"

    binary_asset_names = [base_name]
    if platform_name == "windows":
        binary_asset_names = [f"{base_name}.exe", f"{base_name}-{DFIXXER_RELEASE_TAG}.exe"]
    else:
        binary_asset_names = [base_name, f"{base_name}-{DFIXXER_RELEASE_TAG}"]

    zip_asset_names = [f"{base_name}-{DFIXXER_RELEASE_TAG}.zip", f"{base_name}.zip"]

    preferred_names = binary_asset_names + zip_asset_names
    for expected_name in preferred_names:
        for asset in assets:
            if asset.get("name") == expected_name:
                return asset.get("browser_download_url"), expected_name, expected_name.endswith(".zip")

    for asset in assets:
        asset_name = asset.get("name", "")
        if asset_name.startswith(base_name) and asset_name.endswith(".zip"):
            return asset.get("browser_download_url"), asset_name, True

    return None, None, False


def extract_binary_from_zip(zip_path: Path, binary_name: str, output_path: Path) -> None:
    """Extract the expected dfixxer binary from a zip archive."""
    with zipfile.ZipFile(zip_path) as zip_file:
        matches = [
            item
            for item in zip_file.infolist()
            if not item.is_dir() and Path(item.filename).name.lower() == binary_name.lower()
        ]

        if not matches:
            raise RuntimeError(f"Zip archive {zip_path.name} does not contain {binary_name}")

        with zip_file.open(matches[0]) as source, output_path.open("wb") as target:
            shutil.copyfileobj(source, target)


def download_dfixxer() -> Path:
    """Download dfixxer binary to cache directory."""
    cache_dir = get_cache_dir()
    platform_name, arch = get_platform_info()
    binary_name = get_binary_name(platform_name)
    binary_path = cache_dir / binary_name

    if binary_path.exists():
        return binary_path

    print("dfixxer not found, downloading...")

    # Get release info from a specific pinned tag.
    try:
        with urllib.request.urlopen(DFIXXER_RELEASE_API_URL) as response:
            release_data = json.loads(response.read().decode())
    except Exception as e:
        raise RuntimeError(f"Failed to fetch release info for {DFIXXER_RELEASE_TAG}: {e}")

    download_url, asset_name, is_zip = find_download_asset(release_data, platform_name, arch)

    if not download_url:
        raise RuntimeError(f"No binary found for {platform_name}-{arch} in release {DFIXXER_RELEASE_TAG}")

    # Download the binary (directly or extracted from zip).
    try:
        print(f"Downloading {download_url}...")
        if is_zip:
            archive_path = cache_dir / asset_name
            urllib.request.urlretrieve(download_url, archive_path)
            extract_binary_from_zip(archive_path, binary_name, binary_path)
            archive_path.unlink(missing_ok=True)
        else:
            urllib.request.urlretrieve(download_url, binary_path)
        binary_path.chmod(0o755)  # Make executable on Unix-like systems
        print(f"Downloaded dfixxer to {binary_path}")
        return binary_path
    except Exception as e:
        raise RuntimeError(f"Failed to download dfixxer: {e}")


def get_dfixxer_path() -> str:
    """Get path to dfixxer binary, downloading if necessary."""
    # Try to find dfixxer in PATH first
    try:
        result = subprocess.run(
            ["dfixxer", "--version"],
            capture_output=True,
            check=True
        )
        return "dfixxer"
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    # Download and use cached version
    try:
        binary_path = download_dfixxer()
        return str(binary_path)
    except RuntimeError as e:
        print(f"Error: {e}")
        return None


def run_dfixxer(filename: str) -> int:
    """Run dfixxer on a single file."""
    dfixxer_path = get_dfixxer_path()
    if not dfixxer_path:
        return 1

    try:
        result = subprocess.run(
            [dfixxer_path, "update", filename],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            print(f"dfixxer failed on {filename}:")
            if result.stderr:
                print(result.stderr)
            if result.stdout:
                print(result.stdout)
            return result.returncode

        return 0
    except Exception as e:
        print(f"Error running dfixxer: {e}")
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the pre-commit hook."""
    parser = argparse.ArgumentParser(description="Run dfixxer on Pascal files")
    parser.add_argument("filenames", nargs="*", help="Filenames to format")
    args = parser.parse_args(argv)

    retval = 0
    for filename in args.filenames:
        if run_dfixxer(filename) != 0:
            retval = 1

    return retval


if __name__ == "__main__":
    sys.exit(main())
