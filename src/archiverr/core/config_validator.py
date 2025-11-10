"""Config Validator - Validate config.yml against JSON Schema"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


class ConfigValidator:
    """
    Validates config.yml structure using JSON Schema.
    
    Note: Requires jsonschema package (optional dependency).
    If not installed, validation is skipped with warning.
    """
    
    def __init__(self, schema_path: Optional[Path] = None):
        if schema_path is None:
            # Default: config.schema.json in project root
            schema_path = Path(__file__).parent.parent.parent.parent / 'config.schema.json'
        
        self.schema_path = schema_path
        self.schema = None
        self.validator = None
        
        # Try to load schema and validator
        self._init_validator()
    
    def _init_validator(self) -> None:
        """Initialize JSON Schema validator if possible"""
        try:
            # Try to import jsonschema
            from jsonschema import Draft7Validator
            
            # Load schema
            if not self.schema_path.exists():
                return
            
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
            
            # Create validator
            self.validator = Draft7Validator(self.schema)
            
        except ImportError:
            # jsonschema not installed - validation will be skipped
            pass
        except Exception:
            # Schema load failed - validation will be skipped
            pass
    
    def validate(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate config against schema.
        
        Args:
            config: Loaded config.yml as dict
            
        Returns:
            (is_valid, error_message)
            - (True, None) if valid or validation skipped
            - (False, "error details") if invalid
        """
        if self.validator is None:
            # Validation not available - assume valid
            return True, None
        
        try:
            # Validate
            errors = list(self.validator.iter_errors(config))
            
            if not errors:
                return True, None
            
            # Format first error
            error = errors[0]
            path = " -> ".join(str(p) for p in error.path)
            message = f"Config validation error at '{path}': {error.message}"
            
            return False, message
            
        except Exception as e:
            # Validation failed unexpectedly
            return False, f"Validation error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if validation is available"""
        return self.validator is not None
