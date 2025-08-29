"""
MathDiagram - Generic Mathematical Diagram Generation Library

A flexible, configurable system for generating mathematical diagrams for any topic.
Supports geometry, algebra, trigonometry, calculus, statistics, and more.

Basic Usage:
    from mathdiagram import MathDiagram
    
    # Create a diagram generator
    md = MathDiagram()
    
    # Generate any math topic diagram
    diagram = md.create_diagram("geometry", "circle_tangents", {
        'radius': 4,
        'external_point': (7, 5)
    })
    
    # Save the diagram
    diagram.save("my_diagram.png")

Advanced Usage:
    # Create custom problem template
    template = md.create_template({
        'topic': 'trigonometry',
        'elements': [...],
        'constraints': [...]
    })
    
    # Generate random problem
    problem = md.random_problem("algebra", difficulty="intermediate")
"""

from .core import MathDiagram
from .templates import ProblemTemplate, TemplateLoader
from .shapes import ShapeGenerator
from .config import DiagramConfig
from .constraints import ConstraintSolver

__version__ = "1.0.0"
__author__ = "MathDiagram Library"

# Main exports for library users
__all__ = [
    'MathDiagram',
    'ProblemTemplate', 
    'TemplateLoader',
    'ShapeGenerator',
    'DiagramConfig',
    'ConstraintSolver'
]

# Convenience functions for quick usage
def create_diagram(topic, subtopic=None, parameters=None, config=None):
    """
    Quick function to create a diagram
    
    Args:
        topic (str): Mathematical topic (e.g., 'geometry', 'algebra')
        subtopic (str): Specific subtopic (e.g., 'circle_tangents', 'linear_equations')
        parameters (dict): Custom parameters for the diagram
        config (DiagramConfig): Configuration settings
        
    Returns:
        str: Path to generated diagram
    """
    md = MathDiagram(config)
    return md.create_diagram(topic, subtopic, parameters)

def list_topics():
    """List all available mathematical topics"""
    md = MathDiagram()
    return md.list_topics()

def random_problem(topic, difficulty=None):
    """Generate a random problem for given topic"""
    md = MathDiagram()
    return md.random_problem(topic, difficulty)