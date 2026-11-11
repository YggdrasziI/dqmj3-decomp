#ifndef GAME_SCRIPT_BINDINGS_H
#define GAME_SCRIPT_BINDINGS_H

// Shared by the Squirrel binding files (FieldScriptFunc.cpp, BattleScriptFunc.cpp).
// Each file defines SCRIPT_FILE, the bare file name its error paths pass.

#include "game/squirrel_api.h"

// A vector of three floats: fn_001446AC reads it from a script table with the
// keys "x", "y" and "z" (0x001447AC), fn_001447BC pushes one back.
struct UnkVec3 {
    float x;
    float y;
    float z;
};

extern "C" {
// Stubbed out in this build: returns "" (0x001446A0, 12 bytes).
const char* fn_001446A0(const char* msg, const char* file, const char* func, int line);
SQRESULT fn_001446AC(UnkVec3* out, HSQUIRRELVM v, SQInteger idx);
SQRESULT fn_001447BC(HSQUIRRELVM v, const UnkVec3* vec);
// The object most bindings call.
extern void* lbl_007E7808;
}

// The original passes the bare file name, not the compiler's __FILE__.
#define SCRIPT_ERROR(v, msg) \
    sq_throwerror((v), fn_001446A0((msg), SCRIPT_FILE, __FUNCTION__, __LINE__))

#endif
