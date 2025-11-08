"""Plugin Loader - Load and instantiate plugins"""
import importlib
from typing import Dict, Any, Optional


class PluginLoader:
    """Loads plugin classes from discovered metadata"""
    
    def __init__(self, plugin_metadata: Dict[str, Dict[str, Any]], config: Dict[str, Any]):
        self.plugin_metadata = plugin_metadata
        self.config = config
        self.loaded_plugins = {}
    
    def load_plugin(self, plugin_name: str) -> Optional[Any]:
        """
        Load and instantiate a single plugin.
        
        Args:
            plugin_name: Name of plugin to load
            
        Returns:
            Plugin instance or None if failed
        """
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name]
        
        metadata = self.plugin_metadata.get(plugin_name)
        if not metadata:
            return None
        
        # Check if enabled in config
        plugin_config = self.config.get('plugins', {}).get(plugin_name, {})
        if not plugin_config.get('enabled', False):
            return None
        
        try:
            # Import plugin module
            module_path = f"archiverr.plugins.{plugin_name}.client"
            module = importlib.import_module(module_path)
            
            # Find plugin class (convention: {Name}Plugin)
            # Convert plugin_name to PascalCase: mock_test -> MockTest, tmdb -> Tmdb
            parts = plugin_name.split('_')
            class_name = ''.join(part.capitalize() for part in parts) + 'Plugin'
            
            # Special cases for acronyms
            if plugin_name == 'ffprobe':
                class_name = 'FFProbePlugin'
            elif plugin_name == 'tmdb':
                class_name = 'TMDbPlugin'
            elif plugin_name == 'tvdb':
                class_name = 'TVDbPlugin'
            elif plugin_name == 'omdb':
                class_name = 'OMDbPlugin'
            elif plugin_name == 'tvmaze':
                class_name = 'TVMazePlugin'
            
            plugin_class = getattr(module, class_name, None)
            if not plugin_class:
                return None
            
            # Instantiate
            instance = plugin_class(plugin_config)
            instance._metadata = metadata
            
            self.loaded_plugins[plugin_name] = instance
            return instance
            
        except Exception as e:
            if self.config.get('options', {}).get('debug', False):
                print(f"Failed to load plugin {plugin_name}: {e}")
            return None
    
    def load_all(self) -> Dict[str, Any]:
        """Load all enabled plugins"""
        plugins = {}
        
        for plugin_name in self.plugin_metadata.keys():
            plugin = self.load_plugin(plugin_name)
            if plugin:
                plugins[plugin_name] = plugin
        
        return plugins
    
    def load_by_category(self, category: str) -> Dict[str, Any]:
        """Load all plugins of a specific category"""
        plugins = {}
        
        for plugin_name, metadata in self.plugin_metadata.items():
            if metadata.get('category') != category:
                continue
            
            plugin = self.load_plugin(plugin_name)
            if plugin:
                plugins[plugin_name] = plugin
        
        return plugins
