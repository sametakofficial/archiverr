"""
Safe parsers for FFProbe output values.

Industry-standard approach: Never use eval() on external tool output.
Use regex-based parsing with explicit validation.

References:
- FFmpeg-python: Uses regex parsing for frame rates
- PyAV: Uses fractions module for rational numbers
- moviepy: Uses manual string splitting with validation
"""
import re
from typing import Optional


def parse_fps(fps_str: str) -> float:
    """
    Parse FPS from FFProbe format safely without eval().
    
    FFProbe returns frame rate in formats:
    - Fraction: "24000/1001" (23.976 fps)
    - Fraction: "30/1" (30 fps)
    - Decimal: "29.97"
    - Integer: "24"
    
    Args:
        fps_str: Frame rate string from FFProbe
        
    Returns:
        Frame rate as float, 0.0 if invalid
        
    Examples:
        >>> parse_fps("24000/1001")
        23.976023976023978
        >>> parse_fps("30/1")
        30.0
        >>> parse_fps("29.97")
        29.97
        >>> parse_fps("0/0")
        0.0
        >>> parse_fps("invalid")
        0.0
    """
    if not fps_str:
        return 0.0
    
    fps_str = fps_str.strip()
    
    # Pattern 1: Fraction format "num/denom"
    fraction_match = re.match(r'^(\d+)/(\d+)$', fps_str)
    if fraction_match:
        try:
            numerator = float(fraction_match.group(1))
            denominator = float(fraction_match.group(2))
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
        except (ValueError, ZeroDivisionError):
            return 0.0
    
    # Pattern 2: Decimal or integer format
    try:
        return float(fps_str)
    except ValueError:
        return 0.0


def parse_duration(duration_str: str) -> float:
    """
    Parse duration from FFProbe output safely.
    
    Args:
        duration_str: Duration string from FFProbe (seconds as string)
        
    Returns:
        Duration in seconds as float, 0.0 if invalid
        
    Examples:
        >>> parse_duration("125.5")
        125.5
        >>> parse_duration("0")
        0.0
        >>> parse_duration("invalid")
        0.0
    """
    if not duration_str:
        return 0.0
    
    try:
        return float(duration_str)
    except ValueError:
        return 0.0


def parse_bitrate(bitrate_str: str) -> int:
    """
    Parse bitrate from FFProbe output safely.
    
    Args:
        bitrate_str: Bitrate string from FFProbe (bits per second)
        
    Returns:
        Bitrate as integer, 0 if invalid
        
    Examples:
        >>> parse_bitrate("8000000")
        8000000
        >>> parse_bitrate("0")
        0
        >>> parse_bitrate("invalid")
        0
    """
    if not bitrate_str:
        return 0
    
    try:
        return int(bitrate_str)
    except ValueError:
        return 0


def parse_int_safe(value_str: str, default: int = 0) -> int:
    """
    Parse integer safely with default fallback.
    
    Args:
        value_str: String to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed integer or default
    """
    if not value_str:
        return default
    
    try:
        return int(value_str)
    except ValueError:
        return default
