"""
Utility functions for MathDiagram library
"""

import os
import math
from pathlib import Path
from typing import Dict, Any, List, Tuple

def validate_parameters(parameters: Dict[str, Any], 
                       parameter_ranges: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate and clamp parameters to their allowed ranges
    
    Args:
        parameters: Dictionary of parameter values
        parameter_ranges: Dictionary defining allowed ranges for each parameter
        
    Returns:
        Dict of validated parameters
        
    Raises:
        ValueError: If parameter is outside acceptable range
    """
    validated = parameters.copy()
    
    for param_name, value in parameters.items():
        if param_name in parameter_ranges:
            range_info = parameter_ranges[param_name]
            
            # Check minimum value
            if "min" in range_info and value < range_info["min"]:
                raise ValueError(f"Parameter {param_name}={value} below minimum {range_info['min']}")
                
            # Check maximum value  
            if "max" in range_info and value > range_info["max"]:
                raise ValueError(f"Parameter {param_name}={value} above maximum {range_info['max']}")
                
            # Type conversion if needed
            param_type = range_info.get("type", "float")
            if param_type == "int":
                validated[param_name] = int(value)
            elif param_type == "float":
                validated[param_name] = float(value)
                
    return validated

def ensure_output_dir(directory: str):
    """
    Ensure output directory exists, create if needed
    
    Args:
        directory: Path to directory
    """
    Path(directory).mkdir(parents=True, exist_ok=True)

def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
        
    Returns:
        Distance between points
    """
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def angle_between_vectors(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    """
    Calculate angle between two vectors in radians
    
    Args:
        v1: First vector (x, y)
        v2: Second vector (x, y)
        
    Returns:
        Angle in radians
    """
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    
    if mag1 == 0 or mag2 == 0:
        return 0
        
    cos_angle = dot_product / (mag1 * mag2)
    # Clamp to avoid numerical errors
    cos_angle = max(-1, min(1, cos_angle))
    
    return math.acos(cos_angle)

def normalize_vector(vector: Tuple[float, float]) -> Tuple[float, float]:
    """
    Normalize a vector to unit length
    
    Args:
        vector: Vector (x, y)
        
    Returns:
        Normalized vector
    """
    x, y = vector
    magnitude = math.sqrt(x**2 + y**2)
    
    if magnitude == 0:
        return (0, 0)
        
    return (x / magnitude, y / magnitude)

def rotate_point(point: Tuple[float, float], 
                center: Tuple[float, float], 
                angle_radians: float) -> Tuple[float, float]:
    """
    Rotate a point around a center by given angle
    
    Args:
        point: Point to rotate (x, y)
        center: Center of rotation (x, y) 
        angle_radians: Rotation angle in radians
        
    Returns:
        Rotated point
    """
    px, py = point
    cx, cy = center
    
    # Translate to origin
    x = px - cx
    y = py - cy
    
    # Rotate
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    
    x_new = x * cos_a - y * sin_a
    y_new = x * sin_a + y * cos_a
    
    # Translate back
    return (x_new + cx, y_new + cy)

def point_on_line(point1: Tuple[float, float], 
                 point2: Tuple[float, float], 
                 t: float) -> Tuple[float, float]:
    """
    Get point on line segment at parameter t (0 = point1, 1 = point2)
    
    Args:
        point1: Start point (x, y)
        point2: End point (x, y)
        t: Parameter [0, 1]
        
    Returns:
        Point on line
    """
    x1, y1 = point1
    x2, y2 = point2
    
    x = x1 + t * (x2 - x1)
    y = y1 + t * (y2 - y1)
    
    return (x, y)

def line_from_points(point1: Tuple[float, float], 
                    point2: Tuple[float, float]) -> Dict[str, float]:
    """
    Get line equation coefficients from two points
    
    Returns line in form ax + by + c = 0
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
        
    Returns:
        Dict with keys 'a', 'b', 'c' for line equation
    """
    x1, y1 = point1
    x2, y2 = point2
    
    # Line equation: (y2-y1)x - (x2-x1)y + (x2-x1)y1 - (y2-y1)x1 = 0
    a = y2 - y1
    b = -(x2 - x1)
    c = (x2 - x1) * y1 - (y2 - y1) * x1
    
    return {"a": a, "b": b, "c": c}

def distance_point_to_line(point: Tuple[float, float], 
                          line_coeffs: Dict[str, float]) -> float:
    """
    Calculate distance from point to line
    
    Args:
        point: Point (x, y)
        line_coeffs: Line coefficients {'a': a, 'b': b, 'c': c} for ax + by + c = 0
        
    Returns:
        Distance from point to line
    """
    x, y = point
    a, b, c = line_coeffs["a"], line_coeffs["b"], line_coeffs["c"]
    
    return abs(a * x + b * y + c) / math.sqrt(a**2 + b**2)

def is_point_on_circle(point: Tuple[float, float], 
                      center: Tuple[float, float], 
                      radius: float, 
                      tolerance: float = 1e-6) -> bool:
    """
    Check if point lies on circle
    
    Args:
        point: Point to check (x, y)
        center: Circle center (x, y)
        radius: Circle radius
        tolerance: Numerical tolerance
        
    Returns:
        True if point is on circle
    """
    distance = calculate_distance(point, center)
    return abs(distance - radius) < tolerance

def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """
    Safe division with default value for zero denominator
    
    Args:
        numerator: Numerator value
        denominator: Denominator value  
        default: Value to return if denominator is zero
        
    Returns:
        Division result or default
    """
    if abs(denominator) < 1e-10:
        return default
    return numerator / denominator

def format_number(value: float, decimal_places: int = 2) -> str:
    """
    Format number for display with specified decimal places
    
    Args:
        value: Number to format
        decimal_places: Number of decimal places
        
    Returns:
        Formatted string
    """
    return f"{value:.{decimal_places}f}"

def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians"""
    return degrees * math.pi / 180

def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees"""
    return radians * 180 / math.pi

def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp value to range [min_value, max_value]
    
    Args:
        value: Value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Clamped value
    """
    return max(min_value, min(value, max_value))