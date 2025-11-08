"""File Reader Plugin - Read paths from .txt file"""
from typing import Dict, Any
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path


class FileReaderPlugin:
    """Input plugin that reads file paths from a text file"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "file_reader"
        self.category = "input"
    
    def execute(self) -> List[Dict[str, Any]]:
        """
        Read paths from text file(s) in targets.
        Returns list of matches: [{status, input}]
        """
        start_time = datetime.now()
        targets = self.config.get('targets', [])
        allow_virtual = self.config.get('allow_virtual_paths', False)
        
        results = []
        for target in targets:
            if not target.endswith('.txt'):
                continue
            
            target_path = Path(target)
            if not target_path.exists():
                continue
            
            with open(target_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Skip existence check if allow_virtual is True
                        if not allow_virtual and not Path(line).exists():
                            continue
                        
                        item_start = datetime.now()
                        item_end = datetime.now()
                        results.append({
                            'status': {
                                'success': True,
                                'started_at': item_start.isoformat(),
                                'finished_at': item_end.isoformat(),
                                'duration_ms': int((item_end - item_start).total_seconds() * 1000)
                            },
                            'input': line
                        })
        
        return results
