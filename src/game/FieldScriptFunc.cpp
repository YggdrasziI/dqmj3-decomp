// FieldScriptFunc.cpp: Squirrel bindings used by the field scripts.
//
// The file name is the one the error paths pass to the error formatter
// ("FieldScriptFunc.cpp" in the literal pools of the 186 functions here).
// Its directory is unknown.
//
// Each binding is named after its __FUNCTION__ string, which its error path
// passes to the formatter. armcc puts the __FUNCTION__ strings of a file in one
// .constdata section, in source order: the 186 names at 0x00724B18-0x00725871
// give the order of the functions below. The bindings without an error path
// have no such string, and nothing ties them to this file yet.
//
// The field object at lbl_007E7808 and its methods are not decompiled; they are
// declared with their analysis names and the argument types the calls show.

#include <stddef.h>
#include <string.h>

#include "game/squirrel_api.h"

// A vector of three floats: fn_001446AC reads it from a script table with the
// keys "x", "y" and "z" (0x001447AC), fn_001447BC pushes one back.
struct UnkVec3 {
    float x;
    float y;
    float z;
};

// Filled by SetAnalyzeInfo_ from a script table; the field names are the table's
// keys ("flagId", "searchDist", "nameKey", "messageKey"), id is its first argument.
struct UnkAnalyzeInfo {
    int id;
    int flagId;
    float searchDist;
    const char* nameKey;
    const char* messageKey;
};

// Returned by fn_0060DA04; SetAnalyzeInfo_ reads one byte at 0xDC.
struct Unk0060DA04 {
    unsigned char unk0[0xDC];
    unsigned char unkDC;
};

