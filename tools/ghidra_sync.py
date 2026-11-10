#!/usr/bin/env python3
"""Creates or updates the Ghidra project from symbols.txt, without the Ghidra GUI.

The first run imports build/<version>/code.elf (written by tools/ghidra_elf.py) into
a new project as ARM:LE:32:v6; every run then applies symbols.txt with
tools/ghidra/SyncSymbols.java (Thumb mode, functions, labels, names). Names typed in
Ghidra are kept unless symbols.txt has a real name there; they are not evidence.

The Ghidra install (12.2), its Java (JDK 21 or newer) and the project folder (outside
this repository) come from --ghidra, --java and --project, or from the
GHIDRA_INSTALL_DIR, GHIDRA_JAVA_HOME and DQMJ3_GHIDRA_PROJECT environment variables.

Usage:
  python tools/ghidra_sync.py                # import if needed, then sync
  python tools/ghidra_sync.py --analyze      # also run Ghidra's auto-analysis (slow)
  python tools/ghidra_sync.py --dry-run      # report what would change
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROGRAM = "code.elf"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", default="jpn")
    parser.add_argument("--ghidra", default=os.environ.get("GHIDRA_INSTALL_DIR"), help="Ghidra install dir")
    parser.add_argument("--java", default=os.environ.get("GHIDRA_JAVA_HOME"), help="JDK for Ghidra")
    parser.add_argument("--project", default=os.environ.get("DQMJ3_GHIDRA_PROJECT"), help="Ghidra project dir")
    parser.add_argument("--analyze", action="store_true", help="run auto-analysis after the sync")
    parser.add_argument("--dry-run", action="store_true", help="change nothing")
    args = parser.parse_args()
    if not args.ghidra or not args.project:
        parser.error("set --ghidra and --project, or GHIDRA_INSTALL_DIR and DQMJ3_GHIDRA_PROJECT")

    name = f"dqmj3_{args.version}"
    project = Path(args.project)
    symbols = ROOT / "config" / args.version / "symbols.txt"
    elf = ROOT / "build" / args.version / PROGRAM
    if not elf.is_file():
        subprocess.run([sys.executable, str(ROOT / "tools" / "ghidra_elf.py"), "--version", args.version],
                       check=True)

    headless = Path(args.ghidra) / "support" / ("analyzeHeadless.bat" if os.name == "nt" else "analyzeHeadless")
    exists = (project / f"{name}.gpr").is_file()
    if exists:
        cmd = [str(headless), str(project), name, "-process", PROGRAM]
    elif args.dry_run:
        sys.exit(f"no project {project / name}: nothing to compare with (run without --dry-run)")
    else:
        project.mkdir(parents=True, exist_ok=True)
        cmd = [str(headless), str(project), name, "-import", str(elf),
               "-processor", "ARM:LE:32:v6", "-cspec", "default", "-loader", "ElfLoader"]
    # The sync runs before analysis, so that analysis starts from the right Thumb mode
    # and function starts
    cmd += ["-scriptPath", str(ROOT / "tools" / "ghidra"), "-preScript", "SyncSymbols.java", str(symbols)]
    if args.dry_run:
        cmd += ["dry"]
    if not args.analyze or args.dry_run:
        cmd.append("-noanalysis")

    env = dict(os.environ)
    if args.java:
        env["JAVA_HOME"] = args.java
        env["PATH"] = str(Path(args.java) / "bin") + os.pathsep + env.get("PATH", "")
    out = subprocess.run(cmd, capture_output=True, text=True, env=env)
    lines = [line.strip() for line in (out.stdout + out.stderr).splitlines()]
    for line in lines:
        if "SyncSymbols" in line or line.startswith(("ERROR", "INFO  REPORT")):
            print(line)
    errors = [line for line in lines if line.startswith("ERROR")]
    if out.returncode != 0 and not errors:
        print("\n".join(lines[-20:]))
    return 0 if out.returncode == 0 and not errors else 1


if __name__ == "__main__":
    sys.exit(main())
