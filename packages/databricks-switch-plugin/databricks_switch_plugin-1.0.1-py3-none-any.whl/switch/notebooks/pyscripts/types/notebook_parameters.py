"""Parameters for Switch notebook execution."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class NotebookParameters:
    """Parameters for Switch notebook execution.
    
    This dataclass defines all parameters used in Switch notebooks,
    with clear distinction between required and optional fields.
    """
    # Required parameters
    target_type: str
    source_format: str
    comment_lang: str
    log_level: str
    input_dir: str
    endpoint_name: str
    result_catalog: str
    result_schema: str
    token_count_threshold: int
    concurrency: int
    max_fix_attempts: int
    output_dir: str
    conversion_prompt_yaml: str
    
    # Optional parameters with defaults
    output_extension: str = ""
    sql_output_dir: str = ""
    request_params: str = ""
    
    @classmethod
    def from_notebook_globals(cls, **kwargs) -> 'NotebookParameters':
        """Create NotebookParameters from notebook global variables.
        
        Args:
            **kwargs: Keyword arguments containing parameter values
            
        Returns:
            NotebookParameters instance
        """
        return cls(**kwargs)