extern "C" {
// Stubbed out in this build: returns "" (0x001446A0, 12 bytes).
const char* fn_001446A0(const char* msg, const char* file, const char* func, int line);
SQRESULT fn_001446AC(UnkVec3* out, HSQUIRRELVM v, SQInteger idx);
SQRESULT fn_001447BC(HSQUIRRELVM v, const UnkVec3* vec);
void fn_001BB68C(void* self, int, int);
void fn_001CE0F4(void* self, bool a0);
int fn_001D9DB4(void* self, const char* a0, int a1, const UnkVec3* pos);
int fn_001D9E8C(void* self, int a0, const UnkVec3* pos);
void fn_001D9FAC(void* self, int);
void fn_001DA194(void* self, const char*, bool, bool);
const char* fn_001DA2D4(void* self, int, const char*);
void fn_001DA534(void* self, bool);
void fn_001DA5CC(void* self, bool);
void fn_001DA600(void* self, signed char);
void fn_001DA638(void* self, short);
bool fn_001DA70C(void* self, int);
int fn_001DA748(void* self, const char*);
void fn_001DA788(void* self, int);
void fn_001DA7FC(void* self, int a0, const UnkVec3* pos);
void fn_001DA830(void* self, int);
void fn_001DA860(void* self, int, const char*);
void fn_001DA8CC(void* self, int a0, const UnkVec3* pos);
void fn_001DA908(void* self, const char*);
void fn_001DA958(void* self, int, bool);
void fn_001DA984(void* self, short, int);
void fn_001DA99C(void* self, unsigned char);
void fn_001DA9B0(void* self, int, int, int);
void fn_001DAAB0(void* self, int);
void fn_001DAB54(void* self, int);
void fn_001DD96C(void* self, unsigned char a0);
void fn_001DDA48(void* self, float);
void fn_001DDB68(void* self, int, bool);
void fn_001DDBA4(void* self, int, bool);
void fn_001DDBF8(void* self, unsigned char, unsigned char, unsigned char, unsigned char);
void fn_001DDCDC(void* self, unsigned char);
int fn_001DDD34(void* self, const char*, int);
void fn_001DDD90(void* self, int, const char*);
void fn_001DDDE8(void* self, float);
void fn_001DDE14(void* self, float);
void fn_001DDE40(void* self, int, const char*);
void fn_001DDE98(void* self, bool);
void fn_001DDEA8(void* self, int);
void fn_001DDEF8(void* self, int, bool);
void fn_001DDF24(void* self, unsigned char);
void fn_001DDF5C(void* self, int);
void fn_001DE400(void* self, int);
void fn_001DE450(void* self, const char*);
void fn_001DE4B8(void* self, int, const char*, bool);
void fn_001DE52C(void* self, int, float);
int fn_001DE660(void* self, int, bool);
int fn_001DE6B0(void* self, int, const char*);
void fn_001DE708(void* self, float, float, float, int);
void fn_001DE764(void* self, const char* a0, const UnkVec3* pos, float a1);
void fn_001DE7C4(void* self, int);
void fn_001DEAA0(void* self, int);
void fn_001DEABC(void* self, int);
void fn_001DEAE0(void* self, int);
void fn_001DEB54(void* self, signed char);
void fn_001DEBD4(void* self, int);
void fn_001DEBF8(void* self, bool);
void fn_001DEC1C(void* self, int, const char*);
void fn_001DEC88(void* self, const char*);
void fn_001DECAC(void* self, int, const char*);
int fn_001DECE0(void* self, int, float, bool);
int fn_001DED44(void* self, int, float, float);
int fn_001DEDBC(void* self, int a0, const UnkVec3* pos, float a1);
void fn_001DEE28(void* self, int);
void fn_001DEE50(void* self, int);
void fn_001DEE64(void* self, int a0);
void fn_001DEEE8(void* self, int, bool);
void fn_001DEEFC(void* self, int, float);
void fn_001DEF30(void* self, bool);
void fn_001DEF70(void* self, const char*);
void fn_001DEFB4(void* self, int, int);
void fn_001DF008(void* self, const char* a0, bool a1);
int fn_001DF0A8(void* self, int a0, const char* a1, float a2);
int fn_001DF138(void* self, int, int);
void fn_001DF450(void* self, SQBool);
void fn_001DF494(void* self, const UnkVec3* pos, float a0);
void fn_001DF4CC(void* self, int, bool);
void fn_001DF508(void* self, int, float);
int fn_001DF540(void* self, short);
int fn_001DF588(void* self, int, int);
int fn_001DF5F8(void* self, const char*, int, const char*);
int fn_001DF660(void* self, const UnkVec3* pos, float a0);
int fn_001DF804(void* self, const char*, const char*);
void fn_001DF8AC(void* self, const UnkVec3* pos, float a0);
int fn_001DF8D8(void* self, const char*, int, int);
int fn_001DF968(void* self, int, const char*);
int fn_001DFA00(void* self, const char*, bool);
void fn_001DFA58(void* self, const char*);
int fn_001DFA9C(void* self, const char*, const char*);
int fn_001DFBFC(void* self, int, const char*);
void fn_001DFEB8(void* self, const char*);
int fn_001DFF1C(void* self, int);
void fn_001DFF64(void* self, int);
void fn_001E0074(void* self, int);
void fn_001E0088(void* self, const UnkVec3* pos, float a0);
void fn_001E00C0(void* self, int, bool);
int fn_001E00EC(void* self, short, int);
void fn_001E013C(void* self, int);
void fn_001E014C(void* self, float);
void fn_001E01A4(void* self, int, bool);
void fn_001E01D8(void* self, int, bool);
void fn_001E023C(void* self, int a0, const UnkVec3* offset);
int fn_001E0274(void* self, const char*, bool);
void fn_001E043C(void* self, int, int, const char*, int);
int fn_001E0494(void* self, unsigned char, const char*);
void fn_001E04D8(void* self, int);
bool fn_001E064C(void* self, int);
int fn_001E068C(void* self, const char*, bool);
int fn_001E06D0(void* self, int, const char*, const char*, const char*);
int fn_001E06F0(void* self, const char*, float);
void fn_001E07F0(void* self, int, bool);
int fn_001E082C(void* self, int, const char*);
int fn_001E0834(void* self, int, const char*, float);
void fn_001E08E4(void* self, int);
void fn_001E0944(void* self, int);
void fn_001E09D4(void* self, const char*, bool);
int fn_001E0A04(void* self, const char*, unsigned char, int);
void fn_001E0AD0(void* self, int a0, const UnkVec3* offset);
int fn_001E0B08(void* self, int, const char*);
int fn_001E0BE8(void* self, int, float, float, const char*, const char*);
int fn_001E0C70(void* self, int a0, const UnkVec3* pos, float a1, const char* a2, const char* a3);
void fn_001E0CF8(void* self, int);
void fn_001E0E60(void* self, signed char, int);
int fn_001E0F2C(void* self, const char* a0, int a1, int a2, const UnkVec3* pos);
int fn_001E0FB0(void* self, int, const char*, const char*, const char*);
int fn_001E0FD0(void* self, int, float, const char*, const char*);
int fn_001E1378(void* self, const char*);
int fn_001E13CC(void* self, const char* a0, int a1, const char* a2, const UnkVec3* pos);
void fn_001E1490(void* self, int);
void fn_001E14A0(void* self, float);
void fn_001E1AA0(void* self, int, int, int, signed char);
void fn_001E1D40(void* self, int a0, const UnkVec3* pos);
void fn_001E1DF8(void* self, unsigned char, int);
void fn_001E1E54(void* self, int);
void fn_001E1E68(void* self, short, short);
int fn_001E1E94(void* self, const char*);
void fn_001E1F60(void* self, int, int);
void fn_001E1FF0(void* self, int, const char*);
void fn_001E203C(void* self, float);
void fn_001E207C(void* self, const char*);
void fn_001E2360(void* self, const char*);
void fn_001E23A4(void* self, unsigned char);
void fn_001E2414(void* self, int, bool);
void fn_001E2450(void* self, int, const char*, int);
void fn_001E25A0(void* self, int, const char*);
void fn_001FB54C(Unk0060DA04* self, const UnkAnalyzeInfo* info);
void fn_00239680(void* self, const char*);
void fn_002397FC(void* self, const char*, bool);
void fn_0029CBA0(void* self, bool);
const char* fn_0029CBC8(void* self, int a0);
void fn_0029CBE0(void* self, int, const char*);
void fn_0029CD48(void* self, const char*);
int fn_0060D108(void* self, short);
void fn_0060D14C(void* self, int, int);
bool fn_0060D180(void* self, unsigned char);
bool fn_0060D194(void* self, const char*);
void fn_0060D208(void* self, const char*, bool);
void fn_0060D3C8(void* self, int, int);
int fn_0060D568(void* self, short);
void fn_0060D654(void* self, int, int, float);
bool fn_0060D85C(void* self, unsigned char);
int fn_0060D96C(void* self, signed char);
Unk0060DA04* fn_0060DA04(void* self, int id);
int fn_0060DA30(void* self, unsigned char);
int fn_0060DAE0(void* self, int);
int fn_0060DB34(void* self, signed char, int);
int fn_0060DBC4(void* self, signed char, int);
int fn_0060DC5C(void* self, signed char, int);
int fn_0060DD20(void* self, signed char, int);
bool fn_0060DE18(void* self, signed char);
bool fn_0060DECC(void* self, signed char);
UnkVec3 fn_0060DF80(void* self, int a0);
void fn_0060E014(void* self, int, int, float);
bool fn_0060E054(void* self, short);
bool fn_0060E118(void* self, signed char, int, int);
int fn_0060E1F4(void* self, signed char, int);
UnkVec3 fn_0060E290(void* self, int a0);
int fn_0060E374(void* self, unsigned char);
bool fn_0060E390(void* self, int);
bool fn_0060E4A4(void* self, signed char);
float fn_0060E564(void* self, int);
const UnkVec3* fn_0060E5A0(void* self, int a0);
float fn_0060E640(void* self, int);
bool fn_0060E678(void* self, int);
int fn_0060E6AC(void* self, const char*);
int fn_0060E6D4(void* self, int);
int fn_0060E710(void* self, const char*);
void fn_0060E768(void* self, const char*, unsigned char);
void* fn_0064DCE8(void* self);
extern void* lbl_007E7808;
extern void* lbl_007E5984;
}

