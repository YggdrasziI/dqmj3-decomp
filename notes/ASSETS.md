# Game files (RomFS)

Formats of the files in the RomFS, for understanding the code. No game file, extracted
or converted, is ever committed.

Not analysed yet (roadmap step 7). The RomFS is 0x353C2000 bytes (`ctrtool`); extract it
with `ctrtool -n 0 --romfsdir=extract/jpn/romfs <dump>.3ds`.

Names seen in `code.bin`, as leads: NintendoWare layout images (`.bflim`) and fonts
(`.bffnt`, e.g. `break_font.bffnt`), table files such as `029W_EvaluationPoint.bin`.
