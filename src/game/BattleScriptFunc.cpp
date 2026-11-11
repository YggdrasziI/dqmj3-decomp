// BattleScriptFunc.cpp: Squirrel bindings used by the battle scripts.
//
// The file name is the one the error paths pass to the error formatter
// ("BattleScriptFunc.cpp"). Its directory is unknown.
//
// Each binding is named after its __FUNCTION__ string, which its error path
// passes to the formatter. armcc puts the __FUNCTION__ strings of a file in one
// .constdata section, in source order: the 143 names at 0x00720260-0x00720BBD
// give the order of the functions below. The bindings without an error path
// have no such string, and nothing ties them to this file yet.
//
// fn_00131FC8 and fn_00133E58, in this unit's ranges, are not written yet: they
// inline CreateTask_PathMoveCharInfo and free a vector of 12-byte elements
// (fn_001008C4).
//
// The object at lbl_007E7808 and its methods are not decompiled; they are
// declared with their analysis names and the argument types the calls show.

#include <stddef.h>
#include <string.h>

#define SCRIPT_FILE "BattleScriptFunc.cpp"
#include "game/script_bindings.h"

extern "C" {
void fn_001400E4(void* self, int a0, bool a1);
int fn_00144CCC(void* self, unsigned char, unsigned char);
void fn_00144DCC(void* self, unsigned char);
void fn_00144E4C(void* self, unsigned char, const char*);
void fn_00144FD8(void* self, unsigned char);
int fn_00145060(void* self, const char*, unsigned char);
void fn_001450C0(void* self, unsigned char, short);
int fn_001450F0(void* self, const char*, const char*);
int fn_00145258(void* self, unsigned char, float);
int fn_00145350(void* self, unsigned char, float);
void fn_001456D0(void* self, const char*);
int fn_001456F4(void* self, unsigned char, int, float);
int fn_00145790(void* self, const char*, const char*);
void fn_001457CC(void* self, int);
void fn_001458C8(void* self, const char*);
int fn_00145904(void* self, const char*, float);
int fn_00145AE0(void* self, const char* a0, float a1, const int* frm);
int fn_00145BC4(void* self, const char* a0, float a1, const int* frm);
void fn_00145CAC(void* self, unsigned char, const char*);
int fn_00145D78(void* self, const char*, const char*, int);
int fn_00145F50(void* self, const char* a0, unsigned char a1, const char* a2, const UnkVec3* pos);
void fn_00145FD8(void* self, unsigned char, const char*);
int fn_00146048(void* self, const char*, float);
void fn_00146228(void* self, unsigned char a0, UnkVec3 pos);
void fn_00146248(void* self, unsigned char, unsigned char, unsigned char, unsigned char);
bool fn_001507D0(void* self, int);
UnkVec3 fn_001508B4(void* self, unsigned char a0, const char* a1);
UnkVec3 fn_0015094C(void* self, unsigned char a0);
bool fn_00150A28(void* self, int, int, short);
bool fn_00150A54(void* self, int, int);
void fn_00150A7C(void* self, const char*);
void fn_00150AB8(void* self, unsigned char idx, bool a1);
void fn_00150B24(void* self, int);
bool fn_00150B8C(void* self, int, int);
bool fn_00150BB4(void* self, int, int);
bool fn_00150BDC(void* self, int);
void fn_00150C00(void* self, unsigned char, short);
void fn_00150C30(void* self, unsigned char, short);
void fn_00150C60(void* self, const char*);
int fn_00150C9C(void* self, int, int);
int fn_00150CB4(void* self, signed char);
int fn_00150CDC(void* self, unsigned char);
int fn_00150D3C(void* self, signed char);
int fn_00150D6C(void* self, int, int);
int fn_00150D88(void* self, int, int);
bool fn_00150DA0(void* self, int);
bool fn_00150DC4(void* self, int, int, short);
bool fn_00150DF0(void* self, int, int);
bool fn_00150E18(void* self, int, int);
bool fn_00150E40(void* self, int);
void fn_00150EDC(void* self, int);
int fn_00150F24(void* self, int, int);
int fn_00150F3C(void* self, signed char);
int fn_00150F70(void* self, bool a0);
bool fn_00150FAC(void* self, int, int, int);
int fn_00150FE4(void* self, int, int, short);
int fn_00151014(void* self, unsigned char);
bool fn_0015108C(void* self, int, int);
bool fn_001510E0(void* self, int);
void fn_00151190(void* self, unsigned char, short);
void fn_001511C0(void* self, unsigned char);
void fn_001511EC(void* self, unsigned char, float);
void fn_00151234(void* self, unsigned char, short);
void fn_00151264(void* self, int, int);
void fn_001512B4(void* self, int);
int fn_00151378(void* self, int, int);
bool fn_00151390(void* self, int, int);
bool fn_001513B8(void* self, int);
void fn_001513F8(void* self, signed char, signed char);
void fn_00151440(void* self, int, int, int);
const char* fn_00151484(void* self, signed char, int);
int fn_00151534(void* self, signed char);
bool fn_00151564(void* self, int, int, int);
int fn_0015159C(void* self, int);
int fn_00151704(void* self, signed char, int);
void fn_0015183C(void* self, int);
int fn_001518D8(void* self, int, int);
int fn_001518F0(void* self, int, int);
void fn_00151928(void* self, unsigned char, float);
int fn_00151990(void* self, int, int);
const char* fn_001519C4(void* self, signed char, int);
void fn_00151A70(void* self, unsigned char, int, int);
int fn_00151ACC(void* self, signed char, int);
void fn_00151B78(void* self, unsigned char, const char*);
void fn_00151BF4(void* self, unsigned char idx, bool a1);
void fn_00151C48(void* self, unsigned char);
void fn_00151C5C(void* self, int a0, int kind);
int fn_00151D58(void* self, int, signed char);
void fn_00151D90(void* self, unsigned char idx, const char* a1, bool a2);
void fn_00151E20(void* self, bool a0, int a1, int kind);
void fn_00151EA4(void* self, bool a0, int a1, int kind);
float fn_00151F30(void* self, unsigned char);
bool fn_00151F9C(void* self, int, int);
bool fn_00151FE0(void* self, int, int, short);
bool fn_0015200C(void* self, signed char);
void fn_00152088(void* self, unsigned char idx, int a1, int a2, bool a3, int a4, int a5, float a6);
bool fn_00152178(void* self, int, int);
bool fn_001521A0(void* self, int, int);
float fn_001521F0(void* self, unsigned char);
int fn_0015225C(void* self, int);
bool fn_0015230C(void* self, int, int);
bool fn_00152334(void* self, unsigned char);
bool fn_00152364(void* self, int);
bool fn_001523B8(void* self, int);
void fn_001524D8(void* self, unsigned char, short);
void fn_00152508(void* self, unsigned char, short);
const UnkVec3* fn_001525C8(void* self, const char* a0);
int fn_0015267C(void* self, unsigned char);
bool fn_001526B0(void* self, int);
bool fn_00152700(void* self, int, int);
bool fn_00152728(void* self, int, int);
void fn_00152750(void* self, unsigned char, int, int);
void fn_00155D64(void* self, const unsigned char& a0, const unsigned char& a1);
void fn_00156264(void* self, unsigned char);
void fn_0015639C(void* self, unsigned char);
void fn_001563CC(void* self, unsigned short, unsigned short);
int fn_00156F44(void* self, unsigned char, const char*);
int fn_00156F4C(void* self, unsigned char, const char*, int);
int fn_001570A0(void* self, unsigned char, const char*);
int fn_001570A8(void* self, unsigned char, const char*, int);
void fn_0015750C(void* self, int);
void fn_0015754C(void* self, bool);
int fn_0015E534(void* self, int);
int fn_0015E814(void* self, int);
void fn_0015E834(void* self, int, unsigned char);
int fn_0015EFD8(void* self, int);
int fn_0015F224(void* self, int, int, int);
const UnkVec3* fn_0015F298(void* self, const char* a0);
UnkVec3 fn_0015F608(void* self, unsigned char a0);
bool fn_0015F694(void* self, unsigned char);
int fn_0015FBB0(void* self, signed char);
int fn_0015FD20(void* self, signed char);
int fn_0015FE60(void* self, signed char a0, signed char a1);
void fn_001660F4(void* self, int);
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger SetPos_(HSQUIRRELVM v) {
    SQInteger a0;
    UnkVec3 pos;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 96
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    fn_001446AC(&pos, v, -1);
    void* self = lbl_007E7808;
    fn_00146228(self, a0, pos);
    return 0;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger GetPos_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 109
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    UnkVec3 pos = fn_0015F608(self, a0);
    fn_001447BC(v, &pos);
    return 1;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger GetDir_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 193
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushfloat(v, fn_00151F30(self, a0));
    return 1;
}

// 99.9 %: stack slots differ. The original puts a0 at sp+0x20 and a3 at
// sp+0x24, above the other locals; armcc puts a0 at the top here whatever
// the declaration order.
SQInteger SetPop_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    SQBool a3;
    SQInteger a4;
    SQInteger a5;
    SQFloat a6;
    if (SQ_FAILED(sq_getinteger(v, -7, &a0))) {
#line 357
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -6, &a1))) {
#line 360
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -5, &a2))) {
#line 363
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -4, &a3))) {
#line 366
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    if (SQ_FAILED(sq_getinteger(v, -3, &a4))) {
#line 369
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a5))) {
#line 372
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a6))) {
#line 375
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    signed char idx = a0;
    void* self = lbl_007E7808;
    fn_00152088(self, idx, a1, a2, a3 != 0, a4, a5, a6);
    return 0;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger IsAlly_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 695
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_0015F694(self, a0));
    return 1;
}