// The original passes the bare file name, not the compiler's __FILE__.
#define SCRIPT_ERROR(v, msg) \
    sq_throwerror((v), fn_001446A0((msg), "FieldScriptFunc.cpp", __FUNCTION__, __LINE__))

SQInteger SetPos_(HSQUIRRELVM v) {
    SQInteger a0;
    UnkVec3 pos;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 301
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    fn_001446AC(&pos, v, -1);
    void* self = lbl_007E7808;
    fn_001E1D40(self, a0, &pos);
    return 0;
}

// 92.8 %: the original copies the vector with ldmia r0, {r0, r1, r2}; this
// copies it as ldmia r0, {r1, r2} + ldr r0, [r0, #8] (pointer, memcpy, member
// and derived-struct forms give the same).
SQInteger GetPos_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 349
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    UnkVec3 pos = *fn_0060E5A0(self, a0);
    fn_001447BC(v, &pos);
    return 1;
}

SQInteger GetDir_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 458
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushfloat(v, fn_0060E564(self, a0));
    return 1;
}

SQInteger RideOn_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    SQInteger a3;
    if (SQ_FAILED(sq_getinteger(v, -4, &a0))) {
#line 729
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -3, &a1))) {
#line 732
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a2))) {
#line 735
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a3))) {
#line 738
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E1AA0(self, a0, a1, a2, a3);
    return 0;
}

SQInteger EndDemoBgmFade_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 34
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DDF5C(self, a0);
    return 0;
}

SQInteger CheckFieldRideMonster_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 57
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_0060E054(self, a0));
    return 1;
}

SQInteger PlayerForcePause_(HSQUIRRELVM v) {
    SQBool a0;
    if (SQ_FAILED(sq_getbool(v, -1, &a0))) {
#line 81
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = fn_0064DCE8(lbl_007E5984);
    fn_001CE0F4(self, a0);
    return 0;
}

SQInteger ReadNpc_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 91
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E1E94(self, a0));
    return 1;
}

SQInteger ArrangeNpc_(HSQUIRRELVM v) {
    SQInteger a0;
    UnkVec3 pos;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 101
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    fn_001446AC(&pos, v, -1);
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001D9E8C(self, a0, &pos));
    return 1;
}

SQInteger ArrangePointNpc_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 114
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 117
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DE6B0(self, a0, a1));
    return 1;
}

SQInteger SetComMode_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 127
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 130
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_0060D14C(self, a0, a1);
    return 0;
}

SQInteger SetWalkRadius_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 139
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 142
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_0060D3C8(self, a0, a1);
    return 0;
}

SQInteger SetTalkEnable_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 151
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 154
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DDEF8(self, a0, a1);
    return 0;
}

SQInteger SetSearchableAngle_(HSQUIRRELVM v) {
    SQInteger a0;
    SQFloat a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 163
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a1))) {
#line 166
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_001DF508(self, a0, a1);
    return 0;
}

SQInteger AddNearPlayerStopEffect_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    const SQChar* a2;
    SQInteger a3;
    if (SQ_FAILED(sq_getinteger(v, -4, &a0))) {
#line 175
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -3, &a1))) {
#line 178
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a2))) {
#line 181
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a3))) {
#line 184
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E043C(self, a0, a1, a2, a3);
    return 0;
}

SQInteger ReadGimmick_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 193
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DA748(self, a0));
    return 1;
}

SQInteger ArrangeGimmick_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQInteger a1;
    UnkVec3 pos;
    if (SQ_FAILED(sq_getstring(v, -3, &a0))) {
#line 203
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 206
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    fn_001446AC(&pos, v, -1);
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001D9DB4(self, a0, a1, &pos));
    return 1;
}

SQInteger ArrangePointGimmick_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQInteger a1;
    const SQChar* a2;
    if (SQ_FAILED(sq_getstring(v, -3, &a0))) {
#line 219
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 222
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a2))) {
#line 225
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DF5F8(self, a0, a1, a2));
    return 1;
}

SQInteger SetGimmickMapHitEnable_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 235
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 238
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001E01A4(self, a0, a1);
    return 0;
}

SQInteger ArrangeReactorPoint_(HSQUIRRELVM v) {
    UnkVec3 pos;
    SQFloat a0;
    fn_001446AC(&pos, v, -2);
    if (SQ_FAILED(sq_getfloat(v, -1, &a0))) {
#line 250
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DF660(self, &pos, a0));
    return 1;
}

SQInteger ArrangePointReactorPoint_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQFloat a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 260
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a1))) {
#line 263
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E06F0(self, a0, a1));
    return 1;
}

SQInteger SetPosNoFit_(HSQUIRRELVM v) {
    SQInteger a0;
    UnkVec3 pos;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 313
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    fn_001446AC(&pos, v, -1);
    void* self = lbl_007E7808;
    fn_001DA8CC(self, a0, &pos);
    return 0;
}

SQInteger SetPointPos_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 325
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 328
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001DA860(self, a0, a1);
    return 0;
}

SQInteger SetPointPosNoFit_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 337
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 340
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001DEC1C(self, a0, a1);
    return 0;
}

SQInteger SetActive_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 359
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 362
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001E2414(self, a0, a1);
    return 0;
}

SQInteger GetActive_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 371
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_0060E678(self, a0));
    return 1;
}

SQInteger SetHideIfFar_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 381
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 384
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DDB68(self, a0, a1);
    return 0;
}

SQInteger SetReactorMarkerTypeHide_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 393
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 396
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001E07F0(self, a0, a1);
    return 0;
}

SQInteger IsReactorMarkerTypeHide_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 405
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_001E064C(self, a0));
    return 1;
}

SQInteger GetAlpha_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 426
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushfloat(v, fn_0060E640(self, a0));
    return 1;
}

SQInteger SetManualCalcAlpha_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 436
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 439
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DF4CC(self, a0, a1);
    return 0;
}

