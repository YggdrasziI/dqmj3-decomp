"""
Build generation.

Turns the project description in configure.py into build.ninja and objdiff.json.

The build has four stages:

  compile   armcc compiles every source file listed in configure.py
  split     tools/ctr/split.py cuts the original image into one object per unit for
            objdiff to compare against
  link      tools/ctr/link.py lays the objects of all matching units over the
            original image, which is then verified against the expected SHA-1
  report    objdiff-cli measures how much of the game is decompiled
"""

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ninja_syntax
from ctr.image import VersionConfig
from ctr.symbols import Splits, SymbolTable, Unit
from ctr.units import object_name, resolve_units

Matching = True
NonMatching = False
PRELINK_BATCH_SIZE = 64


class Object:
    def __init__(self, completed: bool, name: str, **options: Any) -> None:
        """
        `name` is the path of the source file relative to the library's source
        directory. It must have an entry of the same name in splits.txt.

        Options:
            cflags          replaces the library's compiler flags
            extra_cflags    appended to the compiler flags
            armcc_version   replaces the library's compiler version
            symbol_mappings reproducible objdiff target-to-source symbol mappings
        """
        self.name = name
        self.completed = completed
        self.options = options


class ProgressCategory:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name


class ProjectConfig:
    def __init__(self) -> None:
        # Paths
        self.build_dir = Path("build")
        self.src_dir = Path("src")
        self.tools_dir = Path("tools")
        self.config_dir = Path("config")

        # Version
        self.version: str = ""

        # Tooling
        self.armcc_version: str = ""
        self.compilers_path: Optional[Path] = None  # directory holding <version>/bin/armcc.exe
        self.wrapper: Optional[Path] = None  # wibo or wine
        self.wibo_tag: Optional[str] = None
        self.objdiff_path: Optional[Path] = None
        self.objdiff_tag: Optional[str] = None

        # Flags
        self.cflags: List[str] = []
        self.scratch_compilers: Dict[str, str] = {}  # armcc version -> decomp.me compiler id

        # Objects
        self.libs: List[Dict[str, Any]] = []
        self.progress_categories: List[ProgressCategory] = []
        # Title of the progress image (assets/progress.svg). None disables the image.
        self.progress_image_title: Optional[str] = None

        # Behaviour
        self.non_matching = False  # also link units that are not marked as matching
        self.progress = True  # print progress after a build
        self.configure_args: List[str] = []

    @property
    def out_dir(self) -> Path:
        return self.build_dir / self.version

    @property
    def version_config_path(self) -> Path:
        return self.config_dir / self.version / "config.toml"


def is_windows() -> bool:
    return os.name == "nt"


EXE = ".exe" if is_windows() else ""


def unix(path: Any) -> str:
    return str(path).replace(os.sep, "/")


class ResolvedObject:
    def __init__(self, config: ProjectConfig, lib: Dict[str, Any], obj: Object) -> None:
        self.name = obj.name
        self.completed = obj.completed
        self.lib = lib["lib"]
        self.src_path = Path(lib.get("src_dir", config.src_dir)) / obj.name
        self.armcc_version = obj.options.get(
            "armcc_version", lib.get("armcc_version", config.armcc_version)
        )
        cflags = obj.options.get("cflags", lib.get("cflags", config.cflags))
        self.cflags: List[str] = list(cflags) + list(obj.options.get("extra_cflags", []))
        self.progress_category = lib.get("progress_category")
        self.symbol_mappings: Dict[str, str] = dict(obj.options.get("symbol_mappings", {}))
        stem = Path(obj.name).with_suffix(".o")
        self.obj_path = config.out_dir / "src" / stem
        self.diff_path = config.out_dir / "diff" / stem
        self.unit: Optional[Unit] = None


def resolve_objects(config: ProjectConfig, splits: Splits) -> Dict[str, ResolvedObject]:
    objects: Dict[str, ResolvedObject] = {}
    for lib in config.libs:
        for obj in lib["objects"]:
            if obj.name in objects:
                sys.exit(f"configure.py: {obj.name} is listed more than once")
            resolved = ResolvedObject(config, lib, obj)
            resolved.unit = splits.unit(obj.name)
            if resolved.unit is None:
                sys.exit(
                    f"configure.py: {obj.name} has no entry in {config.config_dir / config.version / 'splits.txt'}"
                )
            if not resolved.src_path.is_file():
                sys.exit(f"configure.py: configured source {resolved.src_path} does not exist")
            objects[obj.name] = resolved
    for unit in splits.units:
        if unit.name not in objects:
            print(f"warning: {unit.name} is in splits.txt but has no source configured")
    return objects


