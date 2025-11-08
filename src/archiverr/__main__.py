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
from archiverr.utils.debug import init_debugger, get_debugger


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
    
    # Initialize debug system
    debugger = init_debugger(enabled=debug)
    debugger.info("system", "Archiverr starting", debug=debug, dry_run=dry_run)
    
    # Phase 1: Discover plugins
    debugger.debug("system", "Starting plugin discovery")
    discovery = PluginDiscovery()
    all_plugins = discovery.discover()
    debugger.info("discovery", "Plugin discovery complete", total=len(all_plugins))
    
    # Phase 2: Load enabled plugins
    debugger.debug("system", "Loading enabled plugins")
    loader = PluginLoader(all_plugins, config)
    input_plugins = loader.load_by_category('input')
    output_plugins = loader.load_by_category('output')
    debugger.info("loader", "Plugins loaded", input=len(input_plugins), output=len(output_plugins))
    
    # Phase 3: Resolve dependencies
    debugger.debug("system", "Resolving dependencies")
    resolver = DependencyResolver(all_plugins)
    enabled_output = list(output_plugins.keys())
    
    try:
        execution_groups = resolver.resolve(enabled_output)
        debugger.info("resolver", "Dependency resolution complete", groups=len(execution_groups))
        for i, group in enumerate(execution_groups):
            debugger.debug("resolver", f"Group {i}", plugins=", ".join(group))
    except ValueError as e:
        debugger.error("resolver", "Dependency resolution failed", error=str(e))
        print(f"ERROR: {e}")
        sys.exit(1)
    
    # Phase 4: Execute input plugins
    debugger.debug("system", "Executing input plugins")
    executor = PluginExecutor()
    input_matches = executor.execute_input_plugins(input_plugins)
    
    if not input_matches:
        debugger.warn("executor", "No matches found")
        print("No matches found")
        sys.exit(0)
    
    debugger.info("executor", "Input plugins complete", matches=len(input_matches))
    print(f"Found {len(input_matches)} targets")
    
    # Phase 5: Execute output plugins and tasks for each match
    processed_matches = []
    all_task_results = []
    
    template_manager = TemplateManager()
    task_manager = TaskManager(config, template_manager)
    builder = APIResponseBuilder()
    
    debugger.debug("system", "Starting per-match processing")
    for index, match in enumerate(input_matches):
        debugger.info("executor", f"Processing match {index + 1}/{len(input_matches)}")
        
        # Execute output plugins with expectations checking
        result = executor.execute_output_pipeline(
            output_plugins,
            execution_groups,
            match,
            resolver  # Pass resolver for expectations validation
        )
        
        processed_matches.append(result)
        
        # Check if match is complete (all output plugins finished)
        status = result.get('status', {})
        success_plugins = status.get('success_plugins', [])
        failed_plugins = status.get('failed_plugins', [])
        not_supported_plugins = status.get('not_supported_plugins', [])
        total_plugins_run = len(success_plugins) + len(failed_plugins) + len(not_supported_plugins)
        
        debugger.debug("executor", f"Match {index} complete", 
                      success=len(success_plugins),
                      failed=len(failed_plugins),
                      not_supported=len(not_supported_plugins))
        
        # If all enabled output plugins finished, execute tasks for this match
        if total_plugins_run == len(output_plugins):
            # Build incremental API response for task execution
            temp_api_response = builder.build(processed_matches)
            
            # Add total_matches to globals for condition checking
            temp_api_response['globals']['total_matches'] = len(input_matches)
            temp_api_response['globals']['current_match'] = index
            
            # Execute tasks for this match
            debugger.debug("tasks", f"Executing tasks for match {index}")
            task_results = task_manager.execute_tasks_for_match(
                temp_api_response,
                index,
                dry_run
            )
            all_task_results.extend(task_results)
            debugger.debug("tasks", f"Tasks complete for match {index}", executed=len(task_results))
    
    # Phase 6: Build final API response
    debugger.debug("system", "Building final API response")
    api_response = builder.build(processed_matches)
    
    # Update globals with task count
    api_response['globals']['status']['tasks'] = len(all_task_results)
    
    debugger.info("system", "Archiverr complete", 
                 matches=len(processed_matches),
                 tasks=len(all_task_results),
                 errors=api_response['globals']['status']['errors'])


if __name__ == "__main__":
    main()
