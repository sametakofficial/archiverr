"""Scanner Plugin - File/Directory Discovery"""
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
from archiverr.utils.debug import get_debugger


class ScannerPlugin:
    """Input plugin that discovers media files from configured targets"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "scanner"
        self.category = "input"
        self.debugger = get_debugger()
    
    def execute(self, match_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Scan targets and return list of matches.
        Each match has structure: {status, input}
        """
        targets = self.config.get('targets', [])
        recursive = self.config.get('recursive', True)
        allow_virtual = self.config.get('allow_virtual_paths', False)
        
        self.debugger.debug("scanner", "Starting scan", targets=len(targets), recursive=recursive)
        
        results = []
        
        for target in targets:
            # Skip .txt files (handled by file_reader)
            if target.endswith('.txt'):
                continue
            
            target_path = Path(target)
            
            # Direct file
            if target_path.is_file():
                start_time = datetime.now()
                end_time = datetime.now()
                results.append({
                    'status': {
                        'success': True,
                        'started_at': start_time.isoformat(),
                        'finished_at': end_time.isoformat(),
                        'duration_ms': int((end_time - start_time).total_seconds() * 1000)
                    },
                    'input': {
                        'path': str(target_path),
                        'virtual': False
                    }
                })
            
            # Directory scanning
            elif target_path.is_dir() and recursive:
                for ext in ['.mkv', '.mp4', '.avi', '.m4v', '.ts']:
                    for file in target_path.rglob(f'*{ext}'):
                        if file.is_file():
                            start_time = datetime.now()
                            end_time = datetime.now()
                            results.append({
                                'status': {
                                    'success': True,
                                    'started_at': start_time.isoformat(),
                                    'finished_at': end_time.isoformat(),
                                    'duration_ms': int((end_time - start_time).total_seconds() * 1000)
                                },
                                'input': {
                                    'path': str(file),
                                    'virtual': False
                                }
                            })
            
            # Virtual path support
            elif allow_virtual and not target_path.exists():
                self.debugger.debug("scanner", "Virtual path detected", path=target)
                start_time = datetime.now()
                end_time = datetime.now()
                results.append({
                    'status': {
                        'success': True,
                        'started_at': start_time.isoformat(),
                        'finished_at': end_time.isoformat(),
                        'duration_ms': int((end_time - start_time).total_seconds() * 1000)
                    },
                    'input': {
                        'path': target,
                        'virtual': True
                    }
                })
        
        self.debugger.info("scanner", "Scan complete", found=len(results))
        return results
