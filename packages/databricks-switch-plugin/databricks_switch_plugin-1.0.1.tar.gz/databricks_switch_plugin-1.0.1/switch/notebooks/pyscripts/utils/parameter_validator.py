"""Parameter validation utilities for Switch notebooks."""
from typing import List
import json

from ..types.comment_language import CommentLanguage
from ..types.log_level import LogLevel
from ..types.notebook_parameters import NotebookParameters
from ..types.target_type import TargetType
from ..types.source_format import SourceFormat


class SwitchParameterValidator:
    """Validates Switch notebook parameters with error accumulation."""

    def __init__(self):
        self.errors: List[str] = []

    def _validate_enum(self, value: str, valid_values: List[str], param_name: str) -> None:
        """Validate enum parameter against valid values."""
        if value not in valid_values:
            self.errors.append(f"Invalid {param_name}: '{value}'. Supported: {', '.join(valid_values)}")

    def _validate_positive_int(self, value: int, param_name: str) -> None:
        """Validate that integer parameter is positive."""
        if value <= 0:
            self.errors.append(f"{param_name} must be positive, got: {value}")

    def _validate_non_negative_int(self, value: int, param_name: str) -> None:
        """Validate that integer parameter is non-negative (>= 0)."""
        if value < 0:
            self.errors.append(f"{param_name} must be non-negative, got: {value}")

    def _validate_json_format(self, value: str, param_name: str) -> None:
        """Validate JSON string format."""
        if value:
            try:
                json.loads(value)
            except json.JSONDecodeError as e:
                self.errors.append(f"{param_name} is not valid JSON: {e}")

    def _validate_workspace_path(self, path: str, param_name: str, required: bool = True) -> None:
        """Validate Databricks workspace path format."""
        if not path and not required:
            return
        if not path:
            self.errors.append(f"{param_name} is required")
            return
        if not (path.startswith("/Workspace/") or path.startswith("/Users/") or path.startswith("/Shared/")):
            self.errors.append(f"{param_name} must be a Databricks workspace path (start with /Workspace/, /Users/, or /Shared/), got: {path}")

    def _validate_target_dependencies(self, target_type: str, output_extension: str) -> None:
        """Validate target-specific parameter dependencies."""
        if target_type == "file" and not output_extension:
            self.errors.append("output_extension is required when target_type='file'")

    def validate_all(self, params: NotebookParameters) -> List[str]:
        """
        Validate all parameters and return list of errors.

        Args:
            params: NotebookParameters dataclass instance

        Returns:
            List of validation error messages
        """
        self.errors = []

        # Validate enum values using dataclass attributes
        self._validate_enum(params.target_type, TargetType.get_supported_types(), "target_type")
        self._validate_enum(params.source_format, SourceFormat.get_supported_formats(), "source_format")
        self._validate_enum(params.comment_lang, CommentLanguage.get_supported_languages(), "comment_lang")
        self._validate_enum(params.log_level, LogLevel.get_supported_levels(), "log_level")

        # Validate positive integers
        self._validate_positive_int(params.token_count_threshold, "token_count_threshold")
        self._validate_positive_int(params.concurrency, "concurrency")
        
        # Validate non-negative integers (0 is allowed)
        self._validate_non_negative_int(params.max_fix_attempts, "max_fix_attempts")

        # Validate workspace paths
        self._validate_workspace_path(params.output_dir, "output_dir", required=True)
        self._validate_workspace_path(params.sql_output_dir, "sql_output_dir", required=False)

        # Validate JSON format
        self._validate_json_format(params.request_params, "request_params")

        # Validate target-specific dependencies
        self._validate_target_dependencies(params.target_type, params.output_extension)

        return self.errors
