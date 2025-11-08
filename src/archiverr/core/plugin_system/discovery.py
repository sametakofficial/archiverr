"""Plugin Discovery - Scan and load plugin metadata"""
import json
from pathlib import Path
from typing import Dict, List, Any
from archiverr.utils.debug import get_debugger


class PluginDiscovery:
    """Discovers plugins by scanning plugin.json files"""
    
    def __init__(self, plugins_dir: str = None):
        if plugins_dir is None:
            # Default: src/archiverr/plugins (from core/plugin_system/discovery.py → archiverr/plugins)
            base = Path(__file__).parent.parent.parent
            plugins_dir = base / 'plugins'
        
        self.plugins_dir = Path(plugins_dir)
        self.debugger = get_debugger()
    
    def discover(self) -> Dict[str, Dict[str, Any]]:
        """
        Scan plugins directory and load plugin.json files.
        
        Returns:
            Dict[plugin_name, plugin_metadata]
        """
        plugins = {}
        
        if not self.plugins_dir.exists():
            self.debugger.warn("discovery", "Plugins directory not found", path=str(self.plugins_dir))
            return plugins
        
        self.debugger.debug("discovery", "Scanning plugins directory", path=str(self.plugins_dir))
        
        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue
            
            plugin_json = plugin_dir / 'plugin.json'
            if not plugin_json.exists():
                self.debugger.debug("discovery", "Skipping directory (no plugin.json)", dir=plugin_dir.name)
                continue
            
            try:
                with open(plugin_json, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                plugin_name = metadata.get('name')
                if not plugin_name:
                    self.debugger.warn("discovery", "Plugin missing name field", dir=plugin_dir.name)
                    continue
                
                # Add path info
                metadata['_path'] = str(plugin_dir)
                plugins[plugin_name] = metadata
                
                category = metadata.get('category', 'unknown')
                version = metadata.get('version', '?')
                self.debugger.debug("discovery", f"Found plugin", name=plugin_name, category=category, version=version)
                
            except Exception as e:
                self.debugger.error("discovery", "Failed to load plugin.json", dir=plugin_dir.name, error=str(e))
                continue
        
        return plugins
    
    def get_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get plugins filtered by category (input/output)"""
        all_plugins = self.discover()
        return {
            name: meta
            for name, meta in all_plugins.items()
            if meta.get('category') == category
        }
    
    def get_input_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Get all input plugins"""
        return self.get_by_category('input')
    
    def get_output_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Get all output plugins"""
        return self.get_by_category('output')
