import re
import ast
import os
from pathlib import Path
from .base_validator import Validator


class PythonValidator(Validator):
    name: str = "python"

    supported_extensions: list[str] = ['.py', '.pyw']

    def validate(self, source_code: str, file_path: str | Path) -> tuple[bool, str]:
        path: str = os.fspath(file_path)
        try:
            return self._validate_syntax(source_code, path)
        except Exception as e:
            return False, f"Unexpected error validating Python code in {path}: {str(e)}"

    def _validate_syntax(self, code: str, path: str) -> tuple[bool, str]:
        try:
            ast.parse(code, filename=path)
            return True, ""
        except SyntaxError as e:
            return False, self._format_syntax_error(e, path)
        except Exception as e:
            return False, f"Syntax validation failed for {path}: {str(e)}"

    def _format_syntax_error(self, error: SyntaxError, path: str) -> str:
        """Format syntax error for user display"""
        error_details = [f"Python syntax error in {path}:"]

        if error.msg:
            error_details.append(f"Error: {error.msg}")

        if error.lineno:
            error_details.append(f"Line: {error.lineno}")

        if error.offset:
            error_details.append(f"Column: {error.offset}")

        if error.text:
            error_details.append(f"Code: {error.text.strip()}")
            if error.offset:
                # Add pointer to error location
                pointer = ' ' * (error.offset - 1) + '^'
                error_details.append(f"      {pointer}")

        return "\n".join(error_details)
