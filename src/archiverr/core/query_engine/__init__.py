# engine/__init__.py
"""
YML Engine - Gelişmiş değişken, pattern ve query motoru.

API Response + FFprobe + Global değişkenlerden pattern rendering ve query execution.
"""
from .engine import YMLEngine
from .variables import build_variable_context
from .variable_engine import render_template, execute_query

__all__ = ['YMLEngine', 'build_variable_context', 'render_template', 'execute_query']