SQInteger IsMiss_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 1478
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 1481
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 1484
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00151FE0(self, a0, a1, a2));
    return 1;
}

SQInteger IsDead_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1262
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1265
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00151F9C(self, a0, a1));
    return 1;
}

SQInteger IsRide_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1504
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_0015200C(self, a0));
    return 1;
}

SQInteger SetPointCameraEye_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 34
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001456D0(self, a0);
    return 0;
}

SQInteger SetPointCameraTarget_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 44
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001458C8(self, a0);
    return 0;
}

SQInteger SetVisible_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 54
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 57
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    signed char idx = a0;
    void* self = lbl_007E7808;
    fn_00150AB8(self, idx, a1 == 1);
    return 0;
}

SQInteger SetMonsterMeshVisible_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    SQBool a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 67
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a1))) {
#line 70
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a2))) {
#line 73
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    signed char idx = a0;
    void* self = lbl_007E7808;
    fn_00151D90(self, idx, a1, a2 == 1);
    return 0;
}

SQInteger SetMonsterPlayMoveSE_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 83
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 86
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    signed char idx = a0;
    void* self = lbl_007E7808;
    fn_00151BF4(self, idx, a1 == 1);
    return 0;
}

SQInteger SetPointPos_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 121
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 124
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_00144E4C(self, a0, a1);
    return 0;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger GetPitch_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 216
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushfloat(v, fn_001521F0(self, a0));
    return 1;
}

