"""Plugin Executor - Execute plugins with parallel support"""
import asyncio
import time
from typing import Dict, List, Any, Set
from concurrent.futures import ThreadPoolExecutor


class PluginExecutor:
    """Executes plugins in dependency order with parallel support"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
    
    async def execute_group_async(
        self,
        plugins: Dict[str, Any],
        group: List[str],
        match_data: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute a group of plugins in parallel (no dependencies between them).
        
        Args:
            plugins: Dict of loaded plugin instances
            group: List of plugin names to execute
            match_data: Current match data
            
        Returns:
            Dict of plugin results {plugin_name: result}
        """
        async def run_plugin(plugin_name: str):
            plugin = plugins.get(plugin_name)
            if not plugin:
                return plugin_name, self._error_result()
            
            try:
                started_at = time.time()
                
                # Execute plugin
                result = await asyncio.to_thread(plugin.execute, match_data)
                
                finished_at = time.time()
                duration_ms = int((finished_at - started_at) * 1000)
                
                # Add status
                if not isinstance(result, dict):
                    result = {}
                
                if 'status' not in result:
                    result['status'] = {
                        'success': True,
                        'started_at': started_at,
                        'finished_at': finished_at,
                        'duration_ms': duration_ms
                    }
                
                return plugin_name, result
                
            except Exception:
                return plugin_name, self._error_result()
        
        # Run all plugins in group concurrently
        tasks = [run_plugin(name) for name in group]
        results = await asyncio.gather(*tasks)
        
        return dict(results)
    
    def execute_group(
        self,
        plugins: Dict[str, Any],
        group: List[str],
        match_data: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Sync wrapper for execute_group_async"""
        return asyncio.run(self.execute_group_async(plugins, group, match_data))
    
    def execute_input_plugins(
        self,
        plugins: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Execute all input plugins and collect matches.
        
        Returns:
            List of matches from all input plugins
        """
        all_matches = []
        
        for plugin_name, plugin in plugins.items():
            try:
                results = plugin.execute()
                
                if isinstance(results, list):
                    for result in results:
                        # Add plugin name
                        match = {
                            plugin_name: result
                        }
                        all_matches.append(match)
                        
            except Exception:
                continue
        
        return all_matches
    
    def execute_output_pipeline(
        self,
        plugins: Dict[str, Any],
        execution_groups: List[List[str]],
        match_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute output plugins in dependency order.
        
        Args:
            plugins: Dict of loaded output plugins
            execution_groups: List of groups (from DependencyResolver)
            match_data: Initial match data from input plugins
            
        Returns:
            Complete match data with all plugin results
        """
        result = dict(match_data)
        success_plugins = []
        failed_plugins = []
        not_supported_plugins = []
        
        for group in execution_groups:
            group_results = self.execute_group(plugins, group, result)
            
            for plugin_name, plugin_result in group_results.items():
                result[plugin_name] = plugin_result
                
                # Track success/failure/not_supported
                status = plugin_result.get('status', {})
                if status.get('not_supported', False):
                    not_supported_plugins.append(plugin_name)
                elif status.get('success', False):
                    success_plugins.append(plugin_name)
                else:
                    failed_plugins.append(plugin_name)
        
        # Add status
        from datetime import datetime
        now = datetime.now().isoformat()
        result['status'] = {
            'success_plugins': success_plugins,
            'failed_plugins': failed_plugins,
            'not_supported_plugins': not_supported_plugins,
            'success': len(failed_plugins) == 0,
            'started_at': now,
            'finished_at': now,
            'duration_ms': 0
        }
        
        return result
    
    def _error_result(self) -> Dict[str, Any]:
        """Create error result structure"""
        from datetime import datetime
        now = datetime.now().isoformat()
        return {
            'status': {
                'success': False,
                'started_at': now,
                'finished_at': now,
                'duration_ms': 0
            }
        }
