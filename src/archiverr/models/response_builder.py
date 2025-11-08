"""API Response Builder - Merge plugin results"""
from typing import Dict, List, Any
from datetime import datetime


class APIResponseBuilder:
    """Builds final API response from plugin results"""
    
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
        now = datetime.now().isoformat()
        
        # Build items with index and rename status to matchGlobals
        items = []
        total_errors = 0
        for index, match in enumerate(matches):
            item = dict(match)
            item['index'] = index
            
            # Rename status to matchGlobals
            if 'status' in item:
                item['matchGlobals'] = item.pop('status')
                # Count errors - only failed plugins, not "not supported" ones
                failed_count = len(item['matchGlobals'].get('failed_plugins', []))
                if failed_count > 0:
                    total_errors += 1
            
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
