#ifndef GAME_SQUIRREL_API_H
#define GAME_SQUIRREL_API_H

// Squirrel 2.2.5 ("Squirrel 2.2.5 stable" at 0x00155C40) types and the API
// functions used by the game's bindings. The API functions below compile from the
// Squirrel 2.2.5 sources to the bytes at their address (notes/COMPILER.md).

typedef int SQInteger;
typedef int SQRESULT;
typedef float SQFloat;
typedef unsigned int SQBool;
typedef char SQChar;
typedef struct SQVM* HSQUIRRELVM;

#define SQ_FAILED(res) ((res) < 0)

extern "C" {
SQRESULT sq_getstring(HSQUIRRELVM v, SQInteger idx, const SQChar** c);
SQRESULT sq_getinteger(HSQUIRRELVM v, SQInteger idx, SQInteger* i);
SQRESULT sq_getfloat(HSQUIRRELVM v, SQInteger idx, SQFloat* f);
SQRESULT sq_getbool(HSQUIRRELVM v, SQInteger idx, SQBool* b);
SQRESULT sq_throwerror(HSQUIRRELVM v, const char* err);
SQRESULT sq_get(HSQUIRRELVM v, SQInteger idx);
SQRESULT sq_suspendvm(HSQUIRRELVM v);
void sq_pop(HSQUIRRELVM v, SQInteger nelemstopop);
void sq_pushstring(HSQUIRRELVM v, const SQChar* s, SQInteger len);
void sq_pushfloat(HSQUIRRELVM v, SQFloat f);
void sq_pushinteger(HSQUIRRELVM v, SQInteger n);
void sq_pushbool(HSQUIRRELVM v, SQBool b);
}

#endif
