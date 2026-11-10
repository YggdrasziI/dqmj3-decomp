#!/usr/bin/env python3
"""
Downloads the external tools the build needs.

Usage:
    python tools/download_tool.py <tool> <output> --tag <tag>

Tools:
    armcc      RVCT compiler. <tag> is the build to extract (e.g. 4.1/b894) and
               <output> the path of the resulting armcc.exe.
    wibo       Minimal Win32 loader used to run armcc on Linux and macOS.
    objdiff    objdiff-cli, used to generate progress reports.
"""

import argparse
import io
import os
import platform
import shutil
import stat
import sys
import urllib.request
import zipfile
from pathlib import Path

ARMCC_URL = "https://github.com/decompme/compilers/releases/download/compilers/armcc.zip"


def host() -> tuple:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if machine in ("amd64", "x86_64"):
        machine = "x86_64"
    elif machine in ("arm64", "aarch64"):
        machine = "aarch64"
    return system, machine


def wibo_url(tag: str) -> str:
    system, machine = host()
    if system == "darwin":
        asset = "wibo-macos"
    elif system == "linux" and machine in ("x86_64", "i686"):
        asset = f"wibo-{machine}"
    else:
        raise SystemExit(
            f"wibo is not available for {system}/{machine}. Install wine and pass --wrapper to configure.py."
        )
    return f"https://github.com/decompals/wibo/releases/download/{tag}/{asset}"


def objdiff_url(tag: str) -> str:
    system, machine = host()
    if system == "darwin":
        system = "macos"
        if machine == "aarch64":
            machine = "arm64"
    elif system == "windows" and machine == "aarch64":
        machine = "arm64"
    suffix = ".exe" if system == "windows" else ""
    return (
        f"https://github.com/encounter/objdiff/releases/download/{tag}/"
        f"objdiff-cli-{system}-{machine}{suffix}"
    )


def fetch(url: str) -> bytes:
    print(f"Downloading {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "decomp-build"})
    with urllib.request.urlopen(request) as response:
        return response.read()


def download_binary(url: str, output: Path) -> None:
    data = fetch(url)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    output.chmod(output.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def download_armcc(tag: str, output: Path) -> None:
    # <output> is <root>/<tag>/bin/armcc.exe
    root = output
    for _ in range(len(Path(tag).parts) + 2):
        root = root.parent
    prefix = tag.strip("/") + "/"
    with zipfile.ZipFile(io.BytesIO(fetch(ARMCC_URL))) as archive:
        members = [m for m in archive.infolist() if m.filename.startswith(prefix)]
        if not members:
            raise SystemExit(f"armcc build {tag} is not in the archive")
        for member in members:
            target = root / member.filename
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
    if not output.is_file():
        raise SystemExit(f"{output} was not found in the archive")
    os.utime(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Downloads the external tools the build needs.")
    parser.add_argument("tool", choices=["armcc", "wibo", "objdiff"])
    parser.add_argument("output", type=Path)
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()

    if args.tool == "armcc":
        download_armcc(args.tag, args.output)
    elif args.tool == "wibo":
        download_binary(wibo_url(args.tag), args.output)
    else:
        download_binary(objdiff_url(args.tag), args.output)


if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        sys.exit(f"error: {e}")
