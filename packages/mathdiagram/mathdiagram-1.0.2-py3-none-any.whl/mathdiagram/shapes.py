"""
Shape generation utilities for mathematical diagrams
"""

import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.patches import Circle, Rectangle, Polygon, Arc, Ellipse, Wedge
from matplotlib.collections import LineCollection
from typing import Dict, List, Any, Tuple, Optional, Union

from .config import DiagramConfig

class ShapeGenerator:
    """Generates geometric shapes with mathematical precision"""
    
    def __init__(self, ax: plt.Axes, config: DiagramConfig):
        self.ax = ax
        self.config = config
        self.shapes = {}
        self._shape_id = 0
        
    def create_circle(self, center: Tuple[float, float], radius: float, 
                     style: Dict[str, Any] = None, label: str = None) -> Circle:
        """
        Create a circle
        
        Args:
            center: (x, y) center coordinates
            radius: Circle radius
            style: matplotlib styling options
            label: Optional label for legend
            
        Returns:
            Circle: matplotlib Circle patch
        """
        style = style or {'fill': False, 'color': 'blue', 'linewidth': 2}
        
        circle = Circle(center, radius, label=label, **style)
        self.ax.add_patch(circle)
        
        shape_id = f"circle_{self._shape_id}"
        self.shapes[shape_id] = {
            'type': 'circle',
            'object': circle,
            'center': center,
            'radius': radius
        }
        self._shape_id += 1
        
        return circle
    
    def create_triangle(self, vertices: List[Tuple[float, float]], 
                       style: Dict[str, Any] = None, label: str = None) -> Polygon:
        """Create a triangle from three vertices"""
        style = style or {'fill': False, 'edgecolor': 'blue', 'linewidth': 2}
        
        triangle = Polygon(vertices, label=label, **style)
        self.ax.add_patch(triangle)
        
        shape_id = f"triangle_{self._shape_id}"
        self.shapes[shape_id] = {
            'type': 'triangle',
            'object': triangle,
            'vertices': vertices
        }
        self._shape_id += 1
        
        return triangle
    
    def create_line(self, start: Tuple[float, float], end: Tuple[float, float],
                   style: Dict[str, Any] = None, label: str = None):
        """Create a line segment"""
        style = style or {'color': 'blue', 'linewidth': 2}
        
        line = self.ax.plot([start[0], end[0]], [start[1], end[1]], 
                           label=label, **style)[0]
        
        shape_id = f"line_{self._shape_id}"
        self.shapes[shape_id] = {
            'type': 'line',
            'object': line,
            'start': start,
            'end': end
        }
        self._shape_id += 1
        
        return line
    
    def create_point(self, position: Tuple[float, float], 
                    style: Dict[str, Any] = None, label: str = None):
        """Create a point"""
        style = style or {'color': 'red', 'markersize': 8, 'marker': 'o'}
        
        point = self.ax.plot(position[0], position[1], label=label, **style)[0]
        
        shape_id = f"point_{self._shape_id}"
        self.shapes[shape_id] = {
            'type': 'point',
            'object': point,
            'position': position
        }
        self._shape_id += 1
        
        return point
    
    def create_angle(self, vertex: Tuple[float, float], 
                    point1: Tuple[float, float], 
                    point2: Tuple[float, float], 
                    radius: float = 1, 
                    style: Dict[str, Any] = None,
                    label: str = None) -> Wedge:
        """Create an angle marking"""
        # Calculate angle
        v1 = np.array(point1) - np.array(vertex)
        v2 = np.array(point2) - np.array(vertex)
        
        angle1 = math.atan2(v1[1], v1[0])
        angle2 = math.atan2(v2[1], v2[0])
        
        # Ensure positive angle
        if angle2 < angle1:
            angle2 += 2 * math.pi
            
        style = style or {'facecolor': 'yellow', 'alpha': 0.3, 'edgecolor': 'orange'}
        
        wedge = Wedge(vertex, radius, math.degrees(angle1), math.degrees(angle2), 
                     label=label, **style)
        self.ax.add_patch(wedge)
        
        shape_id = f"angle_{self._shape_id}"
        self.shapes[shape_id] = {
            'type': 'angle',
            'object': wedge,
            'vertex': vertex,
            'point1': point1,
            'point2': point2,
            'angle_degrees': math.degrees(angle2 - angle1)
        }
        self._shape_id += 1
        
        return wedge
    
    def create_rectangle(self, bottom_left: Tuple[float, float], 
                        width: float, height: float,
                        style: Dict[str, Any] = None, label: str = None) -> Rectangle:
        """Create a rectangle"""
        style = style or {'fill': False, 'color': 'blue', 'linewidth': 2}
        
        rect = Rectangle(bottom_left, width, height, label=label, **style)
        self.ax.add_patch(rect)
        
        shape_id = f"rectangle_{self._shape_id}"
        self.shapes[shape_id] = {
            'type': 'rectangle',
            'object': rect,
            'bottom_left': bottom_left,
            'width': width,
            'height': height
        }
        self._shape_id += 1
        
        return rect
    
    def create_function_plot(self, func, x_range: Tuple[float, float], 
                           num_points: int = 1000, 
                           style: Dict[str, Any] = None, label: str = None):
        """Create a function plot"""
        x = np.linspace(x_range[0], x_range[1], num_points)
        
        try:
            if callable(func):
                y = func(x)
            elif isinstance(func, str):
                # Simple function parser
                y = eval(func.replace('x', 'x'))
            else:
                raise ValueError("Function must be callable or string expression")
                
            style = style or {'color': 'blue', 'linewidth': 2}
            line = self.ax.plot(x, y, label=label, **style)[0]
            
            shape_id = f"function_{self._shape_id}"
            self.shapes[shape_id] = {
                'type': 'function',
                'object': line,
                'function': func,
                'x_range': x_range
            }
            self._shape_id += 1
            
            return line
            
        except Exception as e:
            print(f"Error plotting function: {e}")
            return None
    
    def create_polygon(self, vertices: List[Tuple[float, float]],
                      style: Dict[str, Any] = None, label: str = None) -> Polygon:
        """Create a general polygon"""
        style = style or {'fill': False, 'edgecolor': 'blue', 'linewidth': 2}
        
        polygon = Polygon(vertices, label=label, **style)
        self.ax.add_patch(polygon)
        
        shape_id = f"polygon_{self._shape_id}"
        self.shapes[shape_id] = {
            'type': 'polygon',
            'object': polygon,
            'vertices': vertices
        }
        self._shape_id += 1
        
        return polygon
    
    def create_arc(self, center: Tuple[float, float], radius: float,
                  start_angle: float, end_angle: float,
                  style: Dict[str, Any] = None, label: str = None) -> Arc:
        """Create an arc"""
        style = style or {'color': 'blue', 'linewidth': 2}
        
        arc = Arc(center, 2*radius, 2*radius, 
                 angle=0, theta1=start_angle, theta2=end_angle,
                 label=label, **style)
        self.ax.add_patch(arc)
        
        shape_id = f"arc_{self._shape_id}"
        self.shapes[shape_id] = {
            'type': 'arc',
            'object': arc,
            'center': center,
            'radius': radius,
            'start_angle': start_angle,
            'end_angle': end_angle
        }
        self._shape_id += 1
        
        return arc
    
    def create_text(self, position: Tuple[float, float], text: str,
                   style: Dict[str, Any] = None) -> plt.Text:
        """Create text annotation"""
        style = style or {'fontsize': 12, 'ha': 'center', 'va': 'center'}
        
        text_obj = self.ax.text(position[0], position[1], text, **style)
        
        shape_id = f"text_{self._shape_id}"
        self.shapes[shape_id] = {
            'type': 'text',
            'object': text_obj,
            'position': position,
            'text': text
        }
        self._shape_id += 1
        
        return text_obj
    
    def create_arrow(self, start: Tuple[float, float], end: Tuple[float, float],
                    style: Dict[str, Any] = None, label: str = None):
        """Create an arrow"""
        style = style or {'arrowstyle': '->', 'color': 'black', 'lw': 2}
        
        arrow = self.ax.annotate('', xy=end, xytext=start,
                               arrowprops=style, label=label)
        
        shape_id = f"arrow_{self._shape_id}"
        self.shapes[shape_id] = {
            'type': 'arrow',
            'object': arrow,
            'start': start,
            'end': end
        }
        self._shape_id += 1
        
        return arrow
    
    def mark_right_angle(self, vertex: Tuple[float, float], 
                        point1: Tuple[float, float], 
                        point2: Tuple[float, float], 
                        size: float = 0.3):
        """Mark a right angle with a square symbol"""
        v1 = np.array(point1) - np.array(vertex)
        v2 = np.array(point2) - np.array(vertex)
        
        # Normalize and scale
        v1_norm = v1 / np.linalg.norm(v1) * size
        v2_norm = v2 / np.linalg.norm(v2) * size
        
        # Create square
        corner = np.array(vertex) + v1_norm + v2_norm
        square_points = [
            vertex,
            np.array(vertex) + v1_norm,
            corner,
            np.array(vertex) + v2_norm,
            vertex
        ]
        
        square_x = [p[0] for p in square_points]
        square_y = [p[1] for p in square_points]
        
        line = self.ax.plot(square_x, square_y, 'k-', linewidth=1, alpha=0.7)[0]
        
        shape_id = f"right_angle_{self._shape_id}"
        self.shapes[shape_id] = {
            'type': 'right_angle_marker',
            'object': line,
            'vertex': vertex,
            'point1': point1,
            'point2': point2
        }
        self._shape_id += 1
        
        return line
    
    def get_shape_info(self, shape_id: str) -> Dict[str, Any]:
        """Get information about a shape"""
        return self.shapes.get(shape_id, {})
    
    def list_shapes(self) -> List[str]:
        """List all created shapes"""
        return list(self.shapes.keys())
    
    def clear_all(self):
        """Clear all shapes"""
        self.ax.clear()
        self.shapes.clear()
        self._shape_id = 0