SQInteger SetDirToPos_(HSQUIRRELVM v) {
    SQInteger a0;
    UnkVec3 pos;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 468
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    fn_001446AC(&pos, v, -1);
    void* self = lbl_007E7808;
    fn_001DA7FC(self, a0, &pos);
    return 0;
}

SQInteger SetDirToPoint_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 480
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 483
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001DDD90(self, a0, a1);
    return 0;
}

SQInteger SetDirToPlayer_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 492
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DE400(self, a0);
    return 0;
}

SQInteger SetDirToObject_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 501
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 504
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001BB68C(self, a0, a1);
    return 0;
}

SQInteger Task_RotateToPos_(HSQUIRRELVM v) {
    SQInteger a0;
    UnkVec3 pos;
    SQFloat a1;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 513
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    fn_001446AC(&pos, v, -2);
    if (SQ_FAILED(sq_getfloat(v, -1, &a1))) {
#line 519
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DEDBC(self, a0, &pos, a1));
    return 1;
}

SQInteger Task_RotateToPosSetMotion_(HSQUIRRELVM v) {
    SQInteger a0;
    UnkVec3 pos;
    SQFloat a1;
    const SQChar* a2;
    const SQChar* a3;
    if (SQ_FAILED(sq_getinteger(v, -5, &a0))) {
#line 529
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    fn_001446AC(&pos, v, -4);
    if (SQ_FAILED(sq_getfloat(v, -3, &a1))) {
#line 535
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a2))) {
#line 538
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a3))) {
#line 541
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E0C70(self, a0, &pos, a1, a2, a3));
    return 1;
}

SQInteger Task_RotateToPlayerSetMotion_(HSQUIRRELVM v) {
    SQInteger a0;
    SQFloat a1;
    const SQChar* a2;
    const SQChar* a3;
    if (SQ_FAILED(sq_getinteger(v, -4, &a0))) {
#line 551
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -3, &a1))) {
#line 554
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a2))) {
#line 557
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a3))) {
#line 560
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E0FD0(self, a0, a1, a2, a3));
    return 1;
}

SQInteger Task_RotateToDir_(HSQUIRRELVM v) {
    SQInteger a0;
    SQFloat a1;
    SQFloat a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 570
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -2, &a1))) {
#line 573
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a2))) {
#line 576
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DED44(self, a0, a1, a2));
    return 1;
}

SQInteger Task_RotateToDirSetMotion_(HSQUIRRELVM v) {
    SQInteger a0;
    SQFloat a1;
    SQFloat a2;
    const SQChar* a3;
    const SQChar* a4;
    if (SQ_FAILED(sq_getinteger(v, -5, &a0))) {
#line 586
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -4, &a1))) {
#line 589
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getfloat(v, -3, &a2))) {
#line 592
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a3))) {
#line 595
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a4))) {
#line 598
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E0BE8(self, a0, a1, a2, a3, a4));
    return 1;
}

SQInteger SetMotion_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 608
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a1))) {
#line 611
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 614
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E2450(self, a0, a1, a2);
    return 0;
}

SQInteger GetMotion_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 623
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0060E6D4(self, a0));
    return 1;
}

SQInteger ReadMotion_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 633
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 636
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushstring(v, fn_001DA2D4(self, a0, a1), -1);
    return 1;
}

SQInteger IsMotionEnd_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 646
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_001DA70C(self, a0));
    return 1;
}

SQInteger SetMotionSpeed_(HSQUIRRELVM v) {
    SQInteger a0;
    SQFloat a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 656
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a1))) {
#line 659
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_001DE52C(self, a0, a1);
    return 0;
}

SQInteger SetFace_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 668
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 671
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001E1FF0(self, a0, a1);
    return 0;
}

SQInteger SetMeshVisible_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    SQBool a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 680
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a1))) {
#line 683
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a2))) {
#line 686
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DE4B8(self, a0, a1, a2);
    return 0;
}

SQInteger SetSilhouetteHideIfFar_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 717
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 720
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001E01D8(self, a0, a1);
    return 0;
}

SQInteger RideOff_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 747
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 750
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E1F60(self, a0, a1);
    return 0;
}

SQInteger SetTalkAction_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 759
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DDEA8(self, a0);
    return 0;
}

SQInteger SetTalkTurn_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 768
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 771
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DA958(self, a0, a1);
    return 0;
}

SQInteger AttachObject_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 787
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 790
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 793
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DA9B0(self, a0, a1, a2);
    return 0;
}

SQInteger DetachObject_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 802
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DAAB0(self, a0);
    return 0;
}

SQInteger SetStepSe_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 811
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 814
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001E25A0(self, a0, a1);
    return 0;
}

SQInteger ResetStepSe_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 823
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DA788(self, a0);
    return 0;
}

SQInteger SetStepSePan_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 832
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 835
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DDBA4(self, a0, a1);
    return 0;
}

SQInteger Task_MoveForward_(HSQUIRRELVM v) {
    SQInteger a0;
    SQFloat a1;
    SQBool a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 844
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -2, &a1))) {
#line 847
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a2))) {
#line 850
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DECE0(self, a0, a1, a2));
    return 1;
}

SQInteger Task_MoveToPointSetSpeed_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    SQFloat a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 860
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a1))) {
#line 863
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a2))) {
#line 866
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E0834(self, a0, a1, a2));
    return 1;
}

SQInteger Task_AnimeMoveNoDir_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 876
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 879
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E0B08(self, a0, a1));
    return 1;
}

SQInteger Task_AnimeMoveNoDirNoFit_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 889
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 892
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E082C(self, a0, a1));
    return 1;
}

SQInteger Task_AnimeMove_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 902
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 905
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DFBFC(self, a0, a1));
    return 1;
}

SQInteger Task_AnimeMoveNoFit_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 915
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 918
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DF968(self, a0, a1));
    return 1;
}

SQInteger Task_AnimeMoveSetMotion_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    const SQChar* a2;
    const SQChar* a3;
    if (SQ_FAILED(sq_getinteger(v, -4, &a0))) {
#line 928
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -3, &a1))) {
#line 931
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a2))) {
#line 934
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a3))) {
#line 937
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E06D0(self, a0, a1, a2, a3));
    return 1;
}