SQInteger ReadMonsterAddMotion_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 227
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 230
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_00151B78(self, a0, a1);
    return 0;
}

SQInteger SetMotion_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 240
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 243
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 246
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00152750(self, a0, a1, a2);
    return 0;
}

SQInteger SetMasterRideMotion_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 256
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 259
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 262
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00151A70(self, a0, a1, a2);
    return 0;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger GetMotion_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 285
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0015267C(self, a0));
    return 1;
}

SQInteger SetMotionFrame_(HSQUIRRELVM v) {
    SQInteger a0;
    SQFloat a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 272
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a1))) {
#line 275
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_001511EC(self, a0, a1);
    return 0;
}

SQInteger SetMotionStepFrame_(HSQUIRRELVM v) {
    SQInteger a0;
    SQFloat a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 296
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a1))) {
#line 299
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_00151928(self, a0, a1);
    return 0;
}

SQInteger StartEarthQuake_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 393
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 396
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 399
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00151440(self, a0, a1, a2);
    return 0;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger GetMonsterSize_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 416
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00151014(self, a0));
    return 1;
}

SQInteger ChangeIndexPointData_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 494
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001457CC(self, a0);
    return 0;
}

SQInteger GetMonsterLinage_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 457
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00151534(self, a0));
    return 1;
}

