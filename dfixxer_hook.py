#!/usr/bin/env python3
"""Pre-commit hook for dfixxer - Delphi/Pascal code formatter."""

import argparse
import subprocess
import sys
from typing import List, Optional


def run_dfixxer(filename: str) -> int:
    """Run dfixxer on a single file."""
    try:
        result = subprocess.run(
            ["dfixxer", "update", filename],
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
    except FileNotFoundError:
        print("Error: dfixxer is not installed or not in PATH.")
        print("Please install dfixxer from: https://github.com/tuncb/dfixxer")
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