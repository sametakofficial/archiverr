"""File Reader Plugin - Read paths from .txt file"""
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
from archiverr.utils.debug import get_debugger


class FileReaderPlugin:
    """Input plugin that reads file paths from a text file"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "file_reader"
        self.category = "input"
        self.debugger = get_debugger()
    
    def execute(self) -> List[Dict[str, Any]]:
        """
        Read paths from text file(s) in targets.
        Returns list of matches: [{status, input}]
        """
        start_time = datetime.now()
        targets = self.config.get('targets', [])
        allow_virtual = self.config.get('allow_virtual_paths', False)
        
        self.debugger.debug("file_reader", "Reading targets", targets=len(targets), allow_virtual=allow_virtual)
        
        results = []
        for target in targets:
            # Check if target is a .txt file or a direct path
            if target.endswith('.txt'):
                # Read paths from text file
                target_path = Path(target)
                if not target_path.exists():
                    continue
                
                self.debugger.debug("file_reader", "Reading file", path=str(target_path))
                
                with open(target_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Check if path is virtual
                            path_exists = Path(line).exists()
                            is_virtual = not path_exists
                            
                            # Skip non-existent non-virtual paths
                            if not allow_virtual and is_virtual:
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
                                'input': {
                                    'path': line,
                                    'virtual': is_virtual
                                }
                            })
            else:
                # Direct path (not a .txt file)
                path_exists = Path(target).exists()
                is_virtual = not path_exists
                
                # Skip non-existent non-virtual paths
                if not allow_virtual and is_virtual:
                    continue
                
                self.debugger.debug("file_reader", "Direct path", path=target, virtual=is_virtual)
                
                item_start = datetime.now()
                item_end = datetime.now()
                results.append({
                    'status': {
                        'success': True,
                        'started_at': item_start.isoformat(),
                        'finished_at': item_end.isoformat(),
                        'duration_ms': int((item_end - item_start).total_seconds() * 1000)
                    },
                    'input': {
                        'path': target,
                        'virtual': is_virtual
                    }
                })
        
        self.debugger.info("file_reader", "Reading complete", found=len(results))
        return results
