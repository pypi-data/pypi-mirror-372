"""
Constraint solving system for mathematical diagrams

This module provides mathematical constraint solving to ensure
diagram validity and geometric relationships.
"""

import numpy as np
import math
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Constraint:
    """Represents a mathematical constraint"""
    constraint_type: str
    elements: List[str]
    parameters: Dict[str, Any]
    tolerance: float = 1e-6

class ConstraintSolver:
    """Solves mathematical constraints for diagram generation"""
    
    def __init__(self):
        self.constraints = []
        self.variables = {}
        
    def add_constraint(self, constraint: Constraint):
        """Add a constraint to the solver"""
        self.constraints.append(constraint)
        
    def solve_tangent_to_circle(self, circle_center: Tuple[float, float], 
                               radius: float, 
                               external_point: Tuple[float, float]) -> List[Tuple[float, float]]:
        """
        Solve for tangent points from external point to circle
        
        Returns the two tangent points where lines from external_point 
        are tangent to the circle.
        """
        cx, cy = circle_center
        px, py = external_point
        
        # Distance from external point to center
        d = math.sqrt((px - cx)**2 + (py - cy)**2)
        
        if d <= radius:
            raise ValueError("Point must be external to circle")
            
        # Length of tangent line
        tangent_length = math.sqrt(d**2 - radius**2)
        
        # Angle from center to external point
        angle_to_point = math.atan2(py - cy, px - cx)
        
        # Angle between radius to tangent point and line to external point
        tangent_angle = math.asin(radius / d)
        
        # Two tangent points
        angle1 = angle_to_point + tangent_angle
        angle2 = angle_to_point - tangent_angle
        
        tangent1 = (cx + radius * math.cos(angle1), cy + radius * math.sin(angle1))
        tangent2 = (cx + radius * math.cos(angle2), cy + radius * math.sin(angle2))
        
        return [tangent1, tangent2]
    
    def solve_triangle_height(self, base: float, angle_degrees: float) -> float:
        """
        Solve for triangle height given base and angle
        
        Uses trigonometry: height = base * tan(angle)
        """
        angle_rad = math.radians(angle_degrees)
        return base * math.tan(angle_rad)
    
    def solve_right_triangle_missing_side(self, known_sides: Dict[str, float], 
                                         missing_side: str) -> float:
        """
        Solve for missing side in right triangle using Pythagorean theorem
        
        Args:
            known_sides: Dict with keys 'a', 'b', 'c' for triangle sides
            missing_side: Which side to solve for ('a', 'b', or 'c')
        """
        if missing_side == 'c':  # hypotenuse
            a, b = known_sides.get('a', 0), known_sides.get('b', 0)
            return math.sqrt(a**2 + b**2)
        elif missing_side == 'a':
            b, c = known_sides.get('b', 0), known_sides.get('c', 0)
            return math.sqrt(c**2 - b**2)
        elif missing_side == 'b':
            a, c = known_sides.get('a', 0), known_sides.get('c', 0)
            return math.sqrt(c**2 - a**2)
        else:
            raise ValueError(f"Unknown side: {missing_side}")
    
    def validate_triangle(self, vertices: List[Tuple[float, float]]) -> bool:
        """
        Validate that three points form a valid triangle
        
        Checks that points are not collinear and triangle inequality holds
        """
        if len(vertices) != 3:
            return False
            
        (x1, y1), (x2, y2), (x3, y3) = vertices
        
        # Check if points are collinear using cross product
        cross_product = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
        if abs(cross_product) < 1e-10:
            return False
            
        # Calculate side lengths
        a = math.sqrt((x2 - x3)**2 + (y2 - y3)**2)
        b = math.sqrt((x1 - x3)**2 + (y1 - y3)**2) 
        c = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        
        # Check triangle inequality
        return (a + b > c) and (a + c > b) and (b + c > a)
    
    def solve_circle_through_points(self, points: List[Tuple[float, float]]) -> Tuple[Tuple[float, float], float]:
        """
        Find circle passing through three points
        
        Returns (center, radius) of circumcircle
        """
        if len(points) != 3:
            raise ValueError("Need exactly 3 points")
            
        (x1, y1), (x2, y2), (x3, y3) = points
        
        # Calculate circumcenter using determinants
        d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        
        if abs(d) < 1e-10:
            raise ValueError("Points are collinear")
            
        ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / d
        uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / d
        
        center = (ux, uy)
        radius = math.sqrt((ux - x1)**2 + (uy - y1)**2)
        
        return center, radius
    
    def solve_line_intersection(self, line1: Dict[str, float], line2: Dict[str, float]) -> Optional[Tuple[float, float]]:
        """
        Find intersection point of two lines
        
        Lines defined as: ax + by + c = 0
        """
        a1, b1, c1 = line1.get('a', 0), line1.get('b', 0), line1.get('c', 0)
        a2, b2, c2 = line2.get('a', 0), line2.get('b', 0), line2.get('c', 0)
        
        det = a1 * b2 - a2 * b1
        
        if abs(det) < 1e-10:
            return None  # Lines are parallel
            
        x = (b1 * c2 - b2 * c1) / det
        y = (a2 * c1 - a1 * c2) / det
        
        return (x, y)
    
    def check_perpendicular(self, line1_points: List[Tuple[float, float]], 
                           line2_points: List[Tuple[float, float]]) -> bool:
        """
        Check if two lines are perpendicular
        
        Each line defined by two points
        """
        if len(line1_points) != 2 or len(line2_points) != 2:
            return False
            
        # Calculate direction vectors
        (x1, y1), (x2, y2) = line1_points
        (x3, y3), (x4, y4) = line2_points
        
        v1 = (x2 - x1, y2 - y1)
        v2 = (x4 - x3, y4 - y3)
        
        # Check if dot product is zero (perpendicular)
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        
        return abs(dot_product) < 1e-6
    
    def check_parallel(self, line1_points: List[Tuple[float, float]], 
                      line2_points: List[Tuple[float, float]]) -> bool:
        """
        Check if two lines are parallel
        
        Each line defined by two points
        """
        if len(line1_points) != 2 or len(line2_points) != 2:
            return False
            
        # Calculate direction vectors
        (x1, y1), (x2, y2) = line1_points
        (x3, y3), (x4, y4) = line2_points
        
        v1 = (x2 - x1, y2 - y1)
        v2 = (x4 - x3, y4 - y3)
        
        # Check if cross product is zero (parallel)
        cross_product = v1[0] * v2[1] - v1[1] * v2[0]
        
        return abs(cross_product) < 1e-6
    
    def validate_tangent_to_circle(self, circle_center: Tuple[float, float],
                                  radius: float,
                                  tangent_line_points: List[Tuple[float, float]]) -> bool:
        """
        Validate that a line is tangent to a circle
        
        Checks that distance from circle center to line equals radius
        """
        if len(tangent_line_points) != 2:
            return False
            
        (x1, y1), (x2, y2) = tangent_line_points
        cx, cy = circle_center
        
        # Distance from point to line formula
        # Line: (y2-y1)x - (x2-x1)y + (x2-x1)y1 - (y2-y1)x1 = 0
        a = y2 - y1
        b = -(x2 - x1)  
        c = (x2 - x1) * y1 - (y2 - y1) * x1
        
        distance = abs(a * cx + b * cy + c) / math.sqrt(a**2 + b**2)
        
        return abs(distance - radius) < 1e-6
    
    def solve_system(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve the complete constraint system
        
        This is a simplified solver that handles common geometric constraints
        """
        solved_params = parameters.copy()
        
        for constraint in self.constraints:
            if constraint.constraint_type == "tangent_to_circle":
                # Handle tangent constraints
                if all(param in solved_params for param in ["circle_center", "radius", "external_point"]):
                    tangent_points = self.solve_tangent_to_circle(
                        solved_params["circle_center"],
                        solved_params["radius"], 
                        solved_params["external_point"]
                    )
                    solved_params["tangent_points"] = tangent_points
                    
            elif constraint.constraint_type == "triangle_height":
                # Handle height calculation
                if "base" in solved_params and "angle_degrees" in solved_params:
                    height = self.solve_triangle_height(
                        solved_params["base"],
                        solved_params["angle_degrees"]
                    )
                    solved_params["height"] = height
                    
        return solved_params
    
    def clear_constraints(self):
        """Clear all constraints"""
        self.constraints.clear()
        self.variables.clear()