import os
from pathlib import Path
from .base_validator import Validator


validators: list[Validator] = []
extension_to_validator: dict[str, Validator] = {}
name_to_validator: dict[str, Validator] = {}
default_validator = Validator()


def _add_validators():
    from .json_validator   import JsonValidator
    from .yaml_validator   import YamlValidator
    from .python_validator import PythonValidator
    from .php_validator    import PhpValidator
    from .go_validator     import GoValidator
    from .js_ts_validator  import JS_TS_Validator
    from .toml_validator   import Toml_Validator
    from .rust_validator   import Rust_Validator

    validators.extend([
        JsonValidator(),
        YamlValidator(),
        PythonValidator(),
        PhpValidator(),
        GoValidator(),
        JS_TS_Validator(),
        Toml_Validator(),
        Rust_Validator(),
    ])

    for validator in validators:
        assert validator.name not in name_to_validator, f"Validators names overlap: '{validator.name}'"
        name_to_validator[validator.name] = validator
        for ext in validator.supported_extensions:
            assert ext == ext.lower(), f"Supported extentions for '{type(validator).__name__}' should all be lower case"
            assert ext not in extension_to_validator, f"Validators extentions overlap: '{ext}'"
            extension_to_validator[ext] = validator


_add_validators()


def get_validator_for_file(file_path: str | Path) -> Validator:
    path: str = os.fspath(file_path)
    ext = os.path.splitext(path)[1].lower()
    return extension_to_validator.get(ext, default_validator)


def get_supported_extensions() -> list[str]:
    return list(extension_to_validator.keys())


def get_validator_names() -> list[str]:
    return list(name_to_validator.keys())


def validate_content(source_code: str, file_path: str | Path) -> tuple[bool, str]:  # is_valid, error_message
    path: str = os.fspath(file_path)
    validator = get_validator_for_file(path)
    return validator.validate(source_code, path)
