"""Dependency Resolver - Build execution graph"""
from typing import Dict, List, Set, Any


class DependencyResolver:
    """Resolves plugin dependencies and creates execution order"""
    
    def __init__(self, plugin_metadata: Dict[str, Dict[str, Any]]):
        self.plugin_metadata = plugin_metadata
    
    def resolve(self, enabled_plugins: List[str]) -> List[List[str]]:
        """
        Resolve dependencies and return execution groups.
        Plugins in same group can run in parallel.
        
        Args:
            enabled_plugins: List of enabled plugin names
            
        Returns:
            List of groups, each group is list of plugin names
        """
        # Build dependency graph
        graph = {}
        for plugin_name in enabled_plugins:
            metadata = self.plugin_metadata.get(plugin_name, {})
            depends_on = metadata.get('depends_on', [])
            graph[plugin_name] = [d for d in depends_on if d in enabled_plugins]
        
        # Check for cycles
        if self._has_cycle(graph):
            raise ValueError("Circular dependency detected in plugins")
        
        # Topological sort into groups
        groups = []
        remaining = set(enabled_plugins)
        
        while remaining:
            # Find plugins with no unresolved dependencies
            ready = set()
            for plugin in remaining:
                deps = set(graph[plugin])
                if deps.issubset(set([p for g in groups for p in g])):
                    ready.add(plugin)
            
            if not ready:
                # Should not happen if no cycles
                break
            
            groups.append(sorted(ready))
            remaining -= ready
        
        return groups
    
    def _has_cycle(self, graph: Dict[str, List[str]]) -> bool:
        """Check if dependency graph has cycles using DFS"""
        visited = set()
        rec_stack = set()
        
        def visit(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if visit(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if visit(node):
                return True
        
        return False
    
    def get_dependencies(self, plugin_name: str) -> List[str]:
        """Get direct dependencies of a plugin"""
        metadata = self.plugin_metadata.get(plugin_name, {})
        return metadata.get('depends_on', [])
    
    def check_expects(self, plugin_name: str, available_data: Set[str]) -> bool:
        """
        Check if plugin's expects are satisfied.
        
        Args:
            plugin_name: Plugin to check
            available_data: Set of available data keys (e.g., {'input', 'ffprobe.video'})
            
        Returns:
            True if all expects are satisfied
        """
        metadata = self.plugin_metadata.get(plugin_name, {})
        expects = metadata.get('expects', [])
        
        for expect in expects:
            if expect not in available_data:
                return False
        
        return True
