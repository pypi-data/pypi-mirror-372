from ctypes import *
import sys

def LINE():
    return sys._getframe(1).f_lineno

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Cannot use
# class TypeDef:
#     PVOID = HANDLE = c_void_p
#     # ==float==
#     F32 = FLOAT = c_float
#     PF32 = PFLOAT = POINTER(c_float)
#     # ==double==
#     F64 = DOUBLE = c_double
#     PF64 = PDOUBLE = POINTER(c_double)
#     # ==char, uchar==
#     CHAR = c_char
#     PCHAR = c_char_p
#     UCHAR = c_ubyte
#     PUCHAR = POINTER(c_ubyte)
#     WCHAR = c_wchar
#     # ==int8, uint8==
#     I8 = c_int8
#     U8 = BOOL = BYTE = c_uint8
#     PI8 = POINTER(c_int8)
#     PU8 = POINTER(c_uint8)
#     # ==int16, uint16==
#     I16 = SHORT = c_int16
#     U16 = USHORT = WORD = c_uint16
#     PU16 = PUSHORT = POINTER(c_uint16)
#     PI16  = POINTER(c_int16)
#     # ==int32, uint32==
#     I32 = LONG = INT = c_int32
#     U32 = ULONG = UINT = DWORD = c_uint32
#     PI32 = POINTER(c_int32)
#     PU32 = PULONG = PUINT = POINTER(c_uint32)
#     # ==int64, uint64==
#     I64 = LONGLONG = c_int64
#     U64 = ULONGLONG = c_uint64
#     PI64 = PLONGLONG = POINTER(c_int64)
#     PU64 = PULONGLONG = POINTER(c_uint64)
