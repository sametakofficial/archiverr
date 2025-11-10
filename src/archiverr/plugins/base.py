"""Base Plugin Interface"""
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation test"""
    passed: bool
    details: Dict[str, Any]


class BasePlugin(ABC):
    """Base class for all plugins"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = None
        self.category = None
        self._metadata = {}
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute plugin logic"""
        pass
    
    def _validate_duration(
        self,
        ffprobe_duration: float,
        api_runtime_minutes: Optional[int],
        tolerance_seconds: int = 600
    ) -> ValidationResult:
        """
        Validate video duration against API runtime.
        
        Args:
            ffprobe_duration: Duration from ffprobe in seconds
            api_runtime_minutes: Runtime from API in minutes (None if not available)
            tolerance_seconds: Allowed difference in seconds (default: 600 = 10 min)
            
        Returns:
            ValidationResult with passed status and details
        """
        if api_runtime_minutes is None or api_runtime_minutes == 0:
            return ValidationResult(
                passed=False,
                details={
                    'ffprobe_duration': ffprobe_duration,
                    'api_runtime': None,
                    'diff_seconds': None,
                    'tolerance': tolerance_seconds,
                    'reason': 'API runtime not available'
                }
            )
        
        api_duration_seconds = api_runtime_minutes * 60
        diff_seconds = abs(ffprobe_duration - api_duration_seconds)
        passed = diff_seconds <= tolerance_seconds
        
        return ValidationResult(
            passed=passed,
            details={
                'ffprobe_duration': ffprobe_duration,
                'api_runtime': api_runtime_minutes,
                'diff_seconds': diff_seconds,
                'tolerance': tolerance_seconds
            }
        )


class InputPlugin(BasePlugin):
    """Base class for input plugins"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.category = "input"
    
    @abstractmethod
    def execute(self) -> List[Dict[str, Any]]:
        """
        Execute input plugin.
        
        Returns:
            List of matches: [{status, input, ...}]
        """
        pass


class OutputPlugin(BasePlugin):
    """Base class for output plugins"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.category = "output"
    
    @abstractmethod
    def execute(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute output plugin.
        
        Args:
            match_data: Current match data with results from previous plugins
            
        Returns:
            Plugin result: {status, ...data}
        """
        pass
