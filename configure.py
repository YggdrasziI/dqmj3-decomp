#!/usr/bin/env python3

###
# Generates build files for the project.
# This file also includes the project configuration,
# such as compiler flags and the object matching status.
#
# Usage:
#   python3 configure.py
#   ninja
#
# Append --help to see available options.
###

import argparse
import sys
from pathlib import Path

from tools.project import (
    Matching,
    NonMatching,
    Object,
    ProgressCategory,
    ProjectConfig,
    calculate_progress,
    generate_build,
    is_windows,
)

# Game versions
DEFAULT_VERSION = 0
VERSIONS = [
    "jpn",  # 0: CTR-P-BJ3J, remaster version 0
]

parser = argparse.ArgumentParser()
parser.add_argument(
    "mode",
    choices=["configure", "progress"],
    default="configure",
    help="script mode (default: configure)",
    nargs="?",
)
parser.add_argument(
    "-v",
    "--version",
    choices=VERSIONS,
    type=str.lower,
    default=VERSIONS[DEFAULT_VERSION],
    help="version to build",
)
parser.add_argument(
    "--build-dir",
    metavar="DIR",
    type=Path,
    default=Path("build"),
    help="base build directory (default: build)",
)
parser.add_argument(
    "--compilers",
    metavar="DIR",
    type=Path,
    help="path to compilers, containing <version>/bin/armcc.exe (optional)",
)
if not is_windows():
    parser.add_argument(
        "--wrapper",
        metavar="BINARY",
        type=Path,
        help="path to wibo or wine (optional)",
    )
parser.add_argument(
    "--objdiff",
    metavar="BINARY",
    type=Path,
    help="path to objdiff-cli (optional)",
)
parser.add_argument(
    "--non-matching",
    dest="non_matching",
    action="store_true",
    help="also link units that do not match yet (the result is not verified)",
)
parser.add_argument(
    "--no-progress",
    dest="progress",
    action="store_false",
    help="disable progress calculation",
)
args = parser.parse_args()

config = ProjectConfig()
config.version = str(args.version)

# Apply arguments
config.build_dir = args.build_dir
config.compilers_path = args.compilers
config.objdiff_path = args.objdiff
config.non_matching = args.non_matching
config.progress = args.progress
if not is_windows():
    config.wrapper = args.wrapper
config.configure_args = sys.argv[1:]
if "progress" in config.configure_args:
    config.configure_args.remove("progress")

# Tool versions
# Used when the tool is neither passed on the command line nor found on PATH.
config.wibo_tag = "1.2.0"
config.objdiff_tag = "v3.8.2"

# Not identified yet (roadmap step 2). RVCT 4.1 build 894 is a placeholder taken
# from New Super Mario Bros. 2 (BigRed); nothing in this game confirms it.
config.armcc_version = "4.1/b894"
config.scratch_compilers = {
    "4.1/b894": "armcc_41_894",
}

# Base flags, common to most source files.
# Placeholders from BigRed until notes/COMPILER.md proves them for this game.
cflags_base = [
    "--cpp",
    "--arm",
    "--cpu=MPCore",
    "--fpmode=fast",
    "--apcs=/interwork",
    "--split_sections",
    "-O3",
    "-Otime",
    "--no_rtti",
    "--no_rtti_data",
    "--signed_chars",
    "-Iinclude",
    "-Isrc",
]
# Code that is equivalent to the original but does not compile to the same
# instructions yet is wrapped in #ifdef NON_MATCHING
if args.non_matching:
    cflags_base.append("-DNON_MATCHING")
config.cflags = cflags_base

config.libs = [
    # No source files yet.
]

# Optional extra categories for progress tracking
# Categories for progress tracking. Code without a source file is attributed to
# one of these by the regions in config/<version>/config.toml.
config.progress_categories = [
    ProgressCategory("game", "Game"),
    ProgressCategory("sdk", "Runtime and SDK"),
    ProgressCategory("nw", "NintendoWare"),
    ProgressCategory("net", "Network libraries"),
    ProgressCategory("unknown", "Unidentified"),
]

config.progress_image_title = None  # badges are drawn by tools/progress_badges.py (step 3)

if args.mode == "configure":
    # Write build.ninja and objdiff.json
    generate_build(config)
elif args.mode == "progress":
    # Print progress information
    calculate_progress(config)
else:
    sys.exit("Unknown mode: " + args.mode)
