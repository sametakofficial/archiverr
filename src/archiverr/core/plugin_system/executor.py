"""Plugin Executor - Execute plugins with parallel support"""
import asyncio
import time
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor
from archiverr.utils.debug import get_debugger


class PluginExecutor:
    """Executes plugins in dependency order with parallel support"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.debugger = get_debugger()
    
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
                self.debugger.error("executor", f"Plugin not found", plugin=plugin_name)
                return plugin_name, self._error_result()
            
            try:
                self.debugger.debug("executor", f"Executing plugin", plugin=plugin_name)
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
                
                # Log result
                status = result.get('status', {})
                if status.get('not_supported'):
                    self.debugger.debug("executor", f"Plugin not supported", plugin=plugin_name, duration_ms=duration_ms)
                elif status.get('success'):
                    self.debugger.info("executor", f"Plugin executed successfully", plugin=plugin_name, duration_ms=duration_ms)
                else:
                    self.debugger.warn("executor", f"Plugin failed", plugin=plugin_name, duration_ms=duration_ms)
                
                return plugin_name, result
                
            except Exception as e:
                self.debugger.error("executor", f"Plugin execution error", plugin=plugin_name, error=str(e))
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
                self.debugger.debug("executor", f"Executing input plugin", plugin=plugin_name)
                results = plugin.execute()
                
                if isinstance(results, list):
                    self.debugger.info("executor", f"Input plugin found matches", plugin=plugin_name, count=len(results))
                    for result in results:
                        # Extract input metadata
                        input_metadata = result.get('input', {'path': '', 'virtual': False})
                        
                        # Add plugin name and input metadata to match
                        match = {
                            plugin_name: result,
                            'input': input_metadata
                        }
                        all_matches.append(match)
                else:
                    self.debugger.warn("executor", f"Input plugin returned non-list", plugin=plugin_name)
                        
            except Exception as e:
                self.debugger.error("executor", f"Input plugin failed", plugin=plugin_name, error=str(e))
                continue
        
        return all_matches
    
    def execute_output_pipeline(
        self,
        plugins: Dict[str, Any],
        execution_groups: List[List[str]],
        match_data: Dict[str, Any],
        resolver: Any = None
    ) -> Dict[str, Any]:
        """
        Execute output plugins with dynamic execution based on expectations.
        
        Args:
            plugins: Dict of loaded output plugins
            execution_groups: List of groups (from DependencyResolver)
            match_data: Initial match data from input plugins
            resolver: DependencyResolver instance for checking expectations
            
        Returns:
            Complete match data with all plugin results
        """
        result = dict(match_data)
        success_plugins = []
        failed_plugins = []
        not_supported_plugins = []
        
        # Track available data for expectations checking
        available_data = self._extract_available_data(result)
        
        for group_idx, group in enumerate(execution_groups):
            self.debugger.debug("executor", f"Executing group {group_idx}", plugins=", ".join(group))
            
            # If resolver provided, filter group by expectations
            if resolver:
                ready_plugins = [p for p in group if resolver.check_expects(p, available_data)]
                pending_plugins = [p for p in group if p not in ready_plugins]
                
                if pending_plugins:
                    self.debugger.debug("executor", "Some plugins waiting for expectations",
                                      pending=", ".join(pending_plugins))
                group = ready_plugins
            
            if not group:
                continue
            
            group_results = self.execute_group(plugins, group, result)
            
            for plugin_name, plugin_result in group_results.items():
                result[plugin_name] = plugin_result
                
                # Update input category if plugin provides it (generic pattern, no hardcoded names)
                if 'category' in plugin_result and 'input' in result and isinstance(result['input'], dict):
                    result['input']['category'] = plugin_result['category']
                    self.debugger.debug("executor", "Updated input category", 
                                      plugin=plugin_name, category=plugin_result['category'])
                
                # Update available data after each plugin execution
                available_data = self._extract_available_data(result)
                
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
        
        self.debugger.debug("executor", "Output pipeline complete",
                          success=len(success_plugins),
                          failed=len(failed_plugins),
                          not_supported=len(not_supported_plugins))
        
        return result
    
    def _extract_available_data(self, result: Dict[str, Any]) -> set:
        """
        Extract available data keys from current result.
        
        Examples:
        - 'input' if result has input
        - 'renamer.parsed' if result['renamer']['parsed'] exists
        - 'ffprobe.video' if result['ffprobe']['video'] exists
        
        Args:
            result: Current match result
            
        Returns:
            Set of available data keys
        """
        available = set()
        
        for key, value in result.items():
            if key in ['status', 'index']:
                continue
            
            # Add top-level key
            available.add(key)
            
            # Add nested keys (plugin.field)
            if isinstance(value, dict):
                for subkey in value.keys():
                    if subkey != 'status':  # Skip status fields
                        available.add(f"{key}.{subkey}")
        
        return available
    
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
