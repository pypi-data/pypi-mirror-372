import ctypes
import os
from pathlib import Path
from .base_validator import Validator

try:
    from .validator_tree import _load_library

    _lib = _load_library("_validator_rust")

    _lib.validate_rust.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    _lib.validate_rust.restype = ctypes.c_void_p

    _lib.free_rust.argtypes = [ctypes.c_void_p]
    _lib.free_rust.restype = None

    LIBRARY_MISSING_ERROR = ""
except (ImportError, OSError) as e:
    LIBRARY_MISSING_ERROR = (
        "The Rust validator could not be loaded.\n"
        "Please ensure the library has been built.\n"
        f"Details: {e}"
    )


class Rust_Validator(Validator):
    name: str = "rust"

    supported_extensions: list[str] = [".rs"]

    def validate(self, source_code: str, file_path: str | Path) -> tuple[bool, str]:
        if LIBRARY_MISSING_ERROR:
            return False, LIBRARY_MISSING_ERROR

        path: str = os.fspath(file_path)
        try:
            error_address = _lib.validate_rust(
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
                _lib.free_rust(error_address)
        except Exception as e:
            return False, f"An unexpected error occurred while validating {path}: {str(e)}"