SQInteger GetMasterKind_(HSQUIRRELVM v) {
    SQBool a0;
    if (SQ_FAILED(sq_getbool(v, -1, &a0))) {
#line 469
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00150F70(self, a0 == 1));
    return 1;
}

SQInteger SetPointWorldEffect_(HSQUIRRELVM v) {
    const SQChar* a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 309
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 312
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00145790(self, a0, a1));
    return 1;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger SetBoneEffect_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 323
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 326
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00145060(self, a0, a1));
    return 1;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger SetFreeSelectBoneEffect_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQInteger a1;
    const SQChar* a2;
    UnkVec3 pos;
    if (SQ_FAILED(sq_getstring(v, -4, &a0))) {
#line 337
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -3, &a1))) {
#line 340
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a2))) {
#line 343
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    fn_001446AC(&pos, v, -1);
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00145F50(self, a0, a1, a2, &pos));
    return 1;
}

SQInteger GetActionEfficacy_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 504
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0015E534(self, a0));
    return 1;
}

SQInteger GetActionCategory_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 515
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0015159C(self, a0));
    return 1;
}

SQInteger RideOffMaster_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 526
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00144FD8(self, a0);
    return 0;
}

SQInteger RideMaster_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 535
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00144DCC(self, a0);
    return 0;
}

SQInteger GetSingleEffectName_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 545
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 548
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushstring(v, fn_001519C4(self, a0, a1), -1);
    return 1;
}

SQInteger GetSingleEffectFrame_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 560
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 563
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00151ACC(self, a0, a1));
    return 1;
}

SQInteger GetAllEffectName_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 575
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 578
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushstring(v, fn_00151484(self, a0, a1), -1);
    return 1;
}

SQInteger GetAllEffectFrame_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 590
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 593
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00151704(self, a0, a1));
    return 1;
}

SQInteger SetSceneOffsetFromMove_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 621
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 624
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_00145CAC(self, a0, a1);
    return 0;
}

SQInteger SetSceneOffsetFromPoint_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 634
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 637
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_00145FD8(self, a0, a1);
    return 0;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger GetInitExistType_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 662
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00150CDC(self, a0));
    return 1;
}

SQInteger GetAllyIndex_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 673
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00150CB4(self, a0));
    return 1;
}

SQInteger GetEnemyIndex_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 684
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00150F3C(self, a0));
    return 1;
}

SQInteger GetFbxPointPos_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 134
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001447BC(v, fn_0015F298(self, a0));
    return 1;
}

SQInteger GetFbxPos_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 145
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001447BC(v, fn_001525C8(self, a0));
    return 1;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger GetBonePos_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 156
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 159
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    UnkVec3 pos = fn_001508B4(self, a0, a1);
    fn_001447BC(v, &pos);
    return 1;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger GetRidePos_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 170
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    UnkVec3 pos = fn_0015094C(self, a0);
    fn_001447BC(v, &pos);
    return 1;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger IsMaster_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 706
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00152334(self, a0));
    return 1;
}

SQInteger IsHighRankSpell_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 717
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_001513B8(self, a0));
    return 1;
}

SQInteger SetMessage_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 735
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_00150A7C(self, a0);
    return 0;
}

SQInteger SetTalkName_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 744
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_00150C60(self, a0);
    return 0;
}

SQInteger ShowActionName_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 767
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001512B4(self, a0);
    return 0;
}

SQInteger ShowBattleEventMessage_(HSQUIRRELVM v) {
    SQBool a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getbool(v, -2, &a0))) {
#line 777
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 779
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00151E20(self, a0 == 1, a1, 0);
    return 0;
}

SQInteger ShowBattleFeatMessage_(HSQUIRRELVM v) {
    SQBool a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getbool(v, -2, &a0))) {
#line 789
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 791
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00151E20(self, a0 == 1, a1, 1);
    return 0;
}

SQInteger ShowBattleOtherMessage_(HSQUIRRELVM v) {
    SQBool a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getbool(v, -2, &a0))) {
#line 801
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 803
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00151E20(self, a0 == 1, a1, 2);
    return 0;
}

SQInteger StartCombo_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 813
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00150B24(self, a0);
    return 0;
}

