"""
Template system for mathematical problem generation
"""

import json
import random
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path
from enum import Enum

class ShapeType(Enum):
    """Supported geometric shapes"""
    CIRCLE = "circle"
    LINE = "line"
    POINT = "point"
    TRIANGLE = "triangle"
    RECTANGLE = "rectangle"
    POLYGON = "polygon"
    ARC = "arc"
    ANGLE = "angle"

class RelationshipType(Enum):
    """Mathematical relationships between elements"""
    TANGENT = "tangent"
    PARALLEL = "parallel"
    PERPENDICULAR = "perpendicular"
    CONGRUENT = "congruent"
    SIMILAR = "similar"
    INSCRIBED = "inscribed"
    CIRCUMSCRIBED = "circumscribed"

@dataclass
class GeometricElement:
    """Represents a geometric element in a problem"""
    shape_type: ShapeType
    parameters: Dict[str, Any]
    style: Dict[str, Any] = field(default_factory=dict)
    label: Optional[str] = None

@dataclass  
class Relationship:
    """Represents a mathematical relationship between elements"""
    relationship_type: RelationshipType
    elements: List[str]  # Element IDs
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProblemTemplate:
    """Template for generating mathematical problems"""
    topic: str
    subtopic: str
    difficulty: str
    problem_type: str
    given_elements: List[GeometricElement]
    required_elements: List[GeometricElement]  
    relationships: List[Relationship]
    problem_statement: str
    solution_steps: List[str]
    key_concepts: List[str]
    parameter_ranges: Dict[str, Dict[str, Any]]
    randomizable: List[str]