SQInteger Task_AnimeMoveNoFitSetMotion_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    const SQChar* a2;
    const SQChar* a3;
    if (SQ_FAILED(sq_getinteger(v, -4, &a0))) {
#line 947
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -3, &a1))) {
#line 950
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a2))) {
#line 953
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a3))) {
#line 956
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E0FB0(self, a0, a1, a2, a3));
    return 1;
}

SQInteger Task_ChangeMotion_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 966
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a1))) {
#line 969
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 972
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DF0A8(self, a0, a1, a2));
    return 1;
}

SQInteger Task_ObjectFadeIn_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 982
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 985
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DF138(self, a0, a1));
    return 1;
}

SQInteger Task_ObjectFadeOut_(HSQUIRRELVM v) {
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
    sq_pushinteger(v, fn_001DF588(self, a0, a1));
    return 1;
}

SQInteger ShowMsg_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 1021
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001E207C(self, a0);
    return 0;
}

SQInteger SetTalkName_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 1051
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001DA908(self, a0);
    return 0;
}

SQInteger SetMsgSpeed_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1060
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DA830(self, a0);
    return 0;
}

SQInteger OpenDialog_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQBool a1;
    SQBool a2;
    if (SQ_FAILED(sq_getstring(v, -3, &a0))) {
#line 1032
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getbool(v, -2, &a1))) {
#line 1034
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a2))) {
#line 1036
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DA194(self, a0, a1, a2);
    return 0;
}

SQInteger SetExchangeMsg_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 1069
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001DE450(self, a0);
    return 0;
}

SQInteger SetExchangePartyMonsterName_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1078
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1081
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E0E60(self, a0, a1);
    return 0;
}

SQInteger SetQueryDefault_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1110
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DEABC(self, a0);
    return 0;
}

SQInteger ShowScreenMessage_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQBool a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 1119
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 1122
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DF008(self, a0, a1);
    return sq_suspendvm(v);
}

SQInteger SetReactorMsg_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1131
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 1134
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001DDE40(self, a0, a1);
    return 0;
}

SQInteger SetReactorEvent_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1143
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DEAE0(self, a0);
    return 0;
}

SQInteger SetTargetNameKey_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1152
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 1155
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001DECAC(self, a0, a1);
    return 0;
}

SQInteger SetMonsterGenPlayerInvasionAreaMin_(HSQUIRRELVM v) {
    SQFloat a0;
    if (SQ_FAILED(sq_getfloat(v, -1, &a0))) {
#line 273
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_001E14A0(self, a0);
    return 0;
}

SQInteger PlacementMonster_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 289
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DEBD4(self, a0);
    return 0;
}

SQInteger SetCameraDir_(HSQUIRRELVM v) {
    SQFloat a0;
    if (SQ_FAILED(sq_getfloat(v, -1, &a0))) {
#line 1199
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_001DDA48(self, a0);
    return 0;
}

SQInteger SetPointCameraEye_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 1226
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001DEF70(self, a0);
    return 0;
}

SQInteger SetPointCameraTarget_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 1235
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001DFA58(self, a0);
    return 0;
}

SQInteger SetLinearCameraEye_(HSQUIRRELVM v) {
    UnkVec3 pos;
    SQFloat a0;
    fn_001446AC(&pos, v, -2);
    if (SQ_FAILED(sq_getfloat(v, -1, &a0))) {
#line 1247
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_001DF494(self, &pos, a0);
    return 0;
}

SQInteger SetLinearCameraTarget_(HSQUIRRELVM v) {
    UnkVec3 pos;
    SQFloat a0;
    fn_001446AC(&pos, v, -2);
    if (SQ_FAILED(sq_getfloat(v, -1, &a0))) {
#line 1259
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_001E0088(self, &pos, a0);
    return 0;
}

SQInteger SetTalkCameraType_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1268
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 1271
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DEFB4(self, a0, a1);
    return 0;
}

// 91.9 %: the original keeps a1 and a2 at sp+4 and the vector at sp+0xC and
// copies a1 and a2 with ldrd/strd; armcc puts the vector first here whatever
// the declaration order (a Set() method gives the ldrd/strd copy).
SQInteger SetTalkCameraEyeOffset_(HSQUIRRELVM v) {
    SQInteger a0;
    SQFloat a1;
    SQFloat a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 1280
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -2, &a1))) {
#line 1283
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a2))) {
#line 1286
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    UnkVec3 offset = {0.0f, a1, a2};
    void* self = lbl_007E7808;
    fn_001E023C(self, a0, &offset);
    return 0;
}

// 91.9 %: same difference as SetTalkCameraEyeOffset_.
SQInteger SetTalkCameraTargetOffset_(HSQUIRRELVM v) {
    SQInteger a0;
    SQFloat a1;
    SQFloat a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 1295
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -2, &a1))) {
#line 1298
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a2))) {
#line 1301
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    UnkVec3 offset = {0.0f, a1, a2};
    void* self = lbl_007E7808;
    fn_001E0AD0(self, a0, &offset);
    return 0;
}

SQInteger StartEarthQuake_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQFloat a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 1317
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 1320
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a2))) {
#line 1323
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_0060D654(self, a0, a1, a2);
    return 0;
}

SQInteger StartDecayEarthQuake_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQFloat a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 1332
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 1335
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a2))) {
#line 1338
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_0060E014(self, a0, a1, a2);
    return 0;
}

SQInteger Task_AnimeMoveCamera_(HSQUIRRELVM v) {
    const SQChar* a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 1354
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 1357
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DFA9C(self, a0, a1));
    return 1;
}

SQInteger SetNavimapVisible_(HSQUIRRELVM v) {
    SQBool a0;
    if (SQ_FAILED(sq_getbool(v, -1, &a0))) {
#line 1374
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DEF30(self, a0);
    return 0;
}

SQInteger ArrangePointNaviMapIcon_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1383
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 1386
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E0494(self, a0, a1));
    return 1;
}

