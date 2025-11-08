"""Task Manager - Execute tasks for matches"""
from typing import Dict, List, Any
from pathlib import Path

from .template_manager import TemplateManager


class TaskManager:
    """Executes tasks (print, save) defined in config"""
    
    def __init__(self, config: Dict[str, Any], template_manager: TemplateManager = None):
        self.config = config
        self.template_manager = template_manager or TemplateManager()
        self.tasks = config.get('tasks', [])
    
    def execute_tasks_for_match(
        self,
        api_response: Dict[str, Any],
        current_index: int,
        dry_run: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Execute tasks for a single match when it completes.
        
        Args:
            api_response: API response with all items processed so far
            current_index: Index of the match that just completed
            dry_run: If True, don't actually save files
            
        Returns:
            List of task results for this match
        """
        task_results = []
        
        for task_config in self.tasks:
            result = self._execute_task(task_config, api_response, current_index, dry_run)
            if result:
                task_results.append(result)
        
        return task_results
    
    def _execute_task(
        self,
        task_config: Dict[str, Any],
        api_response: Dict[str, Any],
        current_index: int,
        dry_run: bool
    ) -> Dict[str, Any]:
        """
        Execute a single task for a single match.
        
        Args:
            task_config: Task configuration from config.yml
            api_response: Complete API response
            current_index: Current match index
            dry_run: If True, don't actually save files
            
        Returns:
            Task result or None
        """
        task_name = task_config.get('name', 'unnamed')
        task_type = task_config.get('type', 'print')
        condition = task_config.get('condition')
        
        # Check condition
        if condition:
            if not self.template_manager.evaluate_condition(condition, api_response, current_index):
                return None
        
        # Execute based on type
        if task_type == 'print':
            return self._execute_print(task_config, api_response, current_index, task_name)
        elif task_type == 'save':
            return self._execute_save(task_config, api_response, current_index, task_name, dry_run)
        
        return None
    
    def _execute_print(
        self,
        task_config: Dict[str, Any],
        api_response: Dict[str, Any],
        current_index: int,
        task_name: str
    ) -> Dict[str, Any]:
        """Execute print task"""
        template = task_config.get('template', '')
        
        if not template:
            return None
        
        output = self.template_manager.render(template, api_response, current_index)
        
        # Print to stdout
        print(output)
        
        return {
            'task_name': task_name,
            'index': current_index,
            'type': 'print',
            'output': output
        }
    
    def _execute_save(
        self,
        task_config: Dict[str, Any],
        api_response: Dict[str, Any],
        current_index: int,
        task_name: str,
        dry_run: bool
    ) -> Dict[str, Any]:
        """Execute save task"""
        destination_template = task_config.get('destination', '')
        
        if not destination_template:
            return None
        
        destination = self.template_manager.render(destination_template, api_response, current_index)
        
        # Get source file
        items = api_response.get('items', [])
        if current_index >= len(items):
            return None
        
        current_item = items[current_index]
        
        source = None
        if 'scanner' in current_item:
            source = current_item['scanner'].get('input')
        elif 'file_reader' in current_item:
            source = current_item['file_reader'].get('input')
        
        if not source or not destination:
            return None
        
        success = False
        if not dry_run:
            try:
                # Create destination directory
                dest_path = Path(destination)
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy or move file
                shutil.copy2(source, destination)
                success = True
                
            except Exception:
                success = False
        else:
            success = True
        
        return {
            'task_name': task_name,
            'index': current_index,
            'type': 'save',
            'source': source,
            'destination': destination,
            'success': success,
            'dry_run': dry_run
        }
