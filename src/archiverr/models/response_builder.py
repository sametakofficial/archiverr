"""API Response Builder - Merge plugin results"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from archiverr.utils.debug import get_debugger


class APIResponseBuilder:
    """Builds final API response from plugin results"""
    
    def __init__(self):
        self.debugger = get_debugger()
        self.loaded_plugins = {}  # Will be set externally
    
    def build(
        self,
        matches: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None,
        start_time: Optional[datetime] = None,
        loaded_plugins: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build professional API response with time-series database structure.
        
        Design Philosophy:
        - Execution-centric: Each run is a timestamped execution record
        - Flat structure: Minimal nesting for query performance
        - Self-contained: All essential data in one document
        - MongoDB-ready: Optimized for time-series queries
        
        Args:
            matches: List of processed matches with plugin results
            config: Config snapshot (only enabled plugins)
            start_time: Execution start time
            loaded_plugins: Loaded plugin manifests
            
        Returns:
            Professional API response:
            {
                "execution": {metadata},
                "summary": {aggregates},
                "config_hash": "sha256",  # For deduplication
                "matches": [{results}]
            }
        """
        self.debugger.debug("response_builder", "Building API response", matches=len(matches))
        
        if start_time is None:
            start_time = datetime.now()
        
        if loaded_plugins:
            self.loaded_plugins = loaded_plugins
        
        now = datetime.now()
        
        # Process matches with flat structure
        processed_matches = []
        total_errors = 0
        total_size_bytes = 0
        total_duration_seconds = 0.0
        total_tasks_executed = 0
        
        for index, match in enumerate(matches):
            formatted_match = self._format_match_flat(match, index)
            processed_matches.append(formatted_match)
            
            # Aggregate statistics
            if not formatted_match.get('success', True):
                total_errors += 1
            
            # Size and duration from ffprobe
            ffprobe_data = formatted_match.get('ffprobe', {})
            if ffprobe_data:
                container = ffprobe_data.get('container', {})
                total_size_bytes += container.get('size', 0)
                total_duration_seconds += container.get('duration', 0)
            
            # Count tasks
            tasks = formatted_match.get('tasks', [])
            total_tasks_executed += len(tasks)
        
        # Execution metadata (flat, query-optimized)
        duration_ms = int((now - start_time).total_seconds() * 1000)
        
        # Build minimal config snapshot (only enabled plugins)
        config_snapshot = self._build_config_snapshot(config, loaded_plugins)
        config_hash = self._hash_config(config_snapshot)
        
        # Professional structure
        response = {
            # Execution metadata (indexed fields)
            'execution': {
                'started_at': start_time.isoformat(),
                'finished_at': now.isoformat(),
                'duration_ms': duration_ms,
                'success': total_errors == 0
            },
            
            # Aggregated summary (for quick stats)
            'summary': {
                'total_matches': len(matches),
                'successful_matches': len(matches) - total_errors,
                'failed_matches': total_errors,
                'total_tasks_executed': total_tasks_executed,
                'total_size_bytes': total_size_bytes,
                'total_duration_seconds': round(total_duration_seconds, 2),
                'enabled_plugins': list(config_snapshot.get('plugins', {}).keys())
            },
            
            # Config reference (for reproducibility)
            'config_hash': config_hash,
            'config': config_snapshot,
            
            # Match results
            'matches': processed_matches
        }
        
        self.debugger.info("response_builder", "API response built", 
                          matches=len(matches), errors=total_errors,
                          duration_ms=duration_ms)
        
        return response
    
    def _format_match_flat(self, match: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        Format match with professional flat structure.
        
        Philosophy:
        - Flat over nested (query performance)
        - Status at top level (quick filtering)
        - Plugin data directly accessible
        - Minimal metadata overhead
        
        Structure:
        {
            "index": 0,
            "input_path": "/path/file.mkv",
            "success": true,
            "executed_plugins": ["scanner", "ffprobe", "renamer", "tmdb"],
            "failed_plugins": [],
            "duration_ms": 2535,
            "tasks": [{task_results}],  # Flat, no nesting
            "scanner": {plugin_data},  # Direct access
            "ffprobe": {plugin_data},
            "renamer": {plugin_data},
            "tmdb": {plugin_data}
        }
        """
        # Extract metadata
        input_metadata = match.get('input', {})
        input_path = input_metadata.get('path', '') if isinstance(input_metadata, dict) else input_metadata
        
        match_status = match.get('status', {})
        success_plugins = match_status.get('success_plugins', [])
        failed_plugins = match_status.get('failed_plugins', [])
        not_supported = match_status.get('not_supported_plugins', [])
        duration_ms = match_status.get('duration_ms', 0)
        
        # Build flat match structure
        flat_match = {
            # Top-level metadata (indexed)
            'index': index,
            'input_path': input_path,
            'success': len(failed_plugins) == 0,
            'executed_plugins': success_plugins,
            'failed_plugins': failed_plugins,
            'not_supported_plugins': not_supported,
            'duration_ms': duration_ms,
            
            # Tasks array (flat)
            'tasks': []  # Will be populated by task executor
        }
        
        # Add plugin data directly (no 'plugins' wrapper)
        for key, value in match.items():
            if key not in ['input', 'status']:
                if isinstance(value, dict):
                    # Clean plugin data: remove nested 'globals' if exists
                    cleaned_data = self._clean_plugin_data(value)
                    flat_match[key] = cleaned_data
                else:
                    flat_match[key] = value
        
        return flat_match
    
    def _clean_plugin_data(self, plugin_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean plugin data: flatten status/validation into root.
        
        Old: {globals: {status: {...}, validation: {...}}, movie: {...}}
        New: {status: {...}, validation: {...}, movie: {...}}
        """
        if 'globals' in plugin_data:
            # Merge globals into root
            globals_data = plugin_data.pop('globals')
            plugin_data.update(globals_data)
        
        return plugin_data
    
    def _build_config_snapshot(self, config: Optional[Dict[str, Any]], loaded_plugins: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build minimal config snapshot (only enabled plugins).
        
        Philosophy: Store only what's needed for reproducibility.
        No full config dump - just enabled plugins and critical options.
        """
        if not config:
            return {}
        
        # Only critical options
        options = {
            'dry_run': config.get('options', {}).get('dry_run', True),
            'debug': config.get('options', {}).get('debug', False)
        }
        
        # Only enabled plugins (minimal config)
        plugins = {}
        for plugin_name, plugin_config in config.get('plugins', {}).items():
            if plugin_config.get('enabled', False):
                # Store only essential config (no sensitive data)
                plugins[plugin_name] = {
                    'enabled': True,
                    'version': loaded_plugins.get(plugin_name, {}).get('version', '1.0.0')
                }
        
        return {
            'options': options,
            'plugins': plugins
        }
    
    def _hash_config(self, config: Dict[str, Any]) -> str:
        """
        Generate config hash for deduplication.
        Same config = same hash = can reference instead of duplicate.
        """
        import hashlib
        import json
        
        # Deterministic JSON (sorted keys)
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]
    
    def _build_summary(
        self, 
        processed_matches: List[Dict[str, Any]],
        total_size_bytes: int,
        total_duration_seconds: float
    ) -> Dict[str, Any]:
        """
        Build globals.summary:
        - input_plugin_used
        - output_plugins_used
        - categories
        - total_size_bytes
        - total_duration_seconds
        """
        # Detect input plugin
        input_plugin_used = None
        output_plugins_used = set()
        
        for match in processed_matches:
            plugins = match.get('plugins', {})
            for plugin_name in plugins.keys():
                if plugin_name in ['scanner', 'file-reader']:
                    input_plugin_used = plugin_name
                else:
                    output_plugins_used.add(plugin_name)
        
        # Collect categories from loaded plugins
        categories = set()
        for plugin_name, plugin_manifest in self.loaded_plugins.items():
            plugin_categories = plugin_manifest.get('categories', [])
            if plugin_categories:  # Empty list means "all categories"
                categories.update(plugin_categories)
        
        # If no specific categories, default to common ones
        if not categories:
            categories = {'movie', 'show'}
        
        return {
            'input_plugin_used': input_plugin_used,
            'output_plugins_used': sorted(list(output_plugins_used)),
            'categories': sorted(list(categories)),
            'total_size_bytes': total_size_bytes,
            'total_duration_seconds': round(total_duration_seconds, 2)
        }
    
    def merge_plugin_result(
        self,
        match_data: Dict[str, Any],
        plugin_name: str,
        plugin_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge a single plugin result into match data.
        
        Args:
            match_data: Current match data
            plugin_name: Name of plugin
            plugin_result: Result from plugin
            
        Returns:
            Updated match data
        """
        updated = dict(match_data)
        updated[plugin_name] = plugin_result
        return updated
    
    def extract_success_plugins(self, match: Dict[str, Any]) -> List[str]:
        """Extract list of successful plugin names from match"""
        return match.get('status', {}).get('success_plugins', [])
    
    def extract_failed_plugins(self, match: Dict[str, Any]) -> List[str]:
        """Extract list of failed plugin names from match"""
        return match.get('status', {}).get('failed_plugins', [])