SQInteger StartComboBattleEventMessage_(HSQUIRRELVM v) {
    SQBool a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getbool(v, -2, &a0))) {
#line 823
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 826
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00151EA4(self, a0 == 1, a1, 0);
    return 0;
}

SQInteger AddActionName_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 836
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00150EDC(self, a0);
    return 0;
}

SQInteger AddBattleEventMessage_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 846
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00151C5C(self, a0, 0);
    return 0;
}

SQInteger AddBattleFeatMessage_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 856
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00151C5C(self, a0, 1);
    return 0;
}

SQInteger AddBattleOtherMessage_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 866
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00151C5C(self, a0, 2);
    return 0;
}

// The original inlines a helper named GetStatusValue (its __FUNCTION__ string is
// in this file's block) that reads the other arguments. The inlined error
// paths take the file name and message from the literal pool of fn_001489F0
// (0x00148AA8, 0x00148AC0). fn_001489F0 is the out-of-line copy of the helper
// (getters at lines 884 and 887, the "GetStatusValue" string in its pool),
// outside this unit's ranges. Not decompiled yet: the code below is a stand-in.
SQInteger GetStatusValue_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 903
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 884
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 887
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0015F224(self, a0, a1, a2));
    return 1;
}

SQInteger GetStatusFlag_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 912
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 915
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 918
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00150FAC(self, a0, a1, a2));
    return 1;
}

SQInteger GetStatusEndFlag_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 927
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 930
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 933
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00151564(self, a0, a1, a2));
    return 1;
}

// The original inlines a helper (its error path is at line 895) that takes the
// file name and message from the literal pool of fn_001489F0 (0x00148AA8,
// 0x00148AC0), like GetStatusValue_. Which of the GetStatusValue and
// GetMonsterStatusValue strings it uses is not established. Not decompiled
// yet: the code below is a stand-in.
SQInteger GetMonsterStatusValue_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 942
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 895
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00151D58(self, a0, a1));
    return 1;
}

SQInteger GetMonsterHp_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 951
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00150D3C(self, a0));
    return 1;
}

SQInteger GetDamageType_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 960
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 963
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00150F24(self, a0, a1));
    return 1;
}

SQInteger GetTargetType_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 974
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0015EFD8(self, a0));
    return 1;
}

SQInteger GetActorIndex_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 985
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0015FD20(self, a0));
    return 1;
}

SQInteger GetTargetIndex_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 995
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 998
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    int r = fn_0015FE60(self, a0, a1);
    sq_pushinteger(v, r);
    return 1;
}

SQInteger GetDamageValue_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 1009
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 1012
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 1015
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00150FE4(self, a0, a1, a2));
    return 1;
}

SQInteger GetTeraDamageValue_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1026
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1029
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001518F0(self, a0, a1));
    return 1;
}

SQInteger GetRevivalValue_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1040
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1043
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00151378(self, a0, a1));
    return 1;
}

SQInteger GetTargetNum_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1055
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0015FBB0(self, a0));
    return 1;
}

SQInteger GetActHitNum_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1073
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1076
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00150C9C(self, a0, a1));
    return 1;
}

SQInteger GetUseMp_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1087
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0015225C(self, a0));
    return 1;
}

SQInteger GetAllyAppealPoint_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1120
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1123
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001518D8(self, a0, a1));
    return 1;
}

SQInteger GetEnemyAppealPoint_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1134
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1137
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00151990(self, a0, a1));
    return 1;
}

SQInteger GetStoleGold_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1148
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1151
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00150D6C(self, a0, a1));
    return 1;
}

SQInteger GetStoleItem_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1162
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1165
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00150D88(self, a0, a1));
    return 1;
}

SQInteger IsTargetSingle_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1184
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_001510E0(self, a0));
    return 1;
}

SQInteger IsCritical_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 1461
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 1464
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 1467
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00150A28(self, a0, a1, a2));
    return 1;
}

SQInteger IsGuard_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1276
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1279
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_001521A0(self, a0, a1));
    return 1;
}

SQInteger IsAbsorb_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1290
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1293
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_0015230C(self, a0, a1));
    return 1;
}

SQInteger IsReflect_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1304
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1307
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00152700(self, a0, a1));
    return 1;
}

