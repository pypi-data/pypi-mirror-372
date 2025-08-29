import os
import ctypes
import platform
from enum import IntEnum
from pathlib import Path


class Language(IntEnum):
    CPP = 0
    # _DEPRECATED_JAVASCRIPT = 1
    # _DEPRECATED_TYPESCRIPT = 2
    PHP = 3
    GO = 4
    # _DEPRECATED_TSX = 5
    RUST = 6


def validate_syntax(source_code: str, language: Language, path: str = "<code>") -> tuple[bool, str]:
    # path is used for display in error messages

    lang_id = int(language)
    debug_dump = False
    c_result = _lib.validate_code(
        source_code.encode("utf-8"),
        path.encode("utf-8"),
        lang_id,
        debug_dump,
    )
    try:
        if not c_result.has_error:
            return True, ""
        return False, c_result.formatted_report.decode("utf-8")
    finally:
        _lib.free_validation_result(c_result)


# --- Private ctypes Implementation ---

class _Validation_Result(ctypes.Structure):
    _fields_ = [
        ("has_error",        ctypes.c_bool  ),
        ("lineno",           ctypes.c_uint32),
        ("column",           ctypes.c_uint32),
        ("end_lineno",       ctypes.c_uint32),
        ("end_column",       ctypes.c_uint32),
        ("message",          ctypes.c_char_p),
        ("formatted_report", ctypes.c_char_p),
    ]


CURRENT_OS = platform.system().lower()

def _load_library(name: str):
    if CURRENT_OS == "darwin":
        LIB_EXT = ".dylib"
    elif CURRENT_OS == "windows":
        LIB_EXT = ".dll"
    else:
        LIB_EXT = ".so"

    lib_path = Path(__file__).parent / f"{name}{LIB_EXT}"
    if not lib_path.exists():
        raise ImportError(f"Cannot find compiled library at {lib_path}. "
                          "Please build it first.")

    return ctypes.CDLL(os.fsdecode(lib_path))

_lib = _load_library("_validator_tree")

_lib.validate_code.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint8, ctypes.c_bool]
_lib.validate_code.restype = _Validation_Result

_lib.free_validation_result.argtypes = [_Validation_Result]
_lib.free_validation_result.restype = None
