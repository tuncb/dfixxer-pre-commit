#!/usr/bin/env python3
"""Pre-commit hook for dfixxer - Delphi/Pascal code formatter."""

import argparse
import json
import platform
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import List, Optional


def get_cache_dir() -> Path:
    """Get the cache directory for dfixxer binary."""
    cache_dir = Path.home() / ".cache" / "dfixxer-pre-commit"
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


def download_dfixxer() -> Path:
    """Download dfixxer binary to cache directory."""
    cache_dir = get_cache_dir()
    platform_name, arch = get_platform_info()
    binary_name = get_binary_name(platform_name)
    binary_path = cache_dir / binary_name

    if binary_path.exists():
        return binary_path

    print("dfixxer not found, downloading...")

    # Get release info and explicitly prefer stable (non-pre-release) versions.
    api_url = "https://api.github.com/repos/tuncb/dfixxer/releases/latest"
    try:
        with urllib.request.urlopen(api_url) as response:
            release_data = json.loads(response.read().decode())
    except Exception as e:
        raise RuntimeError(f"Failed to fetch release info: {e}")

    if release_data.get("prerelease") or release_data.get("draft"):
        releases_url = "https://api.github.com/repos/tuncb/dfixxer/releases"
        try:
            with urllib.request.urlopen(releases_url) as response:
                releases = json.loads(response.read().decode())
        except Exception as e:
            raise RuntimeError(f"Failed to fetch releases list: {e}")

        stable_release = next(
            (
                release
                for release in releases
                if not release.get("prerelease") and not release.get("draft")
            ),
            None,
        )
        if not stable_release:
            raise RuntimeError("No stable release found (non-pre-release, non-draft)")
        release_data = stable_release

    # Find the correct asset
    asset_name = f"dfixxer-{platform_name}-{arch}"
    if platform_name == "windows":
        asset_name += ".exe"

    download_url = None
    for asset in release_data["assets"]:
        if asset["name"] == asset_name:
            download_url = asset["browser_download_url"]
            break

    if not download_url:
        raise RuntimeError(f"No binary found for {platform_name}-{arch}")

    # Download the binary
    try:
        print(f"Downloading {download_url}...")
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
