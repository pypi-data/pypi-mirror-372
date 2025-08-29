"""
Validators package for content validation in file operations.
"""

from .base_validator import Validator
from .catalog import (
    get_validator_for_file,
    get_supported_extensions,
    get_validator_names,
    validate_content,
)

__version__ = "0.3.1"
__all__ = [
    'Validator',
    'get_validator_for_file',
    'get_supported_extensions',
    'get_validator_names',
    'validate_content',
]
