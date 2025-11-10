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
        Build complete API response structure with new format.
        
        Args:
            matches: List of processed matches with plugin results
            config: Config snapshot (for globals.options/plugins/tasks)
            start_time: Execution start time
            loaded_plugins: Loaded plugin manifests for categories
            
        Returns:
            Complete API response with:
            - globals.summary (input_plugin, categories, etc.)
            - globals.options/plugins/tasks (config snapshot)
            - match.plugins wrapper
            - match.globals.output (tasks, validations, paths)
        """
        self.debugger.debug("response_builder", "Building API response", matches=len(matches))
        
        if start_time is None:
            start_time = datetime.now()
        
        if loaded_plugins:
            self.loaded_plugins = loaded_plugins
        
        now = datetime.now()
        
        # Build matches with new structure
        processed_matches = []
        total_errors = 0
        total_size_bytes = 0
        total_duration_seconds = 0.0
        
        for index, match in enumerate(matches):
            formatted_match = self._format_match(match, index, config)
            processed_matches.append(formatted_match)
            
            # Count errors
            match_status = formatted_match['globals']['status']
            failed_count = len(match_status.get('failed_plugins', []))
            if failed_count > 0:
                total_errors += 1
            
            # Accumulate size and duration
            ffprobe_data = formatted_match.get('plugins', {}).get('ffprobe', {})
            if ffprobe_data and isinstance(ffprobe_data, dict):
                container = ffprobe_data.get('container', {})
                if container:
                    total_size_bytes += container.get('size', 0)
                    total_duration_seconds += container.get('duration', 0)
        
        # Build globals with summary, options, plugins, tasks
        end_time = now
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Build summary with validations
        summary = self._build_summary(processed_matches, total_size_bytes, total_duration_seconds)
        
        # Add validation summary to globals.summary
        validation_summary = self._build_global_validations_summary(processed_matches)
        summary['validations'] = validation_summary
        
        globals_data = {
            'status': {
                'success': total_errors == 0,
                'matches': len(matches),
                'tasks': 0,  # Will be updated by task executor
                'errors': total_errors,
                'started_at': start_time.isoformat(),
                'finished_at': end_time.isoformat(),
                'duration_ms': duration_ms
            },
            'summary': summary
        }
        
        # Add config snapshot if provided
        if config:
            globals_data['options'] = config.get('options', {})
            globals_data['plugins'] = config.get('plugins', {})
            globals_data['tasks'] = config.get('tasks', [])
        
        self.debugger.info("response_builder", "API response built", 
                          matches=len(matches), errors=total_errors, 
                          categories=globals_data['summary']['categories'])
        
        return {
            'globals': globals_data,
            'matches': processed_matches
        }
    
    def _format_match(self, match: Dict[str, Any], index: int, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format a single match with new structure:
        - match.globals (index, input, status)
        - match.options (config snapshot for this match)
        - match.tasks (root level, will be filled later)
        - match.plugins.{plugin}.globals (status, options)
        - match.plugins.{plugin}.{data} (plugin's own structure)
        """
        # Extract components
        input_metadata = match.get('input', {'path': '', 'virtual': False})
        match_status = match.get('status', {})
        
        # Separate plugins from metadata
        raw_plugins = {}
        for key, value in match.items():
            if key not in ['input', 'status']:
                raw_plugins[key] = value
        
        # Restructure plugins: move status/validation to plugin.globals
        formatted_plugins = {}
        for plugin_name, plugin_data in raw_plugins.items():
            if not isinstance(plugin_data, dict):
                formatted_plugins[plugin_name] = plugin_data
                continue
            
            # Extract status and validation
            plugin_status = plugin_data.get('status', {})
            plugin_validation = plugin_data.get('validation', {})
            
            # Get plugin-specific options from config
            plugin_options = {}
            if config:
                plugin_options = config.get('plugins', {}).get(plugin_name, {})
            
            # Build plugin.globals
            plugin_globals = {
                'status': plugin_status,
                'options': plugin_options
            }
            if plugin_validation:
                plugin_globals['validation'] = plugin_validation
            
            # Build formatted plugin (globals + plugin's own data)
            formatted_plugin = {'globals': plugin_globals}
            
            # Add plugin's own data (everything except status/validation)
            for key, value in plugin_data.items():
                if key not in ['status', 'validation']:
                    formatted_plugin[key] = value
            
            formatted_plugins[plugin_name] = formatted_plugin
        
        # Build match globals (no output anymore)
        match_globals = {
            'index': index,
            'input': input_metadata,
            'status': match_status
        }
        
        # Match-level options (config snapshot)
        match_options = config.get('options', {}) if config else {}
        
        return {
            'globals': match_globals,
            'options': match_options,
            'tasks': [],  # Will be filled later by task manager
            'plugins': formatted_plugins
        }
    
    def _build_validations_summary(self, plugins: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build validation summary from all plugins.
        Returns: {plugin_name: validation, summary: {...}}
        """
        validations = {}
        total_tests = 0
        passed_tests = 0
        
        for plugin_name, plugin_data in plugins.items():
            if isinstance(plugin_data, dict):
                plugin_globals = plugin_data.get('globals', {})
                validation = plugin_globals.get('validation', {})
                
                if validation:
                    validations[plugin_name] = validation
                    total_tests += validation.get('tests_total', 0)
                    passed_tests += validation.get('tests_passed', 0)
        
        # Build summary
        validation_summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'accuracy': round(passed_tests / total_tests, 2) if total_tests > 0 else 0.0
        }
        
        validations['summary'] = validation_summary
        return validations
    
    def _build_global_validations_summary(self, processed_matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build global validation summary across all matches.
        Returns: {total_tests, passed_tests, failed_tests, accuracy, by_plugin: {...}}
        """
        total_tests = 0
        passed_tests = 0
        by_plugin = {}
        
        for match in processed_matches:
            plugins = match.get('plugins', {})
            
            for plugin_name, plugin_data in plugins.items():
                if isinstance(plugin_data, dict):
                    plugin_globals = plugin_data.get('globals', {})
                    validation = plugin_globals.get('validation', {})
                    
                    if validation and validation.get('tests_total', 0) > 0:
                        # Track per-plugin totals
                        if plugin_name not in by_plugin:
                            by_plugin[plugin_name] = {
                                'total_tests': 0,
                                'passed_tests': 0
                            }
                        
                        by_plugin[plugin_name]['total_tests'] += validation.get('tests_total', 0)
                        by_plugin[plugin_name]['passed_tests'] += validation.get('tests_passed', 0)
                        
                        # Track global totals
                        total_tests += validation.get('tests_total', 0)
                        passed_tests += validation.get('tests_passed', 0)
        
        # Calculate accuracy per plugin
        for plugin_name, stats in by_plugin.items():
            stats['failed_tests'] = stats['total_tests'] - stats['passed_tests']
            stats['accuracy'] = round(stats['passed_tests'] / stats['total_tests'], 2) if stats['total_tests'] > 0 else 0.0
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'accuracy': round(passed_tests / total_tests, 2) if total_tests > 0 else 0.0,
            'by_plugin': by_plugin
        }
    
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
