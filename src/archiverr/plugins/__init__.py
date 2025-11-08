"""
Plugins package.
All plugins (scanner, ffprobe, tmdb, etc.) live here.
"""
from .base import BasePlugin, InputPlugin, OutputPlugin

__all__ = ['BasePlugin', 'InputPlugin', 'OutputPlugin']
