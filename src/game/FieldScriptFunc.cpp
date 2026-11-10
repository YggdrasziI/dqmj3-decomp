// FieldScriptFunc.cpp: Squirrel bindings used by the field scripts.
//
// The file name is the one the error paths pass to the error formatter
// ("FieldScriptFunc.cpp" in the literal pools of 186 functions in
// 0x00251FE8-0x0025D0A0). Its directory is unknown.
//
// Ranges claimed so far (see splits.txt):
//   .text   0x002546FC-0x00254784  SetFogDensity_
//   .rodata 0x00725800-0x0072580F  its __FUNCTION__ string
//
// SetFogDensity_ is named after its __FUNCTION__ string, which the error path
// passes to the formatter. The __FUNCTION__ strings of the bindings are packed
// one after the other in .rodata ("SetFogDensity_", "SetFogDistMax_", ...).

#include "game/squirrel_api.h"

extern "C" {
// Stubbed out in this build: returns "" (0x001446A0, 12 bytes).
const char* fn_001446A0(const char* msg, const char* file, const char* func, int line);
void fn_001DDDE8(void* self, float value);
extern void* lbl_007E7808;
}

// The original passes the bare file name, not the compiler's __FILE__.
#define SCRIPT_ERROR(v, msg) \
    sq_throwerror((v), fn_001446A0((msg), "FieldScriptFunc.cpp", __FUNCTION__, __LINE__))

SQInteger SetFogDensity_(HSQUIRRELVM v) {
    SQFloat value;
    if (SQ_FAILED(sq_getfloat(v, -1, &value))) {
#line 2832
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    fn_001DDDE8(lbl_007E7808, value);
    return 0;
}