SQInteger SetNaviMapIconVisible_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1396
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 1399
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001E00C0(self, a0, a1);
    return 0;
}

SQInteger SetNaviMapIconDir_(HSQUIRRELVM v) {
    SQInteger a0;
    SQFloat a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1408
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getfloat(v, -1, &a1))) {
#line 1411
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_001DEEFC(self, a0, a1);
    return 0;
}

SQInteger FocusIcon_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1420
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E23A4(self, a0);
    return 0;
}

SQInteger OpenNaviMapRideFilter_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1453
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E0074(self, a0);
    return 0;
}

SQInteger IsOpenNaviMapRideFilter_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1462
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_0060E390(self, a0));
    return 1;
}

SQInteger SetDispFlightMap_(HSQUIRRELVM v) {
    SQBool a0;
    if (SQ_FAILED(sq_getbool(v, -1, &a0))) {
#line 1471
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DEBF8(self, a0);
    return 0;
}

SQInteger SetPointCircleEventMine_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQBool a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 1486
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 1489
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E068C(self, a0, a1));
    return 1;
}

SQInteger SetPointBoxEventMine_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQBool a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 1499
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 1502
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DFA00(self, a0, a1));
    return 1;
}

SQInteger SetPointBoxEventMineNoFallWait_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 1512
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E1378(self, a0));
    return 1;
}

SQInteger DeleteEventMine_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1522
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DE7C4(self, a0);
    return 0;
}

SQInteger SetMinePlayerStop_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1531
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 1534
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DEEE8(self, a0, a1);
    return 0;
}

SQInteger ChangeBattleMonsterId_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1543
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DFF64(self, a0);
    return 0;
}

SQInteger ChangeBattleParty_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1551
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E04D8(self, a0);
    return 0;
}

SQInteger ChangeBattlePartyUseHitMap_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1560
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E0CF8(self, a0);
    return 0;
}

SQInteger ChangeDemo_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1645
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001D9FAC(self, a0);
    return 0;
}

SQInteger SetReturnDemoMap_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 1654
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001DEC88(self, a0);
    return 0;
}

SQInteger SetReturnDemoPosDir_(HSQUIRRELVM v) {
    UnkVec3 pos;
    SQFloat a0;
    fn_001446AC(&pos, v, -2);
    if (SQ_FAILED(sq_getfloat(v, -1, &a0))) {
#line 1666
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_001DF8AC(self, &pos, a0);
    return 0;
}

SQInteger InhibitMonsterGenerate_(HSQUIRRELVM v) {
    SQFloat a0;
    if (SQ_FAILED(sq_getfloat(v, -1, &a0))) {
#line 1675
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_001E014C(self, a0);
    return 0;
}

SQInteger BossTaskGuideFlowMenu_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1829
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DFF1C(self, a0));
    return 1;
}

SQInteger BossNPCRegistFlow_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1722
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DEE64(self, a0);
    return sq_suspendvm(v);
}

SQInteger BossNPCRegistFlowResponse_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1732
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E08E4(self, a0);
    return 0;
}

SQInteger BossArrangeStealthBox_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 1756
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001DFEB8(self, a0);
    return 0;
}

SQInteger BossSetupSkyMapMonsterNPC_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1853
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E0944(self, a0);
    return 0;
}

SQInteger BossGetTalkCameraEye_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1862
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    UnkVec3 pos = fn_0060DF80(self, a0);
    fn_001447BC(v, &pos);
    return 1;
}

SQInteger BossGetTalkCameraTarget_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1872
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    UnkVec3 pos = fn_0060E290(self, a0);
    fn_001447BC(v, &pos);
    return 1;
}

SQInteger PushCrackNPCItemNameAndNumMessage_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1622
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E1490(self, a0);
    return 0;
}

SQInteger ExecuteCrackNPCPresent_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1606
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E013C(self, a0);
    return 0;
}

// 99.4 %: v and the tag string are in r5 and r4 in the original, swapped here.
SQInteger GetCrackNPCMessageTag_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1944
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    const char* tag = fn_0029CBC8(self, a0);
    sq_pushstring(v, tag, strlen(tag));
    return 1;
}

SQInteger SetCrackNPCMessageNameTag_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 1955
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_0029CD48(self, a0);
    return 0;
}

SQInteger SetCrackNPCMessageTag_(HSQUIRRELVM v) {
    SQInteger a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 1965
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 1967
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_0029CBE0(self, a0, a1);
    return 0;
}

SQInteger SetDiscQuestEnd_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1977
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DEAA0(self, a0);
    return 0;
}

SQInteger SetDiscQuestUIStop_(HSQUIRRELVM v) {
    SQBool a0;
    if (SQ_FAILED(sq_getbool(v, -1, &a0))) {
#line 1987
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DF450(self, a0);
    return 0;
}

SQInteger AddDiscQuestValue_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 1997
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DEE28(self, a0);
    return 0;
}

SQInteger SetClearFlagCrackMap_(HSQUIRRELVM v) {
    SQBool a0;
    if (SQ_FAILED(sq_getbool(v, -1, &a0))) {
#line 2014
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_0029CBA0(self, a0);
    return 0;
}

SQInteger ChangeMap_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 2029
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_001E2360(self, a0);
    return 0;
}

SQInteger ChangeMapPosDir_(HSQUIRRELVM v) {
    const SQChar* a0;
    UnkVec3 pos;
    SQFloat a1;
    if (SQ_FAILED(sq_getstring(v, -3, &a0))) {
#line 2038
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    fn_001446AC(&pos, v, -2);
    if (SQ_FAILED(sq_getfloat(v, -1, &a1))) {
#line 2044
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_001DE764(self, a0, &pos, a1);
    return 0;
}

SQInteger GotoMenuScene_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2089
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DDCDC(self, a0);
    return 0;
}

SQInteger GotoMenuOpen_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2098
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DD96C(self, a0);
    return sq_suspendvm(v);
}

SQInteger AddFieldMenu_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2107
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DA99C(self, a0);
    return 0;
}

