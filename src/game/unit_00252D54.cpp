// unit_00252D54.cpp: one Squirrel binding, 0x00252D54-0x00252D70 (.text).
//
// The real file is unknown. The function has no error path, so it passes no
// file name and no __FUNCTION__ string; it sits between FieldScriptFunc.cpp
// bindings, but that .text run is sorted by name, so the address does not tie it
// to that file. This one-function unit is a hypothesis.
//
// Name: fn_001DAB80 registers it with the Squirrel VM under "RecoverAll_" (the
// name follows the pool entry at 0x001DD024). For the 183 bindings of that
// function that were already named from their __FUNCTION__ strings, the
// registered name equals the function name in every case.

#include "game/script_bindings.h"

extern "C" {
void fn_001DA504(void* self);
}

SQInteger RecoverAll_(HSQUIRRELVM v) {
    void* self = lbl_007E7808;
    fn_001DA504(self);
    return 0;
}