def find_tool(name: str) -> Optional[Path]:
    found = shutil.which(name)
    return Path(found) if found else None


def generate_build(config: ProjectConfig) -> None:
    version = VersionConfig(config.version_config_path)
    try:
        symbols = SymbolTable.load(version.symbols_path)
        splits = Splits.load(version.splits_path)
        units = resolve_units(version, splits, symbols)
    except ValueError as e:
        sys.exit(f"error: {e}")
    objects = resolve_objects(config, splits)

    generate_build_ninja(config, version, units, objects)
    generate_objdiff_config(config, units, objects)
    generate_compile_commands(config, objects)


def generate_build_ninja(
    config: ProjectConfig,
    version: VersionConfig,
    units: List[Unit],
    objects: Dict[str, ResolvedObject],
) -> None:
    out_dir = config.out_dir
    tools_out = config.build_dir / "tools"
    ctr = config.tools_dir / "ctr"
    python = unix(sys.executable)

    with open("build.ninja", "w", encoding="utf-8", newline="\n") as f:
        n = ninja_syntax.Writer(f)
        n.comment("Generated by configure.py. Do not edit.")
        n.variable("ninja_required_version", "1.7")
        n.variable("builddir", unix(config.build_dir))
        n.variable("python", f'"{python}"')
        n.newline()

        ###
        # Tooling
        ###
        n.comment("Tooling")
        n.rule(
            "download_tool",
            command=f"$python {unix(config.tools_dir / 'download_tool.py')} $tool $out --tag $tag",
            description="TOOL $out",
        )
        download_script = unix(config.tools_dir / "download_tool.py")

        # Wrapper to run armcc with (it is a Windows executable)
        wrapper: Optional[Path] = config.wrapper
        wrapper_implicit: Optional[str] = None
        if not is_windows() and wrapper is None:
            wrapper = find_tool("wibo")
            if wrapper is None:
                wrapper = tools_out / "wibo"
                wrapper_implicit = unix(wrapper)
                n.build(
                    unix(wrapper),
                    "download_tool",
                    implicit=download_script,
                    variables={"tool": "wibo", "tag": config.wibo_tag},
                )
        wrapper_cmd = f"{unix(wrapper)} " if wrapper else ""

        # Compilers
        compilers = config.compilers_path or config.build_dir / "compilers"
        armcc: Dict[str, str] = {}
        for ver in sorted({o.armcc_version for o in objects.values()} | {config.armcc_version}):
            exe = compilers / ver / "bin" / "armcc.exe"
            armcc[ver] = unix(exe)
            if config.compilers_path is None:
                n.build(
                    unix(exe),
                    "download_tool",
                    implicit=download_script,
                    variables={"tool": "armcc", "tag": ver},
                )

        # objdiff
        objdiff: Optional[Path] = config.objdiff_path or find_tool("objdiff-cli")
        objdiff_implicit: Optional[str] = None
        if objdiff is None:
            objdiff = tools_out / f"objdiff-cli{EXE}"
            objdiff_implicit = unix(objdiff)
            n.build(
                unix(objdiff),
                "download_tool",
                implicit=download_script,
                variables={"tool": "objdiff", "tag": config.objdiff_tag},
            )
        n.newline()

        ###
        # Rules
        ###
        n.comment("Compile")
        n.rule(
            "armcc",
            command=(
                f"{wrapper_cmd}$armcc $cflags -c $in -o $out "
                "--depend=$out.d --depend_format=unix_escaped --no_depend_system_headers"
            ),
            description="CC $out",
            depfile="$out.d",
            deps="gcc",
        )
        n.newline()

        ctr_sources = sorted(unix(p) for p in ctr.glob("*.py"))
        config_inputs = [
            unix(version.path),
            unix(version.symbols_path),
            unix(version.splits_path),
            unix(version.object),
        ]

        n.comment("Apply the changes armlink made to calls, for comparison in objdiff")
        n.rule(
            "prelink",
            command=f"$python {unix(ctr / 'prelink.py')} {unix(version.path)} --unit $unit --unit-splits $unit_splits $in -o $out",
            description="PRELINK $out",
        )
        n.rule(
            "prelink_batch",
            command=f"$python {unix(ctr / 'prelink.py')} {unix(version.path)} --batch-manifest $manifest",
            description="PRELINK_BATCH $shard",
        )
        n.newline()

        n.comment("Split the original image into objects")
        n.rule(
            "split",
            command=f"$python {unix(ctr / 'split.py')} {unix(version.path)} -o $outdir --stamp $out",
            description="SPLIT $object",
            restat=True,
        )
        n.newline()

        n.comment("Link")
        n.rule(
            "link",
            command=f"$python {unix(ctr / 'link.py')} {unix(version.path)} -o $out --map $map @$out.rsp",
            description="LINK $out",
            rspfile="$out.rsp",
            rspfile_content="$units",
        )
        n.rule(
            "check",
            command=f"$python {unix(ctr / 'check.py')} {unix(version.path)} $in --stamp $out",
            description="CHECK $in",
        )
        n.newline()

        n.comment("Progress")
        n.rule(
            "report",
            # ninja runs commands without a shell on Windows: chain them through cmd.
            # The report ignores relocation targets by default (functionRelocDiffs=none):
            # a call to another function would still count as a match.
            command=(lambda c: f'cmd /s /c "{c}"' if is_windows() else c)(
                f'"{objdiff}" report generate -c functionRelocDiffs=name_address -o $out && '
                f"$python {unix(ctr / 'report_accounting.py')} {unix(version.path)} $out --standard-output $standard"),
            description="REPORT",
        )
        n.rule(
            "progress",
            command=f"$python configure.py {' '.join(config.configure_args)} progress",
            description="PROGRESS",
        )
        n.newline()

        ###
        # Build edges
        ###
        n.comment("Sources")
        link_units: List[Tuple[str, str]] = []
        diff_objects: List[str] = []
        unit_descriptors: List[str] = []
        prelink_jobs: List[dict] = []
        for obj in objects.values():
            include_dirs = [f"-J{unix(Path(armcc[obj.armcc_version]).parent.parent / 'include')}"]
            implicit = [armcc[obj.armcc_version]]
            if wrapper_implicit:
                implicit.append(wrapper_implicit)
            n.build(
                unix(obj.obj_path),
                "armcc",
                unix(obj.src_path),
                implicit=implicit,
                variables={
                    # CreateProcess does not search a relative path written with '/'
                    "armcc": str(Path(armcc[obj.armcc_version])) if is_windows() else armcc[obj.armcc_version],
                    "cflags": " ".join(obj.cflags + include_dirs),
                },
            )
            # Prelink only reads the selected unit's ranges. Keep that input
            # stable when another unit is added; the full link/split still
            # depends on the complete split table.
            descriptor = out_dir / "prelink_units" / (obj.name + ".txt")
            content = obj.name + ":\n" + "".join(
                f"\t{r.section} start:0x{r.start:08X} end:0x{r.end:08X}\n"
                for r in obj.unit.ranges
            )
            descriptor.parent.mkdir(parents=True, exist_ok=True)
            if not descriptor.exists() or descriptor.read_text() != content:
                descriptor.write_text(content)
            unit_descriptors.append(unix(descriptor))
            prelink_jobs.append({
                "unit": obj.name,
                "input": unix(obj.obj_path),
                "unit_splits": unix(descriptor),
                "output": unix(obj.diff_path),
            })
            diff_objects.append(unix(obj.diff_path))
            if obj.completed or config.non_matching:
                link_units.append((obj.name, unix(obj.obj_path)))

        # Bounded stable shards load Image/SymbolTable once while retaining every
        # per-object input, unit descriptor, global input, and output path.
        prelink_jobs.sort(key=lambda job: job["unit"])
        prelink_implicit = [p for p in config_inputs if p != unix(version.splits_path)]
        for shard_index, start in enumerate(range(0, len(prelink_jobs), PRELINK_BATCH_SIZE)):
            jobs = prelink_jobs[start : start + PRELINK_BATCH_SIZE]
            shard_name = f"shard-{shard_index:04d}"
            manifest = out_dir / "prelink_shards" / f"{shard_name}.json"
            stamp = out_dir / "prelink_shards" / f"{shard_name}.stamp"
            batch = {"jobs": jobs, "stamp": unix(stamp)}
            batch_content = json.dumps(batch, indent=2) + "\n"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            if not manifest.exists() or manifest.read_text(encoding="utf-8") != batch_content:
                manifest.write_text(batch_content, encoding="utf-8", newline="\n")
            inputs = [job["input"] for job in jobs]
            outputs = [job["output"] for job in jobs] + [unix(stamp)]
            implicit = ctr_sources + prelink_implicit + [unix(manifest)]
            implicit.extend(job["unit_splits"] for job in jobs)
            n.build(
                outputs,
                "prelink_batch",
                inputs,
                implicit=implicit,
                variables={"manifest": unix(manifest), "shard": shard_name},
            )
        diff_objects.sort()
        # Compile every configured source for comparison, including unfinished
        # units that the normal matching executable still takes from retail.
        n.build("all_source", "phony", diff_objects)
        n.newline()

        n.comment("Original image")
        delink_dir = out_dir / "delink"
        split_stamp = out_dir / "split.stamp"
        delink_objects = [unix(delink_dir / object_name(u)) for u in units]
        n.build(
            unix(split_stamp),
            "split",
            implicit=ctr_sources + config_inputs,
            implicit_outputs=delink_objects,
            variables={"outdir": unix(delink_dir), "object": unix(version.object)},
        )
        n.newline()

        n.comment("Image")
        binary = out_dir / "code.bin"
        n.build(
            unix(binary),
            "link",
            [path for _, path in link_units],
            implicit=ctr_sources + config_inputs,
            implicit_outputs=unix(out_dir / "code.map"),
            variables={
                "map": unix(out_dir / "code.map"),
                "units": " ".join(f"{name}={path}" for name, path in link_units),
            },
        )
        ok = out_dir / "ok"
        n.build(unix(ok), "check", unix(binary), implicit=ctr_sources)
        n.newline()

        n.comment("Progress report")
        report = out_dir / "report.json"
        report_implicit = delink_objects + ["all_source", "objdiff.json", unix(ctr / "report_accounting.py")]
        if objdiff_implicit:
            report_implicit.append(objdiff_implicit)
        standard_report = out_dir / "tracker" / "report.json"
        n.build(unix(report), "report", implicit=report_implicit,
                implicit_outputs=unix(standard_report),
                variables={"standard": unix(standard_report)})
        progress_implicit = [unix(report), unix(ok)]
        if config.progress_image_title:
            # Checked in, so that the README can show it
            image_script = unix(config.tools_dir / "progress_image.py")
            images = ["assets/progress.svg", "assets/progress_dark.svg"]
            n.rule(
                "progress_image",
                command=(
                    f"$python {image_script} $in -o {images[0]} --dark {images[1]} "
                    f'--title "{config.progress_image_title}"'
                ),
                description="IMAGE $out",
                restat=True,
            )
            n.build(images, "progress_image", unix(standard_report), implicit=image_script)
            progress_implicit += images
        n.build("progress", "progress", implicit=progress_implicit)
        n.newline()

        n.comment("Regenerate the build when the project configuration changes")
        n.rule(
            "configure",
            command=f"$python configure.py {' '.join(config.configure_args)}",
            description="CONFIGURE",
            generator=True,
            restat=True,
        )
        n.build(
            "build.ninja",
            "configure",
            implicit=[
                "configure.py",
                unix(config.tools_dir / "project.py"),
                unix(config.tools_dir / "ninja_syntax.py"),
                unix(ctr / "units.py"),
                unix(ctr / "symbols.py"),
                unix(ctr / "image.py"),
                unix(version.path),
                unix(version.symbols_path),
                unix(version.splits_path),
            ],
            implicit_outputs=["objdiff.json", "compile_commands.json"] + unit_descriptors,
        )
        n.newline()

        n.build("split", "phony", unix(split_stamp))
        n.build("check", "phony", unix(ok))
        n.build("report", "phony", unix(report))
        if config.non_matching:
            # The image is not expected to match, so do not verify it
            n.default([unix(binary), unix(report)])
        elif config.progress:
            n.default("progress")
        else:
            n.default([unix(ok), unix(report)] + progress_implicit[2:])