SQInteger IsRevival_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1318
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1321
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00152728(self, a0, a1));
    return 1;
}

SQInteger IsRezaoral_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1332
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1335
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00150A54(self, a0, a1));
    return 1;
}

SQInteger IsAngel_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1346
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1349
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00152178(self, a0, a1));
    return 1;
}

SQInteger IsLivingDead_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1360
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1363
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00150DF0(self, a0, a1));
    return 1;
}

SQInteger IsBraveHart_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1374
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1377
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00150B8C(self, a0, a1));
    return 1;
}

SQInteger IsLastStand_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1388
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1391
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00150BB4(self, a0, a1));
    return 1;
}

SQInteger IsGambleBody_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 1402
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 1405
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 1408
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00150DC4(self, a0, a1, a2));
    return 1;
}

SQInteger IsCriticalGuard_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1419
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1422
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00151390(self, a0, a1));
    return 1;
}

SQInteger IsPoisonDamage_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1433
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1436
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_0015108C(self, a0, a1));
    return 1;
}

SQInteger IsSwapTarget_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1447
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1450
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00150E18(self, a0, a1));
    return 1;
}

SQInteger IsPasser_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1196
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00152364(self, a0));
    return 1;
}

SQInteger IsPalpnte_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1207
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_001526B0(self, a0));
    return 1;
}

SQInteger IsLightWave_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1218
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00150BDC(self, a0));
    return 1;
}

SQInteger IsFreezeWave_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1229
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00150DA0(self, a0));
    return 1;
}

SQInteger IsTokugi_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1240
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_001523B8(self, a0));
    return 1;
}

SQInteger IsTeraAttack_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1251
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_00150E40(self, a0));
    return 1;
}

SQInteger SetHpDamage_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1515
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1518
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00150C00(self, a0, a1);
    return 0;
}

SQInteger SetMpDamage_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1527
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1530
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00150C30(self, a0, a1);
    return 0;
}

SQInteger SetHpMaxDamage_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1539
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1542
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00151190(self, a0, a1);
    return 0;
}

SQInteger SetMpMaxDamage_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1551
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1554
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00151234(self, a0, a1);
    return 0;
}

SQInteger SetHpMax_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1563
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1566
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001524D8(self, a0, a1);
    return 0;
}

SQInteger SetMpMax_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1575
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1578
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00152508(self, a0, a1);
    return 0;
}

SQInteger SetStatusChange_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1587
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1590
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001513F8(self, a0, a1);
    return 0;
}

SQInteger SetFall_(HSQUIRRELVM v) {
    unsigned char x;
    unsigned char y;
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1599
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1600
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    y = a1;
    x = a0;
    fn_00155D64(lbl_007E7808, x, y);
    return 0;
}

SQInteger SetMonsterDead_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1609
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001511C0(self, a0);
    return 0;
}

SQInteger MonsterRevival_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1618
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1621
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001450C0(self, a0, a1);
    return 0;
}

SQInteger SetParamChange_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1630
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1633
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00151264(self, a0, a1);
    return 0;
}

SQInteger SetTolerChainRate_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1642
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_0015183C(self, a0);
    return 0;
}

SQInteger UnSettingAllowTarget_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1658
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00151C48(self, a0);
    return 0;
}

SQInteger PlayIconAttackAnim_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1674
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00156264(self, a0);
    return 0;
}

SQInteger PlayIconHealAndSupportAnim_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1683
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_0015639C(self, a0);
    return 0;
}

SQInteger AddAppealPoint_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1692
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1695
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001563CC(self, a0, a1);
    return 0;
}

SQInteger SetVisibleScoutGauge_(HSQUIRRELVM v) {
    SQBool a0;
    if (SQ_FAILED(sq_getbool(v, -1, &a0))) {
#line 1789
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_0015754C(self, a0);
    return 0;
}

SQInteger SetScoutGaugeValue_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1814
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001660F4(self, a0);
    return 0;
}

SQInteger AddScoutGaugeValue_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1824
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_0015750C(self, a0);
    return 0;
}

SQInteger Task_PathPointMoveEye_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQFloat a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 2063
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a1))) {
#line 2066
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00145904(self, a0, a1));
    return 1;
}

