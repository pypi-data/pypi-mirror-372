import tomllib
import os
from pathlib import Path
from .base_validator import Validator


class Toml_Validator(Validator):
    name: str = "toml"

    supported_extensions: list[str] = [".toml"]

    def validate(self, source_code: str, file_path: str | Path) -> tuple[bool, str]:
        path: str = os.fspath(file_path)
        try:
            tomllib.loads(source_code)
            return True, ""
        except tomllib.TOMLDecodeError as e:
            error_msg = self._format_toml_error(e, path, source_code)
            return False, error_msg
        except Exception as e:
            return False, f"Unexpected error validating TOML in {path}: {str(e)}"

    def _format_toml_error(self, error: tomllib.TOMLDecodeError, path: str, source: str) -> str:
        if error.args:
            msg = error.args[0]
        else:
            msg = "unnamed error"

        return (
            f"TOML validation failed for {path}:\n" +
            f"Error: {msg}"
        )
