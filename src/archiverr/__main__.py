"""Archiverr - Config-Driven Media Organizer"""
import sys
import yaml
from pathlib import Path

from archiverr.core.plugin_system import (
    PluginDiscovery,
    PluginLoader,
    DependencyResolver,
    PluginExecutor
)
from archiverr.models import APIResponseBuilder
from archiverr.core.task_system import TemplateManager, TaskManager


def main():
    """Main entry point"""
    config_path = Path("config.yml")
    
    if not config_path.exists():
        print("ERROR: config.yml not found")
        sys.exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"ERROR: Failed to load config.yml: {e}")
        sys.exit(1)
    
    debug = config.get('options', {}).get('debug', False)
    dry_run = config.get('options', {}).get('dry_run', True)
    
    # Phase 1: Discover plugins
    discovery = PluginDiscovery()
    all_plugins = discovery.discover()
    
    if debug:
        print(f"Discovered {len(all_plugins)} plugins")
    
    # Phase 2: Load enabled plugins
    loader = PluginLoader(all_plugins, config)
    input_plugins = loader.load_by_category('input')
    output_plugins = loader.load_by_category('output')
    
    if debug:
        print(f"Loaded {len(input_plugins)} input plugins")
        print(f"Loaded {len(output_plugins)} output plugins")
    
    # Phase 3: Resolve dependencies
    resolver = DependencyResolver(all_plugins)
    enabled_output = list(output_plugins.keys())
    
    try:
        execution_groups = resolver.resolve(enabled_output)
        if debug:
            print(f"Execution groups: {execution_groups}")
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    # Phase 4: Execute input plugins
    executor = PluginExecutor()
    input_matches = executor.execute_input_plugins(input_plugins)
    
    if not input_matches:
        print("No matches found")
        sys.exit(0)
    
    print(f"Found {len(input_matches)} targets")
    
    # Phase 5: Execute output plugins and tasks for each match
    processed_matches = []
    all_task_results = []
    
    template_manager = TemplateManager()
    task_manager = TaskManager(config, template_manager)
    builder = APIResponseBuilder()
    
    for index, match in enumerate(input_matches):
        if debug:
            print(f"Processing match {index + 1}/{len(input_matches)}")
        
        # Execute output plugins
        result = executor.execute_output_pipeline(
            output_plugins,
            execution_groups,
            match
        )
        
        processed_matches.append(result)
        
        # Check if match is complete (all output plugins finished)
        status = result.get('status', {})
        success_plugins = status.get('success_plugins', [])
        failed_plugins = status.get('failed_plugins', [])
        not_supported_plugins = status.get('not_supported_plugins', [])
        total_plugins_run = len(success_plugins) + len(failed_plugins) + len(not_supported_plugins)
        
        # If all enabled output plugins finished, execute tasks for this match
        if total_plugins_run == len(output_plugins):
            # Build incremental API response for task execution
            temp_api_response = builder.build(processed_matches)
            
            # Add total_matches to globals for condition checking
            temp_api_response['globals']['total_matches'] = len(input_matches)
            temp_api_response['globals']['current_match'] = index
            
            # Execute tasks for this match
            task_results = task_manager.execute_tasks_for_match(
                temp_api_response,
                index,
                dry_run
            )
            all_task_results.extend(task_results)
    
    # Phase 6: Build final API response
    api_response = builder.build(processed_matches)
    
    # Update globals with task count
    api_response['globals']['status']['tasks'] = len(all_task_results)


if __name__ == "__main__":
    main()