SQInteger AddPlayerAbility_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2116
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DEB54(self, a0);
    return 0;
}

SQInteger SetEventFlg_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQBool a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 2125
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 2128
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_0060D208(self, a0, a1);
    return 0;
}

SQInteger GetEventFlg_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 2137
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_0060D194(self, a0));
    return 1;
}

SQInteger SetNumFlg_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 2147
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 2150
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_0060E768(self, a0, a1);
    return 0;
}

SQInteger GetNumFlg_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 2159
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0060E710(self, a0));
    return 1;
}

SQInteger GetFlagID_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 2169
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0060E6AC(self, a0));
    return 1;
}

SQInteger SetStopLod_(HSQUIRRELVM v) {
    SQBool a0;
    if (SQ_FAILED(sq_getbool(v, -1, &a0))) {
#line 2193
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DA5CC(self, a0);
    return 0;
}

SQInteger SetPointWorldEffect_(HSQUIRRELVM v) {
    const SQChar* a0;
    const SQChar* a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 2202
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getstring(v, -1, &a1))) {
#line 2205
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DF804(self, a0, a1));
    return 1;
}

SQInteger SetBoneEffect_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 2216
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 2219
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DDD34(self, a0, a1));
    return 1;
}

SQInteger SetSelectBoneEffect_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQInteger a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getstring(v, -3, &a0))) {
#line 2230
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 2233
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 2236
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DF8D8(self, a0, a1, a2));
    return 1;
}

SQInteger SetSelectBoneEffectSetOffset_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQInteger a1;
    SQInteger a2;
    UnkVec3 pos;
    if (SQ_FAILED(sq_getstring(v, -4, &a0))) {
#line 2247
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -3, &a1))) {
#line 2250
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a2))) {
#line 2253
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    fn_001446AC(&pos, v, -1);
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E0F2C(self, a0, a1, a2, &pos));
    return 1;
}

SQInteger SetSelectBoneEffectPlayer_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQInteger a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getstring(v, -3, &a0))) {
#line 2267
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 2270
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 2273
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E0A04(self, a0, a1, a2));
    return 1;
}

SQInteger SetSelectBoneEffectSetBoneName_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQInteger a1;
    const SQChar* a2;
    UnkVec3 pos;
    if (SQ_FAILED(sq_getstring(v, -4, &a0))) {
#line 2284
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getinteger(v, -3, &a1))) {
#line 2287
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getstring(v, -2, &a2))) {
#line 2290
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    fn_001446AC(&pos, v, -1);
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E13CC(self, a0, a1, a2, &pos));
    return 1;
}

SQInteger GetPartyMonsterNum_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2304
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0060D96C(self, a0));
    return 1;
}

SQInteger GetPartyMonsterKind_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2321
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 2324
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0060DB34(self, a0, a1));
    return 1;
}

SQInteger GetOwnerMonsterKind_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2334
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0060DAE0(self, a0));
    return 1;
}

SQInteger GetPartyMonsterRank_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2344
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 2347
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0060DC5C(self, a0, a1));
    return 1;
}

SQInteger GetPartyMonsterPlus_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2357
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 2360
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0060DBC4(self, a0, a1));
    return 1;
}

SQInteger GetPartyMonsterSize_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2370
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 2373
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0060DD20(self, a0, a1));
    return 1;
}

SQInteger GetPartyMonsterLineAge_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2383
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 2386
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0060E1F4(self, a0, a1));
    return 1;
}

SQInteger IsPartyMonsterHpMax_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2396
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_0060DE18(self, a0));
    return 1;
}

SQInteger IsPartyMonsterMpMax_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2406
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_0060DECC(self, a0));
    return 1;
}

SQInteger CheckPartyMonsterSkill_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    if (SQ_FAILED(sq_getinteger(v, -3, &a0))) {
#line 2416
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a1))) {
#line 2419
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a2))) {
#line 2422
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_0060E118(self, a0, a1, a2));
    return 1;
}

SQInteger GetFieldRideTypeNum_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2432
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0060DA30(self, a0));
    return 1;
}

SQInteger GetNakamaMonsterRankNum_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2463
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0060E374(self, a0));
    return 1;
}

SQInteger IsRideTypeMonster_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2473
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_0060D85C(self, a0));
    return 1;
}

SQInteger CheckPartyMonsterChangeColor_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2490
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_0060E4A4(self, a0));
    return 1;
}

SQInteger SetTime_(HSQUIRRELVM v) {
    SQFloat a0;
    if (SQ_FAILED(sq_getfloat(v, -1, &a0))) {
#line 2507
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_001E203C(self, a0);
    return 0;
}

SQInteger SetWeather_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2523
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DA600(self, a0);
    return 0;
}

SQInteger Task_AddFellow_(HSQUIRRELVM v) {
    SQInteger a0;
    SQBool a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2538
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 2541
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DE660(self, a0, a1));
    return 1;
}

SQInteger Task_EncountEffect_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2558
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001DF540(self, a0));
    return 1;
}

SQInteger AddGold_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2568
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E1E54(self, a0);
    return 0;
}

SQInteger AddItem_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2584
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 2587
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E1E68(self, a0, a1);
    return 0;
}

SQInteger GetItemNum_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2596
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0060D108(self, a0));
    return 1;
}

SQInteger AddSendMedalCount_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2606
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DEE50(self, a0);
    return 0;
}

SQInteger AddAccessory_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2622
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 2625
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DA984(self, a0, a1);
    return 0;
}

SQInteger GetAccessoryNum_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2634
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_0060D568(self, a0));
    return 1;
}

SQInteger Task_AddAccessoryFlow_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2672
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 2675
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E00EC(self, a0, a1));
    return 1;
}

SQInteger AddOrnament_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2685
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DA638(self, a0);
    return 0;
}

SQInteger LoadLayout_(HSQUIRRELVM v) {
    const SQChar* a0;
    if (SQ_FAILED(sq_getstring(v, -1, &a0))) {
#line 2708
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    void* self = lbl_007E7808;
    fn_00239680(self, a0);
    return 0;
}

SQInteger SetLayoutAnime_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQBool a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 2717
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 2720
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_002397FC(self, a0, a1);
    return 0;
}

