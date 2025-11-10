"""Template Manager - Jinja2 rendering with $ syntax and template functions"""
from jinja2 import Environment, BaseLoader
from typing import Dict, Any
import re


class TemplateManager:
    """
    Template manager using Jinja2 for variable resolution.
    
    Supports template functions:
    - index:$ - Current match index
    - count:matches - Total number of matches
    - count:path.to.data - Count elements in list at path
    """
    
    # Compile regex patterns once at class level for performance
    _FUNCTION_PATTERN = re.compile(r'\b(index|count):([a-zA-Z0-9_.\[\]]*)')
    _DOLLAR_PATTERN = re.compile(r'\$([a-zA-Z0-9_\.]+)')
    
    def __init__(self):
        self.env = Environment(loader=BaseLoader())
    
    def render(self, template: str, context: Dict[str, Any], current_index: int = 0) -> str:
        """
        Render template with context data.
        
        NEW Variable resolution (v2):
        - $tmdb.movie.title → match.plugins.tmdb.movie.title
        - $tmdb.globals.status → match.plugins.tmdb.globals.status
        - $globals.status → match.globals.status
        - $options.debug → match.options.debug
        - $tasks → match.tasks
        - $apiresponse.globals.summary → API root globals
        - $100.tmdb.movie → matches[100].plugins.tmdb.movie
        
        Smart routing:
        - Plugin name (tmdb, omdb, etc.) → match.plugins[plugin_name]
        - 'globals' → match.globals
        - 'options' → match.options
        - 'tasks' → match.tasks
        - 'apiresponse' → API root
        
        Args:
            template: Jinja2 template string
            context: Full API response {globals, matches}
            current_index: Current match index
            
        Returns:
            Rendered string
        """
        # Build template context
        matches = context.get('matches', [])
        
        if current_index >= len(matches):
            return ""
        
        current_match = matches[current_index]
        
        # Create Jinja2 context
        api_globals = context.get('globals', {})
        match_globals = current_match.get('globals', {})
        match_output = match_globals.get('output', {})
        match_plugins = current_match.get('plugins', {})
        
        # Get options from api_response.globals.config
        api_config = api_globals.get('config', {})
        global_options = api_config.get('options', {})
        
        jinja_context = {
            'apiresponse': context,  # Full API response
            'globals': match_globals,  # Current match globals
            'options': global_options,  # From api_response.globals.config.options
            'output': match_output,  # match.globals.output (tasks, validations, paths)
            'index': current_index,
            'total': len(matches),
            'matches': matches  # For indexed access
        }
        
        # Add all plugin data from current match (direct access)
        # $tmdb.movie → will be routed to match.plugins.tmdb.movie
        # $tmdb.globals → will be routed to match.plugins.tmdb.globals
        for plugin_name, plugin_data in match_plugins.items():
            jinja_context[plugin_name] = plugin_data
        
        try:
            # Process template functions first (index:$, count:)
            processed_template = self._process_functions(template, context, current_index)
            
            # Then convert $ prefix to Jinja2 syntax
            processed_template = self._process_dollar_syntax(processed_template)
            
            tmpl = self.env.from_string(processed_template)
            return tmpl.render(**jinja_context)
        except Exception as e:
            return f"Template error: {e}"
    
    def _process_functions(self, template: str, context: Dict[str, Any], current_index: int) -> str:
        """
        Process template functions and replace with actual values.
        
        Functions:
        - index: → current match index (0-based)
        - count:matches → total number of matches
        - count:path.to.data → count elements in list at path
        
        Examples:
        - "{{ index: }}" → "{{ 0 }}"
        - "{{ count:matches }}" → "{{ 2 }}"
        - "{{ count:tmdb.movie.genres }}" → "{{ 3 }}"
        - "{{ count:matches[0].tmdb.movie.people.cast }}" → "{{ 15 }}"
        
        Args:
            template: Template string with functions
            context: Full API response
            current_index: Current match index
            
        Returns:
            Template with functions replaced by values
        """
        def function_replacer(match):
            func_name = match.group(1)
            func_arg = match.group(2) if match.lastindex >= 2 else ''
            
            if func_name == 'index':
                # index: returns current index (no arg needed)
                return str(current_index)
            
            elif func_name == 'count':
                # count:matches returns total matches
                if func_arg == 'matches':
                    matches = context.get('matches', [])
                    return str(len(matches))
                
                # count:path.to.data returns element count at path
                try:
                    value = self._resolve_path(func_arg, context, current_index)
                    if isinstance(value, list):
                        return str(len(value))
                    elif isinstance(value, dict):
                        return str(len(value))
                    else:
                        return '0'
                except Exception:
                    return '0'
            
            return match.group(0)  # Unknown function, keep original
        
        # Use pre-compiled pattern for performance
        # Pattern matches: index:, count:matches, count:tmdb.movie.genres, count:matches[0].data
        # Note: index: has no arg (optional group), count: requires arg
        return self._FUNCTION_PATTERN.sub(function_replacer, template)
    
    def _resolve_path(self, path: str, context: Dict[str, Any], current_index: int) -> Any:
        """
        Resolve a path to data in context.
        
        Paths:
        - $.field → context['matches'][current_index]['field']
        - matches[0].field → context['matches'][0]['field']
        - field.subfield → context['matches'][current_index]['field']['subfield']
        
        Args:
            path: Path to resolve
            context: Full API response
            current_index: Current match index
            
        Returns:
            Value at path
        """
        matches = context.get('matches', [])
        
        # Replace $ with current match reference
        if path.startswith('$.'):
            path = path[2:]  # Remove $.
            if current_index >= len(matches):
                return None
            current_data = matches[current_index]
        elif path.startswith('matches['):
            # Handle matches[N].path
            idx_end = path.index(']')
            idx = int(path[8:idx_end])
            if idx >= len(matches):
                return None
            current_data = matches[idx]
            path = path[idx_end + 2:] if idx_end + 1 < len(path) and path[idx_end + 1] == '.' else ''
        else:
            # No prefix, assume current match
            if current_index >= len(matches):
                return None
            current_data = matches[current_index]
        
        # Navigate path
        if not path:
            return current_data
        
        parts = path.split('.')
        for part in parts:
            if isinstance(current_data, dict):
                current_data = current_data.get(part)
                if current_data is None:
                    return None
            else:
                return None
        
        return current_data
    
    def _process_dollar_syntax(self, template: str) -> str:
        """
        Convert $ prefix to Jinja2 syntax with smart routing.
        
        Smart routing logic:
        - $apiresponse.globals.summary → {{ apiresponse.globals.summary }}
        - $globals.status → {{ globals.status }} (match globals)
        - $tmdb.movie.title → {{ tmdb.movie.title }} (plugin data)
        - $100.tmdb.movie → {{ matches[100].plugins.tmdb.movie }}
        - $100.globals.status → {{ matches[100].globals.status }}
        
        Args:
            template: Template with $ syntax
            
        Returns:
            Template with Jinja2 syntax
        """
        def replacer(match):
            var_path = match.group(1)
            
            # Check for indexed access ($100.tmdb.movie)
            if '.' in var_path:
                parts = var_path.split('.')
                first = parts[0]
                
                # Indexed access: $100.tmdb.movie
                if first.isdigit():
                    index = first
                    second = parts[1] if len(parts) > 1 else ''
                    remaining = '.'.join(parts[2:]) if len(parts) > 2 else ''
                    
                    # Route based on second part
                    if second == 'globals':
                        # $100.globals.status → matches[100].globals.status
                        path = f'matches[{index}].globals'
                        if remaining:
                            path += f'.{remaining}'
                        return f'{{{{ {path} }}}}'
                    else:
                        # $100.tmdb.movie → matches[100].plugins.tmdb.movie
                        path = f'matches[{index}].plugins.{second}'
                        if remaining:
                            path += f'.{remaining}'
                        return f'{{{{ {path} }}}}'
                
                # Current match access: $tmdb.movie or $globals.status or $apiresponse.globals
                # Already routed in jinja_context, just pass through
                # - $globals → globals (match.globals)
                # - $tmdb → tmdb (match.plugins.tmdb)
                # - $apiresponse → apiresponse (full API response)
            
            # Normal variable access (no routing needed, context already set up)
            return f'{{{{ {var_path} }}}}'
        
        # Use pre-compiled pattern for performance
        return self._DOLLAR_PATTERN.sub(replacer, template)
    
    def evaluate_condition(self, condition: str, context: Dict[str, Any], current_index: int = 0) -> bool:
        """
        Evaluate Jinja2 condition.
        
        Args:
            condition: Jinja2 condition string
            context: Full API response
            current_index: Current match index
            
        Returns:
            True if condition passes
        """
        if not condition:
            return True
        
        try:
            # Render condition as template
            result = self.render(condition, context, current_index)
            # If template error occurred, condition fails
            if result.startswith("Template error:"):
                return False
            # Empty string or whitespace = False
            return bool(result.strip())
        except Exception:
            return False
