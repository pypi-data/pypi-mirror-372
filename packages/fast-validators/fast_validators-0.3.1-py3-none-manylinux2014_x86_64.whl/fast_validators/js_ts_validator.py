import ctypes
import os
from pathlib import Path
from .base_validator import Validator

try:
    from .validator_tree import _load_library

    _lib = _load_library("_validator_js_ts")

    _lib.validate.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    _lib.validate.restype = ctypes.c_void_p

    _lib.free_result.argtypes = [ctypes.c_void_p]
    _lib.free_result.restype = None

    LIBRARY_MISSING_ERROR = ""
except (ImportError, OSError) as e:
    LIBRARY_MISSING_ERROR = (
        "The JavaScript/TypeScript validator could not be loaded.\n"
        "Please ensure the library has been built.\n"
        f"Details: {e}"
    )


class JS_TS_Validator(Validator):
    name: str = "js_ts"

    supported_extensions: list[str] = [".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts"]

    def validate(self, source_code: str, file_path: str | Path) -> tuple[bool, str]:
        if LIBRARY_MISSING_ERROR:
            return False, LIBRARY_MISSING_ERROR

        path: str = os.fspath(file_path)
        try:
            error_address = _lib.validate(
                source_code.encode("utf-8"),
                path.encode("utf-8")
            )

            try:
                if not error_address:
                    return True, ""

                error_string_ptr = ctypes.cast(error_address, ctypes.c_char_p)
                error_message = error_string_ptr.value.decode("utf-8")
                return False, error_message
            finally:
                _lib.free_result(error_address)
        except Exception as e:
            return False, f"An unexpected error occurred while validating {path}: {str(e)}"