def scratch_flags(cflags: List[str]) -> str:
    """Compiler flags for a decomp.me scratch: everything but include paths."""
    return " ".join(f for f in cflags if not f.startswith(("-I", "-J")))


def generate_objdiff_config(
    config: ProjectConfig, units: List[Unit], objects: Dict[str, ResolvedObject]
) -> None:
    # Symbol mappings are edited through objdiff, so they are carried over
    existing: Dict[str, Any] = {}
    if Path("objdiff.json").is_file():
        try:
            with open("objdiff.json", "r", encoding="utf-8") as f:
                existing = {u["name"]: u for u in json.load(f).get("units", [])}
        except (ValueError, KeyError):
            existing = {}

    objdiff_config: Dict[str, Any] = {
        "$schema": "https://raw.githubusercontent.com/encounter/objdiff/main/config.schema.json",
        "min_version": "3.0.0",
        "custom_make": "ninja",
        "build_target": False,
        "build_base": True,
        "watch_patterns": [
            "*.c",
            "*.cpp",
            "*.h",
            "*.hpp",
            "*.inc",
            "*.py",
            "*.toml",
            "*.txt",
        ],
        "units": [],
        "progress_categories": [
            {"id": c.id, "name": c.name} for c in config.progress_categories
        ],
    }

    delink_dir = config.out_dir / "delink"
    for unit in units:
        name = str(Path(unit.name).with_suffix("")) if not unit.auto else unit.name
        entry: Dict[str, Any] = {
            "name": unix(name),
            "target_path": unix(delink_dir / object_name(unit)),
            "metadata": {"auto_generated": unit.auto},
        }
        if unit.category:
            entry["metadata"]["progress_categories"] = [unit.category]
        obj = objects.get(unit.name)
        if obj is not None:
            entry["base_path"] = unix(obj.diff_path)
            entry["metadata"]["complete"] = obj.completed
            entry["metadata"]["source_path"] = unix(obj.src_path)
            if obj.progress_category:
                entry["metadata"]["progress_categories"] = [obj.progress_category]
            compiler = config.scratch_compilers.get(obj.armcc_version)
            if compiler:
                entry["scratch"] = {
                    "platform": "n3ds",
                    "compiler": compiler,
                    "c_flags": scratch_flags(obj.cflags),
                }
        previous = existing.get(entry["name"])
        if previous and previous.get("symbol_mappings"):
            entry["symbol_mappings"] = previous["symbol_mappings"]
        if obj is not None and obj.symbol_mappings:
            entry["symbol_mappings"] = {
                **entry.get("symbol_mappings", {}), **obj.symbol_mappings
            }
        objdiff_config["units"].append(entry)

    with open("objdiff.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(objdiff_config, f, indent=2)
        f.write("\n")


def generate_compile_commands(config: ProjectConfig, objects: Dict[str, ResolvedObject]) -> None:
    """A compilation database for clangd, with armcc's flags translated as far as possible."""
    commands = []
    for obj in objects.values():
        args = [
            "clang++",
            "--target=armv6k-none-eabi",
            "-mfloat-abi=hard",
            "-mfpu=vfpv2",
            "-std=gnu++03",
            "-fno-exceptions",
            "-fno-rtti",
            "-fsigned-char",
            "-fshort-wchar",
            "-nostdinc",
            "-Wno-everything",
        ]
        for flag in obj.cflags:
            if flag.startswith(("-I", "-D")):
                args.append(flag)
        args += ["-c", unix(obj.src_path)]
        commands.append(
            {
                "directory": unix(Path.cwd()),
                "file": unix(obj.src_path),
                "arguments": args,
            }
        )
    with open("compile_commands.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(commands, f, indent=2)
        f.write("\n")


###
# Progress
###


def calculate_progress(config: ProjectConfig) -> None:
    report_path = config.out_dir / "tracker" / "report.json"
    if not report_path.is_file():
        sys.exit(f"{report_path} does not exist. Run ninja first.")
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    def number(value: Any) -> float:
        return float(value) if value is not None else 0.0

    def print_measures(name: str, measures: Dict[str, Any]) -> None:
        total_code = number(measures.get("total_code"))
        matched_code = number(measures.get("matched_code"))
        total_data = number(measures.get("total_data"))
        matched_data = number(measures.get("matched_data"))
        total_functions = int(number(measures.get("total_functions")))
        matched_functions = int(number(measures.get("matched_functions")))
        code_percent = matched_code / total_code * 100 if total_code else 0.0
        data_percent = matched_data / total_data * 100 if total_data else 0.0
        print(f"{name}:")
        print(
            f"  Code: {int(matched_code)} / {int(total_code)} bytes ({code_percent:.4f}%), "
            f"{matched_functions} / {total_functions} functions"
        )
        print(f"  Data: {int(matched_data)} / {int(total_data)} bytes ({data_percent:.4f}%)")

    print_measures("Progress (decomp.dev / standard objdiff)", report.get("measures", {}))
    fuzzy = number(report.get("measures", {}).get("fuzzy_match_percent"))
    print(f"  Fuzzy similarity: {fuzzy:.4f}%")
    complete = number(report.get("measures", {}).get("complete_code_percent"))
    print(f"  Completed/linked code: {complete:.4f}%")
    for category in report.get("categories", []):
        print_measures(category.get("name", category.get("id")), category.get("measures", {}))
    unfinished = [unit for unit in report.get("units", [])
                  if unit.get("metadata", {}).get("source_path")
                  and unit.get("metadata", {}).get("complete") is False]
    if unfinished:
        print("Unfinished source comparisons:")
        for unit in unfinished:
            measures = unit.get("measures", {})
            exact = number(measures.get("matched_code_percent"))
            fuzzy = number(measures.get("fuzzy_match_percent"))
            print(f"  {unit['metadata']['source_path']}: "
                  f"exact code {exact:.4f}%, fuzzy {fuzzy:.4f}%")
