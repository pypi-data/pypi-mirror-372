"""
Number formatting utilities with explicit sign display.

This module provides functions to format numbers with explicit positive/negative signs
and specified decimal places. Non-numeric values are returned as-is.
"""

import math
from typing import Union, Any


def format_number_with_sign(value: Union[float, int, Any], decimal_digits: int) -> Union[str, Any]:
    """
    Format number with explicit sign and specified decimal places.
    Non-numeric values are returned as-is.
    
    Args:
        value: The value to format (number or any other type)
        decimal_digits: Number of decimal places to display
        
    Returns:
        Formatted string with explicit + or - sign for numbers,
        original value unchanged for non-numeric inputs
        
    Examples:
        >>> format_number_with_sign(1.1234, 2)
        '+1.12'
        >>> format_number_with_sign(-1.1234, 2)
        '-1.12'
        >>> format_number_with_sign(3.1, 2)
        '+3.10'
        >>> format_number_with_sign(0, 2)
        '+0.00'
        >>> format_number_with_sign('N/A', 2)
        'N/A'
        >>> format_number_with_sign(None, 2)
        None
        >>> format_number_with_sign(float('nan'), 2)
        nan
    """
    if value is None:
        return None
    
    try:
        num_value = float(value)
        
        if math.isnan(num_value) or math.isinf(num_value):
            return value
        
        return f"{num_value:+.{decimal_digits}f}" if isinstance(decimal_digits, int) else f"{num_value:+f}"
        
    except (ValueError, TypeError):
        return value


map_number_to_signed_string = format_number_with_sign


def parse_signed_string_to_number(value: Union[str, Any]) -> Union[float, Any]:
    """Parse signed string back to numeric value"""
    if value is None:
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if not isinstance(value, str):
        return value
    
    try:
        return float(value)  # "+1.23" -> 1.23
    except ValueError:
        return value


map_signed_string_to_number = parse_signed_string_to_number


__all__ = ['format_number_with_sign', 'map_number_to_signed_string', 'parse_signed_string_to_number', 'map_signed_string_to_number']