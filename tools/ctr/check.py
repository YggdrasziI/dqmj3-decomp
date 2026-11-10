#!/usr/bin/env python3
"""
Verifies that a built code image is identical to the original.

Usage:
    python tools/ctr/check.py config/jpn/config.toml build/jpn/code.bin [--stamp <file>]
"""

import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ctr.image import VersionConfig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    parser.add_argument("config", type=Path, help="path to config.toml")
    parser.add_argument("binary", type=Path, help="built code.bin")
    parser.add_argument("--stamp", type=Path, help="file to touch on success")
    args = parser.parse_args()

    config = VersionConfig(args.config)
    digest = hashlib.sha1(args.binary.read_bytes()).hexdigest()
    if digest != config.hash:
        print(f"{args.binary}: FAILED", file=sys.stderr)
        print(f"  expected: {config.hash}", file=sys.stderr)
        print(f"  actual:   {digest}", file=sys.stderr)
        sys.exit(1)
    print(f"{args.binary}: OK")
    if args.stamp:
        args.stamp.parent.mkdir(parents=True, exist_ok=True)
        args.stamp.write_text(digest + "\n")


if __name__ == "__main__":
    main()
