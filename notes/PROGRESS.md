# Progress

Milestones, newest last. Figures come from `build/jpn/tracker/report.json`.

| Date | Milestone | Code linked | Functions matched |
|---|---|---|---|
| 2026-11-10 | Step 1: build from the original image, `build\jpn\code.bin: OK`; 118 automatic units, objdiff report (6,310,790 bytes of code, 34,058 functions) | 0 % | 0 / 34058 |
| 2026-11-10 | Step 2: compiler identified (RVCT 4.1 b921, `-O3 -Otime`); first game unit linked from source, `SetFogDensity_` (`FieldScriptFunc.cpp`, 136 bytes of code, 15 of data) | 0.002 % | 1 / 34058 |
| 2026-11-10 | Squirrel 2.2.5: 224 functions named and matched in objdiff (11 `NonMatching` units from the public source, 87,932 bytes) | 0.002 % | 225 / 34057 |
| 2026-11-10 | Report compares relocation targets (`functionRelocDiffs=name_address`); 58 more symbols named from matched functions; Squirrel 217 functions matched, the 7 others refer to unclaimed long strings | 0.002 % | 218 / 34057 |
| 2026-11-11 | zlib: the two copies of the image matched from the public sources, CTR-SDK 1.2.7 (32 functions, 4.1 b1049, `--cpu=MPCoreNoVFP`) and 1.2.5 (30 functions, b1049, `--cpu=MPCore`, analysis names); Squirrel 186 of 187 functions of its 6 `NonMatching` files | 0.54 % | 353 / 34059 |