class TemplateLoader:
    """Loads and manages problem templates"""
    
    def __init__(self, template_path: str = None):
        self.template_path = template_path or "templates"
        self.templates = {}
        self._load_default_templates()
        
    def _load_default_templates(self):
        """Load built-in default templates"""
        
        # Geometry: Circle Tangents
        self.templates["geometry_circle_tangents"] = ProblemTemplate(
            topic="geometry",
            subtopic="circle_tangents", 
            difficulty="intermediate",
            problem_type="construction",
            given_elements=[
                GeometricElement(
                    shape_type=ShapeType.CIRCLE,
                    parameters={"center_x": 0, "center_y": 0, "radius": "$radius"},
                    style={"fill": False, "color": "blue", "linewidth": 2}
                ),
                GeometricElement(
                    shape_type=ShapeType.POINT,
                    parameters={"x": "$external_x", "y": "$external_y"},
                    style={"color": "red", "markersize": 8}
                )
            ],
            required_elements=[
                GeometricElement(
                    shape_type=ShapeType.LINE,
                    parameters={"start_x": "$external_x", "start_y": "$external_y",
                              "end_x": "$tangent1_x", "end_y": "$tangent1_y"},
                    style={"color": "green", "linewidth": 2}
                ),
                GeometricElement(
                    shape_type=ShapeType.LINE,
                    parameters={"start_x": "$external_x", "start_y": "$external_y", 
                              "end_x": "$tangent2_x", "end_y": "$tangent2_y"},
                    style={"color": "green", "linewidth": 2}
                )
            ],
            relationships=[
                Relationship(
                    relationship_type=RelationshipType.TANGENT,
                    elements=["tangent_line_1", "circle"],
                    parameters={}
                ),
                Relationship(
                    relationship_type=RelationshipType.TANGENT,
                    elements=["tangent_line_2", "circle"],
                    parameters={}
                )
            ],
            problem_statement="Given a circle with center at origin and radius {radius}, and an external point P({external_x}, {external_y}), construct the two tangent lines from P to the circle.",
            solution_steps=[
                "Calculate distance from external point to center",
                "Use Pythagorean theorem to find tangent length",  
                "Find tangent points using perpendicular from center",
                "Draw tangent lines from external point to tangent points"
            ],
            key_concepts=["tangent lines", "circle geometry", "Pythagorean theorem"],
            parameter_ranges={
                "radius": {"min": 1, "max": 8, "type": "float"},
                "external_x": {"min": -10, "max": 10, "type": "float"},
                "external_y": {"min": -10, "max": 10, "type": "float"}
            },
            randomizable=["radius", "external_x", "external_y"]
        )
        
        # Algebra: Linear Equation
        self.templates["algebra_linear_equation"] = ProblemTemplate(
            topic="algebra",
            subtopic="linear_equation",
            difficulty="basic", 
            problem_type="graph",
            given_elements=[],
            required_elements=[
                GeometricElement(
                    shape_type=ShapeType.LINE,
                    parameters={"function": "lambda x: $slope * x + $y_intercept",
                              "x_range": (-10, 10)},
                    style={"color": "blue", "linewidth": 3}
                )
            ],
            relationships=[],
            problem_statement="Graph the linear equation y = {slope}x + {y_intercept}",
            solution_steps=[
                "Identify slope m = {slope}",
                "Identify y-intercept b = {y_intercept}",
                "Plot y-intercept point (0, {y_intercept})",
                "Use slope to find additional points",
                "Draw line through points"
            ],
            key_concepts=["linear equations", "slope", "y-intercept", "graphing"],
            parameter_ranges={
                "slope": {"min": -5, "max": 5, "type": "float"},
                "y_intercept": {"min": -10, "max": 10, "type": "float"}
            },
            randomizable=["slope", "y_intercept"]
        )
        
        # Trigonometry: Angle of Elevation
        self.templates["trigonometry_angle_of_elevation"] = ProblemTemplate(
            topic="trigonometry",
            subtopic="angle_of_elevation",
            difficulty="intermediate",
            problem_type="word_problem",
            given_elements=[
                GeometricElement(
                    shape_type=ShapeType.LINE,
                    parameters={"start_x": 0, "start_y": 0, "end_x": "$distance", "end_y": 0},
                    style={"color": "brown", "linewidth": 3}
                ),
                GeometricElement(
                    shape_type=ShapeType.LINE,
                    parameters={"start_x": "$distance", "start_y": 0, "end_x": "$distance", "end_y": "$height"},
                    style={"color": "gray", "linewidth": 4}
                )
            ],
            required_elements=[
                GeometricElement(
                    shape_type=ShapeType.LINE,
                    parameters={"start_x": 0, "start_y": 0, "end_x": "$distance", "end_y": "$height"},
                    style={"color": "red", "linewidth": 2, "linestyle": "--"}
                ),
                GeometricElement(
                    shape_type=ShapeType.ANGLE,
                    parameters={"vertex_x": 0, "vertex_y": 0, "angle": "$angle_degrees"},
                    style={"facecolor": "yellow", "alpha": 0.3}
                )
            ],
            relationships=[],
            problem_statement="From a point {distance} meters from the base of a building, the angle of elevation to the top is {angle_degrees}°. Find the height of the building.",
            solution_steps=[
                "Draw right triangle with ground distance = {distance}m",
                "Angle of elevation = {angle_degrees}°",
                "Use trigonometry: tan({angle_degrees}°) = height / {distance}",
                "Solve: height = {distance} × tan({angle_degrees}°)"
            ],
            key_concepts=["angle of elevation", "trigonometry", "tangent ratio", "right triangles"],
            parameter_ranges={
                "distance": {"min": 10, "max": 50, "type": "float"},
                "angle_degrees": {"min": 15, "max": 75, "type": "float"}
            },
            randomizable=["distance", "angle_degrees"]
        )
        
        # Statistics: Histogram
        self.templates["statistics_histogram"] = ProblemTemplate(
            topic="statistics",
            subtopic="histogram",
            difficulty="basic",
            problem_type="data_visualization",
            given_elements=[],
            required_elements=[
                GeometricElement(
                    shape_type=ShapeType.RECTANGLE,
                    parameters={"data": "$data", "bins": "$bins"},
                    style={"color": "skyblue", "edgecolor": "black", "alpha": 0.7}
                )
            ],
            relationships=[],
            problem_statement="Create a histogram for the data set: {data}",
            solution_steps=[
                "Organize data: {data}",
                "Determine number of bins: {bins}",
                "Count frequency for each bin",
                "Draw bars with heights equal to frequencies"
            ],
            key_concepts=["histogram", "frequency distribution", "data visualization", "bins"],
            parameter_ranges={
                "bins": {"min": 3, "max": 10, "type": "int"}
            },
            randomizable=["bins"]
        )
        
    def generate_random_parameters(self, template: ProblemTemplate) -> Dict[str, Any]:
        """Generate random parameters for a template"""
        params = {}
        
        for param_name in template.randomizable:
            if param_name in template.parameter_ranges:
                range_info = template.parameter_ranges[param_name]
                param_type = range_info.get("type", "float")
                
                if param_type == "int":
                    params[param_name] = random.randint(range_info["min"], range_info["max"])
                elif param_type == "float":
                    params[param_name] = round(random.uniform(range_info["min"], range_info["max"]), 2)
                    
        # Special handling for specific templates
        if template.subtopic == "histogram":
            # Generate random data set
            data_size = random.randint(10, 30)
            params["data"] = [random.randint(1, 100) for _ in range(data_size)]
            
        return params
    
    def substitute_parameters(self, template: ProblemTemplate, parameters: Dict[str, Any]) -> ProblemTemplate:
        """Create a new template with substituted parameters"""
        # Create a copy of the template with parameter substitution
        # This is a simplified version - full implementation would recursively
        # substitute all parameter references in the template
        
        substituted_statement = template.problem_statement.format(**parameters)
        substituted_steps = [step.format(**parameters) for step in template.solution_steps]
        
        return ProblemTemplate(
            topic=template.topic,
            subtopic=template.subtopic,
            difficulty=template.difficulty,
            problem_type=template.problem_type,
            given_elements=template.given_elements,
            required_elements=template.required_elements,
            relationships=template.relationships,
            problem_statement=substituted_statement,
            solution_steps=substituted_steps,
            key_concepts=template.key_concepts,
            parameter_ranges=template.parameter_ranges,
            randomizable=template.randomizable
        )
        
    def get_template(self, template_id: str) -> Optional[ProblemTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[str]:
        """List all available template IDs"""
        return list(self.templates.keys())
    
    def get_templates_by_topic(self, topic: str) -> List[ProblemTemplate]:
        """Get all templates for a specific topic"""
        return [template for template in self.templates.values() 
                if template.topic.lower() == topic.lower()]