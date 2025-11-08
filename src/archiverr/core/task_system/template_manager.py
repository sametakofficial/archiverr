"""Template Manager - Jinja2 rendering with $ syntax"""
from jinja2 import Environment, BaseLoader
from typing import Dict, Any
import re


class TemplateManager:
    """Template manager using Jinja2 for variable resolution"""
    
    def __init__(self):
        self.env = Environment(loader=BaseLoader())
    
    def render(self, template: str, context: Dict[str, Any], current_index: int = 0) -> str:
        """
        Render template with context data.
        
        Variable resolution:
        - $tmdb.episode.name → context['items'][current_index]['tmdb']['episode']['name']
        - $100.tmdb.episode.name → context['items'][100]['tmdb']['episode']['name']
        - $globals → context['globals']
        - $matchGlobals → context['items'][current_index]['matchGlobals']
        
        Args:
            template: Jinja2 template string
            context: Full API response {globals, items}
            current_index: Current match index
            
        Returns:
            Rendered string
        """
        # Build template context
        items = context.get('items', [])
        
        if current_index >= len(items):
            return ""
        
        current_item = items[current_index]
        
        # Create Jinja2 context
        globals_data = context.get('globals', {})
        
        jinja_context = {
            'globals': globals_data,
            'matchGlobals': current_item.get('matchGlobals', {}),
            'index': current_index,
            'total': len(items)
        }
        
        # Add all plugin data from current item
        for key, value in current_item.items():
            if key not in ['index', 'matchGlobals']:
                jinja_context[key] = value
        
        # Add indexed access (for $100.tmdb.episode.name style)
        jinja_context['items'] = items
        
        try:
            # Convert $ prefix to Jinja2 syntax
            processed_template = self._process_dollar_syntax(template)
            
            tmpl = self.env.from_string(processed_template)
            return tmpl.render(**jinja_context)
        except Exception as e:
            return f"Template error: {e}"
    
    def _process_dollar_syntax(self, template: str) -> str:
        """
        Convert $ prefix to Jinja2 syntax.
        
        Examples:
        - $tmdb.episode.name → {{ tmdb.episode.name }}
        - $100.tmdb.episode.name → {{ items[100].tmdb.episode.name }}
        - $globals.status.matches → {{ globals.status.matches }}
        
        Args:
            template: Template with $ syntax
            
        Returns:
            Template with Jinja2 syntax
        """
        def replacer(match):
            var_path = match.group(1)
            
            # Check for indexed access ($100.tmdb.episode.name)
            if '.' in var_path:
                parts = var_path.split('.')
                first = parts[0]
                
                # If first part is a number, it's indexed access
                if first.isdigit():
                    index = first
                    remaining = '.'.join(parts[1:])
                    return f'{{{{ items[{index}].{remaining} }}}}'
            
            # Normal variable access
            return f'{{{{ {var_path} }}}}'
        
        # Pattern: $variable.path
        pattern = r'\$([a-zA-Z0-9_\.]+)'
        return re.sub(pattern, replacer, template)
    
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
            # Empty string or whitespace = False
            return bool(result.strip())
        except Exception:
            return False
