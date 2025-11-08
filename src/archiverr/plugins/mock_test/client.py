"""Mock Test Plugin - Returns dummy data for testing"""
from typing import Dict, Any
from datetime import datetime
from typing import Dict, Any


class MockTestPlugin:
    """Output plugin that returns mock data for testing parallel execution"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "mock_test"
        self.category = "output"
    
    def execute(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return mock data.
        
        Args:
            match_data: Input match data
            
        Returns:
            {status, mock_data: {...}}
        """
        from datetime import datetime
        start_time = datetime.now()
        # Get input path for context
        input_path = None
        if 'scanner' in match_data:
            input_path = match_data['scanner'].get('input')
        elif 'file_reader' in match_data:
            input_path = match_data['file_reader'].get('input')
        
        end_time = datetime.now()
        return {
            'status': {
                'success': True,
                'started_at': start_time.isoformat(),
                'finished_at': end_time.isoformat(),
                'duration_ms': int((end_time - start_time).total_seconds() * 1000)
            },
            'mock_data': {
                'test_field': 'Mock plugin is working!',
                'input_received': input_path,
                'processed': True,
                'test_array': ['item1', 'item2', 'item3'],
                'test_nested': {
                    'level1': {
                        'level2': 'deep value'
                    }
                }
            }
        }
