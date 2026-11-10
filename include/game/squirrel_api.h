#ifndef GAME_SQUIRREL_API_H
#define GAME_SQUIRREL_API_H

// Squirrel 2.2.5 ("Squirrel 2.2.5 stable" at 0x00155C40) types and the API
// functions used by the game's bindings. The API functions below compile from the
// Squirrel 2.2.5 sources to the bytes at their address (notes/COMPILER.md).

typedef int SQInteger;
typedef int SQRESULT;
typedef float SQFloat;
typedef struct SQVM* HSQUIRRELVM;

#define SQ_FAILED(res) ((res) < 0)

extern "C" {
SQRESULT sq_getfloat(HSQUIRRELVM v, SQInteger idx, SQFloat* f);
SQRESULT sq_throwerror(HSQUIRRELVM v, const char* err);
}

#endif
