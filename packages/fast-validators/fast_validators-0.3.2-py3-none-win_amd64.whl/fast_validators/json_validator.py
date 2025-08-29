import json
import os
from pathlib import Path
from .base_validator import Validator


class JsonValidator(Validator):
    name: str = "json"

    supported_extensions: list[str] = ['.json', '.jsonl', '.geojson']

    def validate(self, source_code: str, file_path: str | Path) -> tuple[bool, str]:
        path: str = os.fspath(file_path)
        try:
            json.loads(source_code)
            return True, ""
        except json.JSONDecodeError as e:
            error_msg = self._format_json_error(e, path)
            return False, error_msg
        except Exception as e:
            return False, f"Unexpected error validating JSON in {path}: {str(e)}"

    def _format_json_error(self, error: json.JSONDecodeError, path: str) -> str:
        return (f"JSON validation failed for {path}:\n"
                f"Error: {error.msg}\n"
                f"Line: {error.lineno}, Column: {error.colno}\n"
                f"Position: {error.pos}")
