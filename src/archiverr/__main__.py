"""Archiverr - Config-Driven Media Organizer"""
import sys
import yaml
from pathlib import Path
from datetime import datetime

from archiverr.core.plugins import (
    PluginDiscovery,
    PluginLoader,
    DependencyResolver,
    PluginExecutor
)
from archiverr.models import APIResponseBuilder
from archiverr.core.tasks import TemplateManager, TaskManager
from archiverr.core.reports import generate_dual_reports
from archiverr.utils.debug import init_debugger, get_debugger
from archiverr.core.config_validator import ConfigValidator


def main():
    """Main entry point"""
    # Record start time (single timestamp for entire execution)
    start_time = datetime.now()
    
    config_path = Path("config.yml")
    
    if not config_path.exists():
        print("ERROR: config.yml not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        # Pre-debug error - use print
        print(f"ERROR: Failed to load config.yml: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Initialize debug system
    debug = config.get('options', {}).get('debug', False)
    dry_run = config.get('options', {}).get('dry_run', True)
    debugger = init_debugger(enabled=debug)
    
    # Validate config structure
    validator = ConfigValidator()
    if validator.is_available():
        is_valid, error_msg = validator.validate(config)
        if not is_valid:
            debugger.error("config", "Invalid configuration", error=error_msg)
            sys.exit(1)
        debugger.debug("config", "Configuration validated")
    else:
        debugger.debug("config", "Schema validation unavailable (jsonschema not installed)")
    
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
        sys.exit(1)
    
    # Phase 4: Execute input plugins
    debugger.debug("system", "Executing input plugins")
    executor = PluginExecutor()
    input_matches = executor.execute_input_plugins(input_plugins)
    
    if not input_matches:
        debugger.warn("executor", "No matches found")
        sys.exit(0)
    
    debugger.info("executor", "Input plugins complete", matches=len(input_matches))
    
    # Phase 5: Execute output plugins and tasks for each match
    processed_matches = []
    all_task_results = []
    match_task_results = {}  # Track task results per match {index: [results]}
    
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
            temp_api_response = builder.build(
                processed_matches,
                config=config,
                start_time=start_time,
                loaded_plugins=all_plugins
            )
            
            # Execute tasks for this match
            debugger.debug("tasks", f"Executing tasks for match {index}")
            task_results = task_manager.execute_tasks_for_match(
                temp_api_response,
                index,
                dry_run
            )
            all_task_results.extend(task_results)
            match_task_results[index] = task_results
            debugger.debug("tasks", f"Tasks complete for match {index}", executed=len(task_results))
    
    # Phase 6: Build final API response
    debugger.debug("system", "Building final API response")
    api_response = builder.build(
        processed_matches,
        config=config,
        start_time=start_time,
        loaded_plugins=all_plugins
    )
    
    # Phase 6.1: Add task results to match.globals.output.tasks
    for match_index, task_results_list in match_task_results.items():
        if match_index < len(api_response['matches']):
            match = api_response['matches'][match_index]
            match_output = match.get('globals', {}).get('output', {})
            
            # Format task results for storage
            formatted_tasks = []
            
            for task_result in task_results_list:
                task_entry = {
                    'name': task_result.get('task_name'),
                    'type': task_result.get('type'),
                    'success': task_result.get('success', True)
                }
                
                # Add type-specific fields
                if task_result.get('type') == 'print':
                    task_entry['rendered'] = task_result.get('output')
                elif task_result.get('type') == 'save':
                    task_entry['destination'] = task_result.get('destination')
                
                formatted_tasks.append(task_entry)
            
            # Update match.globals.output.tasks (NO paths - redundant)
            match_output['tasks'] = formatted_tasks
    
    # Update globals with task count
    api_response['globals']['status']['tasks'] = len(all_task_results)
    
    # Phase 7: Generate dual reports (full + compact + debug log)
    debugger.debug("system", "Generating API response reports")
    timestamp = start_time.strftime("%Y%m%d_%H%M%S")
    report_paths = generate_dual_reports(api_response, timestamp, debugger=debugger)
    
    # Log report paths
    debugger.debug("system", "Reports generated", 
                  full=report_paths['full'], 
                  compact=report_paths['compact'],
                  debug_log=report_paths.get('debug_log', 'N/A'))
    
    debugger.info("system", "Archiverr complete", 
                 matches=len(processed_matches),
                 tasks=len(all_task_results),
                 errors=api_response['globals']['status']['errors'])


if __name__ == "__main__":
    main()
