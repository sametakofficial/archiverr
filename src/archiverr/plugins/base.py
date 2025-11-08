"""Base Plugin Interface"""
from typing import Dict, Any, List
from abc import ABC, abstractmethod


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