SQInteger Task_ChangeLayoutAnime_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQBool a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 2736
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 2739
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    sq_pushinteger(v, fn_001E0274(self, a0, a1));
    return 1;
}

SQInteger SetHitEnableMapChangeNull_(HSQUIRRELVM v) {
    const SQChar* a0;
    SQBool a1;
    if (SQ_FAILED(sq_getstring(v, -2, &a0))) {
#line 2749
        return SCRIPT_ERROR(v, "failed: sq_getstring");
    }
    if (SQ_FAILED(sq_getbool(v, -1, &a1))) {
#line 2752
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001E09D4(self, a0, a1);
    return 0;
}

SQInteger SetSepiaColor_(HSQUIRRELVM v) {
    SQBool a0;
    if (SQ_FAILED(sq_getbool(v, -1, &a0))) {
#line 2796
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DDE98(self, a0);
    return 0;
}

SQInteger SetBgBlack_(HSQUIRRELVM v) {
    SQBool a0;
    if (SQ_FAILED(sq_getbool(v, -1, &a0))) {
#line 2805
        return SCRIPT_ERROR(v, "failed: sq_getbool");
    }
    void* self = lbl_007E7808;
    fn_001DA534(self, a0);
    return 0;
}

SQInteger ChangeColorTone_(HSQUIRRELVM v) {
    SQFloat a0;
    SQFloat a1;
    SQFloat a2;
    SQInteger a3;
    if (SQ_FAILED(sq_getfloat(v, -4, &a0))) {
#line 2814
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getfloat(v, -3, &a1))) {
#line 2817
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getfloat(v, -2, &a2))) {
#line 2820
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a3))) {
#line 2823
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DE708(self, a0, a1, a2, a3);
    return 0;
}

SQInteger SetFogDensity_(HSQUIRRELVM v) {
    SQFloat a0;
    if (SQ_FAILED(sq_getfloat(v, -1, &a0))) {
#line 2832
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_001DDDE8(self, a0);
    return 0;
}

SQInteger SetFogDistMax_(HSQUIRRELVM v) {
    SQFloat a0;
    if (SQ_FAILED(sq_getfloat(v, -1, &a0))) {
#line 2848
        return SCRIPT_ERROR(v, "failed: sq_getfloat");
    }
    void* self = lbl_007E7808;
    fn_001DDE14(self, a0);
    return 0;
}

// Reads one slot of the table at the top of the stack. Each use is on one line,
// so the two error paths of a slot share its line number.
#define GET_SLOT(v, key, getter, dst) \
    sq_pushstring((v), (key), -1); \
    if (SQ_FAILED(sq_get((v), -2))) { \
        return SCRIPT_ERROR((v), "failed: sq_get"); \
    } \
    if (SQ_FAILED(getter((v), -1, &(dst)))) { \
        return SCRIPT_ERROR((v), "failed: " #getter); \
    } \
    sq_pop((v), 1)

// 99.2 %: registers permuted (v in r6, the zero in r5, &info in r4 in the
// original); aggregate, pointer and declaration-order variants do not fix it.
SQInteger SetAnalyzeInfo_(HSQUIRRELVM v) {
    UnkAnalyzeInfo info;
    SQInteger typeId;
    info.id = -1;
    info.flagId = -1;
    info.searchDist = 0.0f;
    info.nameKey = NULL;
    info.messageKey = NULL;
    if (SQ_FAILED(sq_getinteger(v, -2, &info.id))) {
#line 2864
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (info.id == -1) {
        return 0;
    }
    sq_pushstring(v, "typeId", -1);
    if (SQ_FAILED(sq_get(v, -2))) {
#line 2873
        return SCRIPT_ERROR(v, "failed: sq_get");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &typeId))) {
#line 2874
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    sq_pop(v, 1);
#line 2884
    GET_SLOT(v, "flagId", sq_getinteger, info.flagId);
    GET_SLOT(v, "flagId", sq_getinteger, info.flagId);
    GET_SLOT(v, "searchDist", sq_getfloat, info.searchDist);
    GET_SLOT(v, "nameKey", sq_getstring, info.nameKey);
    GET_SLOT(v, "messageKey", sq_getstring, info.messageKey);
    if (typeId == 1) {
        info.messageKey = NULL;
    }
    void* self = lbl_007E7808;
    Unk0060DA04* obj = fn_0060DA04(self, info.id);
    if (obj != NULL && obj->unkDC == 2) {
        fn_001FB54C(obj, &info);
    }
    return 0;
}

SQInteger AddCustomDisc_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    SQInteger a2;
    SQInteger a3;
    if (SQ_FAILED(sq_getinteger(v, -4, &a0))) {
#line 2907
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -3, &a1))) {
#line 2910
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -2, &a2))) {
#line 2913
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a3))) {
#line 2916
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DDBF8(self, a0, a1, a2, a3);
    return 0;
}

SQInteger AddSpecialDisc_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2926
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DDF24(self, a0);
    return 0;
}

SQInteger CheckTrophy_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2955
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    sq_pushbool(v, fn_0060D180(self, a0));
    return 1;
}

SQInteger FieldBgmStop_(HSQUIRRELVM v) {
    SQInteger a0;
    if (SQ_FAILED(sq_getinteger(v, -1, &a0))) {
#line 2985
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001DAB54(self, a0);
    return 0;
}

SQInteger AddCoin_(HSQUIRRELVM v) {
    SQInteger a0;
    SQInteger a1;
    if (SQ_FAILED(sq_getinteger(v, -2, &a0))) {
#line 2994
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    if (SQ_FAILED(sq_getinteger(v, -1, &a1))) {
#line 2997
        return SCRIPT_ERROR(v, "failed: sq_getinteger");
    }
    void* self = lbl_007E7808;
    fn_001E1DF8(self, a0, a1);
    return 0;
}