SQInteger Task_PathPointMoveTgt_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQFloat a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 2077
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a1))) {
#line 2080
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00146048(self, a0, a1));
    return 1;
}

SQInteger Task_PathPointMoveEyeSetFrm_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQFloat a1;
    SQFloat a2;
    SQFloat a3;
    SQFloat a4;
    if (SQ_FAILED(sq_getstring(v, -5, &a0))) {
#line 2092
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getfloat(v, -4, &a1))) {
#line 2095
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getfloat(v, -3, &a2))) {
#line 2098
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getfloat(v, -2, &a3))) {
#line 2101
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a4))) {
#line 2104
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    int frm[3] = {(int)a2, (int)a3, (int)a4};
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00145AE0(self, a0, a1, frm));
    return 1;
}

SQInteger Task_PathPointMoveTgtSetFrm_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQFloat a1;
    SQFloat a2;
    SQFloat a3;
    SQFloat a4;
    if (SQ_FAILED(sq_getstring(v, -5, &a0))) {
#line 2116
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getfloat(v, -4, &a1))) {
#line 2119
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getfloat(v, -3, &a2))) {
#line 2122
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getfloat(v, -2, &a3))) {
#line 2125
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a4))) {
#line 2128
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    int frm[3] = {(int)a2, (int)a3, (int)a4};
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00145BC4(self, a0, a1, frm));
    return 1;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger Task_RideChange_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2140
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 2143
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00144CCC(self, a0, a1));
    return 1;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger Task_ObjectFadeOut_(HSQUIRRELVM v) {
    SQInteger a0;
    SQFloat a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2202
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a1))) {
#line 2205
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00145350(self, a0, a1));
    return 1;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger Task_ObjectFadeIn_(HSQUIRRELVM v) {
    SQInteger a0;
    SQFloat a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2216
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a1))) {
#line 2219
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00145258(self, a0, a1));
    return 1;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger Task_ChangeMotion_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQFloat a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 2230
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 2233
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a2))) {
#line 2236
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001456F4(self, a0, a1, a2));
    return 1;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger Task_SetFrameAnimeMoveChar_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 2001
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a1))) {
#line 2004
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 2007
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00156F4C(self, a0, a1, a2));
    return 1;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger Task_AnimeMoveChar_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2018
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 2021
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00156F44(self, a0, a1));
    return 1;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger Task_SetFrameAnimeMoveCharNoDir_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 2032
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a1))) {
#line 2035
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 2038
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001570A8(self, a0, a1, a2));
    return 1;
}

// u8 load order: the original loads the object pointer into a scratch register
// before it masks the index (and r1, r0, #0xff), then moves it to r0; here the
// object is loaded straight into r0. No form tried gives the original order
// (locals, casts, inline wrappers, references, result locals, masks).
SQInteger Task_AnimeMoveCharNoDir_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2049
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 2052
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001570A0(self, a0, a1));
    return 1;
}

SQInteger Task_AnimeMoveCamera_(HSQUIRRELVM v) {
    const SQChar* a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 2171
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 2174
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001450F0(self, a0, a1));
    return 1;
}

SQInteger Task_SetFrameAnimeMoveCamera_(HSQUIRRELVM v) {
    const SQChar* a0;
    const SQChar* a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getstring(v, -3, &a0))) {
#line 2185
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a1))) {
#line 2188
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 2191
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_00145D78(self, a0, a1, a2));
    return 1;
}

SQInteger FilterOn_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    SQInteger a3;
    if (SQ_FAILED(sq_getinteger(v, -4, &a0))) {
#line 2248
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -3, &a1))) {
#line 2250
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a2))) {
#line 2252
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a3))) {
#line 2254
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_00146248(self, a0, a1, a2, a3);
    return 0;
}

SQInteger SetEventFlg_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2280
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 2283
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001400E4(self, a0, a1 == 1);
    return 0;
}

SQInteger GetEventFlg_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2293
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_001507D0(self, a0));
    return 1;
}

SQInteger SetNumFlg_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2304
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 2307
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_0015E834(self, a0, a1);
    return 0;
}

SQInteger GetNumFlg_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2317
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0015E814(self, a0));
    return 1;
}
