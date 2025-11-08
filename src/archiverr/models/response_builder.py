"""API Response Builder - Merge plugin results"""
from typing import Dict, List, Any
from datetime import datetime
from archiverr.utils.debug import get_debugger


class APIResponseBuilder:
    """Builds final API response from plugin results"""
    
    def __init__(self):
        self.debugger = get_debugger()
    
    def build(self, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build complete API response structure.
        
        Args:
            matches: List of processed matches with plugin results
            
        Returns:
            Complete API response:
            {
                'global_status': {...},
                'items': [...]
            }
        """
        self.debugger.debug("response_builder", "Building API response", matches=len(matches))
        
        now = datetime.now().isoformat()
        
        # Build items with index and rename status to matchGlobals
        items = []
        total_errors = 0
        for index, match in enumerate(matches):
            item = dict(match)
            item['index'] = index
            
            # Extract input metadata (should be at top level of match)
            input_metadata = item.get('input', {'path': '', 'virtual': False})
            
            # Rename status to matchGlobals and add input
            if 'status' in item:
                item['matchGlobals'] = item.pop('status')
                # Add input metadata to matchGlobals
                item['matchGlobals']['input'] = input_metadata
                # Count errors - only failed plugins, not "not supported" ones
                failed_count = len(item['matchGlobals'].get('failed_plugins', []))
                if failed_count > 0:
                    total_errors += 1
                    failed_plugins = item['matchGlobals'].get('failed_plugins', [])
                    self.debugger.warn("response_builder", f"Match has failed plugins", 
                                      index=index, failed=failed_plugins)
            
            items.append(item)
        
        # Build global status
        globals_data = {
            'status': {
                'success': total_errors == 0,
                'matches': len(matches),
                'tasks': 0,
                'errors': total_errors,
                'started_at': now,
                'finished_at': now,
                'duration_ms': 0
            }
        }
        
        self.debugger.info("response_builder", "API response built", 
                          matches=len(matches), errors=total_errors, success=(total_errors == 0))
        
        return {
            'globals': globals_data,
            'items': items
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
