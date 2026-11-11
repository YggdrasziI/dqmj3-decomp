# Progress

Milestones, newest last. Figures come from `build/jpn/tracker/report.json`.

| Date | Milestone | Code linked | Functions matched |
|---|---|---|---|
| 2026-11-10 | Step 1: build from the original image, `build\jpn\code.bin: OK`; 118 automatic units, objdiff report (6,310,790 bytes of code, 34,058 functions) | 0 % | 0 / 34058 |
| 2026-11-10 | Step 2: compiler identified (RVCT 4.1 b921, `-O3 -Otime`); first game unit linked from source, `SetFogDensity_` (`FieldScriptFunc.cpp`, 136 bytes of code, 15 of data) | 0.002 % | 1 / 34058 |
| 2026-11-10 | Squirrel 2.2.5: 224 functions named and matched in objdiff (11 `NonMatching` units from the public source, 87,932 bytes) | 0.002 % | 225 / 34057 |
| 2026-11-10 | Report compares relocation targets (`functionRelocDiffs=name_address`); 58 more symbols named from matched functions; Squirrel 217 functions matched, the 7 others refer to unclaimed long strings | 0.002 % | 218 / 34057 |
| 2026-11-11 | zlib: the two copies of the image matched from the public sources, CTR-SDK 1.2.7 (32 functions, 4.1 b1049, `--cpu=MPCoreNoVFP`) and 1.2.5 (30 functions, b1049, `--cpu=MPCore`, analysis names); Squirrel 186 of 187 functions of its 6 `NonMatching` files | 0.54 % | 353 / 34059 |
| 2026-11-11 | Step 4: region map (`[[regions]]`: two C-library blocks with all 332 Thumb functions, the network block; the rest is name-sorted runs attributed per unit); 89 function bounds fixed (inline UTF-16 strings), 34,021 functions in the report | 0.54 % | 353 / 34021 |
| 2026-11-11 | Step 4: function bounds outside the C library all fixed (`vldr` pools, 12 functions with a mid-function pool, 11 strings that had been taken for functions); 20 functions with unclean control flow left, all in the C library; 33,967 functions in the report | 0.54 % | 353 / 33967 |
| 2026-11-11 | Game code: the 186 bindings of `FieldScriptFunc.cpp` (named from their `__FUNCTION__` strings), 181 at 100 %; matched code 2.82 % -> 3.43 %, the unit `NonMatching` until the last 5 match | 0.54 % | 533 / 33967 |
| 2026-11-11 | Game code: the 138 bindings of `BattleScriptFunc.cpp`, 114 of its 140 functions at 100 %; both binding files built with ARM Compiler 5.04 b82 (`FieldScriptFunc.cpp` 183 of 186); matched code 3.43 % -> 3.86 % | 0.54 % | 649 / 33967 |
