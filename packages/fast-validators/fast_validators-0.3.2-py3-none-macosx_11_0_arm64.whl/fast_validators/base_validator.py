from pathlib import Path

class Validator:
    name: str = "default"

    supported_extensions: list[str] = []

    def validate(self, source_code: str, file_path: str | Path) -> tuple[bool, str]:
        """
        Validate the content for correctness.

        Args:
            source_code: The content to validate
            file_path: The target file_path (for context)

        Returns:
            tuple: (is_valid: bool, error_message: str)
                - is_valid: True if content is valid, False otherwise
                - error_message: Empty string if valid, error description if invalid
        """
        return True, ""
