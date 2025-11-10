"""Task Manager - Execute tasks for matches"""
import shutil
import yaml
from typing import Dict, List, Any
from pathlib import Path

from .template_manager import TemplateManager
from archiverr.utils.debug import get_debugger


class TaskManager:
    """Executes tasks (print, save) defined in config"""
    
    def __init__(self, config: Dict[str, Any], template_manager: TemplateManager = None):
        self.config = config
        self.template_manager = template_manager or TemplateManager()
        self.tasks = config.get('tasks', [])
        self.debugger = get_debugger()
    
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
        
        self.debugger.debug("tasks", f"Evaluating tasks for match", index=current_index, total_tasks=len(self.tasks))
        
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
        is_external = task_config.get('external', False)
        
        # Handle external task
        if is_external:
            return self._execute_external_task(task_config, api_response, current_index, dry_run)
        
        task_type = task_config.get('type', 'print')
        condition = task_config.get('condition')
        
        # Check condition
        if condition:
            if not self.template_manager.evaluate_condition(condition, api_response, current_index):
                self.debugger.debug("tasks", f"Task condition not met", task=task_name)
                return None
        
        self.debugger.debug("tasks", f"Executing task", task=task_name, type=task_type)
        
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
        
        # Get source file from match.globals.input (generic pattern)
        matches = api_response.get('matches', [])
        if current_index >= len(matches):
            return None
        
        current_match = matches[current_index]
        
        # Use generic input metadata from match.globals (plugin-agnostic)
        match_globals = current_match.get('globals', {})
        input_metadata = match_globals.get('input', {})
        source = input_metadata.get('path')
        
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
    
    def _execute_external_task(
        self,
        task_config: Dict[str, Any],
        api_response: Dict[str, Any],
        current_index: int,
        dry_run: bool
    ) -> Dict[str, Any]:
        """
        Execute an external task from a YAML file.
        
        Args:
            task_config: Task config with 'path' to external file
            api_response: API response
            current_index: Current match index
            dry_run: Dry run mode
            
        Returns:
            Task result or None
        """
        task_name = task_config.get('name', 'unnamed')
        task_path = task_config.get('path')
        
        if not task_path:
            self.debugger.error("tasks", "External task missing 'path'", task=task_name)
            return None
        
        # Resolve path relative to config directory
        config_dir = Path(self.config.get('_config_dir', '.'))
        external_file = config_dir / task_path
        
        if not external_file.exists():
            self.debugger.error("tasks", "External task file not found", path=str(external_file))
            return None
        
        try:
            # Load external task file
            with open(external_file, 'r') as f:
                external_config = yaml.safe_load(f)
            
            if not external_config:
                return None
            
            self.debugger.debug("tasks", "Loading external task", task=task_name, path=str(external_file))
            
            # External file can be a single task or a list of tasks
            if isinstance(external_config, dict):
                # Single task
                return self._execute_task(external_config, api_response, current_index, dry_run)
            elif isinstance(external_config, list):
                # Multiple tasks - execute all and return last result
                result = None
                for sub_task in external_config:
                    result = self._execute_task(sub_task, api_response, current_index, dry_run)
                return result
            
        except Exception as e:
            self.debugger.error("tasks", "External task execution failed", task=task_name, error=str(e))
            return None
