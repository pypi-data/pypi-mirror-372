"""
Core MathDiagram Library - Main API Interface
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from .templates import TemplateLoader, ProblemTemplate
from .shapes import ShapeGenerator
from .config import DiagramConfig
from .constraints import ConstraintSolver
from .utils import validate_parameters, ensure_output_dir

class Diagram:
    """Represents a generated mathematical diagram"""
    
    def __init__(self, figure, template: ProblemTemplate, parameters: Dict[str, Any]):
        self.figure = figure
        self.template = template
        self.parameters = parameters
        self._saved_path = None
        
    def save(self, filepath: str = None, dpi: int = 300, format: str = 'png') -> str:
        """
        Save diagram to file
        
        Args:
            filepath: Output file path (auto-generated if None)
            dpi: Image resolution
            format: Output format ('png', 'pdf', 'svg')
            
        Returns:
            str: Path to saved file
        """
        if filepath is None:
            ensure_output_dir("output")
            filepath = f"output/{self.template.topic}_{self.template.subtopic}.{format}"
        
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        self.figure.savefig(filepath, dpi=dpi, bbox_inches='tight', 
                          facecolor='white', edgecolor='none')
        
        self._saved_path = filepath
        return filepath
        
    def show(self):
        """Display diagram interactively"""
        plt.figure(self.figure.number)
        plt.show()
        
    def close(self):
        """Close the diagram figure"""
        plt.close(self.figure)
        
    def get_info(self) -> Dict[str, Any]:
        """Get information about the diagram"""
        return {
            'topic': self.template.topic,
            'subtopic': self.template.subtopic,
            'difficulty': self.template.difficulty,
            'parameters': self.parameters,
            'saved_path': self._saved_path,
            'problem_statement': self.template.problem_statement,
            'key_concepts': self.template.key_concepts
        }

class MathDiagram:
    """
    Main MathDiagram Library Interface
    
    This is the primary class for generating mathematical diagrams.
    Supports any mathematical topic through configurable templates.
    """
    
    def __init__(self, config: DiagramConfig = None, template_path: str = None):
        """
        Initialize MathDiagram generator
        
        Args:
            config: Diagram configuration settings
            template_path: Path to problem templates file
        """
        self.config = config or DiagramConfig()
        self.template_loader = TemplateLoader(template_path)
        self.constraint_solver = ConstraintSolver()
        
    def create_diagram(self, 
                      topic: str, 
                      subtopic: str = None,
                      parameters: Dict[str, Any] = None,
                      random: bool = False) -> Diagram:
        """
        Create a mathematical diagram for any topic
        
        Args:
            topic: Mathematical topic (e.g., 'geometry', 'algebra', 'trigonometry')
            subtopic: Specific subtopic (e.g., 'circle_tangents', 'linear_equations')
            parameters: Custom parameters for the problem
            random: Generate random parameters if True
            
        Returns:
            Diagram: Generated diagram object
            
        Examples:
            # Basic geometry problem
            diagram = md.create_diagram('geometry', 'circle_tangents')
            
            # Custom trigonometry problem  
            diagram = md.create_diagram('trigonometry', 'angle_of_elevation', {
                'ground_distance': 25,
                'angle_degrees': 35
            })
            
            # Random algebra problem
            diagram = md.create_diagram('algebra', 'linear_equations', random=True)
        """
        
        # Find matching template
        template = self._find_template(topic, subtopic)
        if not template:
            raise ValueError(f"No template found for topic='{topic}', subtopic='{subtopic}'")
        
        # Generate or use provided parameters
        if random or parameters is None:
            if parameters is None:
                parameters = {}
            # Merge with random parameters
            random_params = self.template_loader.generate_random_parameters(template)
            random_params.update(parameters)
            parameters = random_params
        
        # Validate parameters
        parameters = validate_parameters(parameters, template.parameter_ranges)
        
        # Create template with substituted parameters
        resolved_template = self.template_loader.substitute_parameters(template, parameters)
        
        # Generate diagram
        figure = self._generate_figure(resolved_template, parameters)
        
        return Diagram(figure, resolved_template, parameters)
    
    def random_problem(self, 
                      topic: str, 
                      difficulty: str = None,
                      subtopic: str = None) -> Diagram:
        """
        Generate a random problem for given topic
        
        Args:
            topic: Mathematical topic
            difficulty: Problem difficulty ('basic', 'intermediate', 'advanced')
            subtopic: Optional specific subtopic
            
        Returns:
            Diagram: Random problem diagram
        """
        return self.create_diagram(topic, subtopic, random=True)
    
    def create_custom_problem(self, 
                            template_definition: Dict[str, Any],
                            parameters: Dict[str, Any] = None) -> Diagram:
        """
        Create diagram from custom template definition
        
        Args:
            template_definition: Dictionary defining the problem template
            parameters: Parameters for the problem
            
        Returns:
            Diagram: Generated custom diagram
        """
        # Convert dictionary to ProblemTemplate
        template = self._dict_to_template(template_definition)
        
        # Generate parameters if not provided
        if parameters is None:
            parameters = self.template_loader.generate_random_parameters(template)
        
        # Generate diagram
        figure = self._generate_figure(template, parameters)
        
        return Diagram(figure, template, parameters)
    
    def list_topics(self) -> List[str]:
        """List all available mathematical topics"""
        topics = set()
        for template in self.template_loader.templates.values():
            topics.add(template.topic)
        return sorted(list(topics))
    
    def list_subtopics(self, topic: str) -> List[str]:
        """List available subtopics for a given topic"""
        subtopics = set()
        for template in self.template_loader.templates.values():
            if template.topic.lower() == topic.lower():
                subtopics.add(template.subtopic)
        return sorted(list(subtopics))
    
    def get_template_info(self, topic: str, subtopic: str = None) -> Dict[str, Any]:
        """Get information about available templates"""
        template = self._find_template(topic, subtopic)
        if not template:
            return {}
        
        return {
            'topic': template.topic,
            'subtopic': template.subtopic,
            'difficulty': template.difficulty,
            'problem_type': template.problem_type,
            'key_concepts': template.key_concepts,
            'parameter_ranges': template.parameter_ranges,
            'randomizable_params': template.randomizable,
            'problem_statement': template.problem_statement
        }
    
    def batch_generate(self, 
                      topic: str, 
                      count: int = 5,
                      subtopic: str = None,
                      output_dir: str = "batch_output") -> List[Diagram]:
        """
        Generate multiple random diagrams for a topic
        
        Args:
            topic: Mathematical topic
            count: Number of diagrams to generate
            subtopic: Optional specific subtopic
            output_dir: Directory to save diagrams
            
        Returns:
            List[Diagram]: List of generated diagrams
        """
        ensure_output_dir(output_dir)
        
        diagrams = []
        for i in range(count):
            try:
                diagram = self.random_problem(topic, subtopic=subtopic)
                
                # Auto-save with unique names
                filename = f"{output_dir}/{topic}_{subtopic or 'mixed'}_{i+1:03d}.png"
                diagram.save(filename)
                
                diagrams.append(diagram)
                
            except Exception as e:
                print(f"Error generating diagram {i+1}: {e}")
                continue
        
        return diagrams
    
    def _find_template(self, topic: str, subtopic: str = None):
        """Find matching template"""
        # Try exact match first
        if subtopic:
            template_id = f"{topic.lower()}_{subtopic.lower()}".replace(" ", "_")
            if template_id in self.template_loader.templates:
                return template_id
        
        # Search by topic and subtopic
        for template_id, template in self.template_loader.templates.items():
            if template.topic.lower() == topic.lower():
                if subtopic is None or template.subtopic.lower().replace(" ", "_") == subtopic.lower().replace(" ", "_"):
                    return template_id
        
        return None
    
    def _generate_figure(self, template: ProblemTemplate, parameters: Dict[str, Any]):
        """Generate matplotlib figure from template"""
        
        # Create figure
        fig = plt.figure(figsize=(self.config.width, self.config.height))
        ax = fig.add_subplot(111)
        
        # Create shape generator
        shape_gen = ShapeGenerator(ax, self.config)
        
        # Generate elements based on template
        self._create_elements(shape_gen, template, parameters)
        
        # Apply styling and layout
        self._apply_styling(ax, template, parameters)
        
        return fig
    
    def _create_elements(self, shape_gen: ShapeGenerator, 
                        template: ProblemTemplate, parameters: Dict[str, Any]):
        """Create geometric elements from template"""
        
        for element in template.given_elements:
            # Resolve parameter references
            resolved_params = self._resolve_element_params(element.parameters, parameters)
            
            # Create the element
            if element.shape_type.value == 'circle':
                center = (resolved_params.get('center_x', 0), resolved_params.get('center_y', 0))
                radius = resolved_params.get('radius', 1)
                shape_gen.create_circle(center, radius, element.style)
                
            elif element.shape_type.value == 'line':
                start = (resolved_params.get('start_x', 0), resolved_params.get('start_y', 0))
                end = (resolved_params.get('end_x', 1), resolved_params.get('end_y', 1))
                shape_gen.create_line(start, end, element.style)
                
            elif element.shape_type.value == 'point':
                pos = (resolved_params.get('x', 0), resolved_params.get('y', 0))
                shape_gen.create_point(pos, element.style)
                
            elif element.shape_type.value == 'triangle':
                vertices = []
                for i in range(3):
                    x = resolved_params.get(f'vertex_{i}_x', i)
                    y = resolved_params.get(f'vertex_{i}_y', i)
                    vertices.append((x, y))
                shape_gen.create_triangle(vertices, element.style)
                
            # Add more shape types as needed
    
    def _resolve_element_params(self, element_params: Dict[str, Any], 
                               global_params: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameter references in element parameters"""
        resolved = {}
        
        for key, value in element_params.items():
            if isinstance(value, str) and value.startswith('$'):
                param_name = value[1:]  # Remove '$' prefix
                resolved[key] = global_params.get(param_name, 0)
            else:
                resolved[key] = value
                
        return resolved
    
    def _apply_styling(self, ax, template: ProblemTemplate, parameters: Dict[str, Any]):
        """Apply styling and finalize diagram"""
        
        # Set title
        title = f"{template.topic}: {template.subtopic}"
        ax.set_title(title, fontsize=self.config.title_size, fontweight='bold')
        
        # Configure axes
        if self.config.grid:
            ax.grid(True, alpha=0.3)
        
        if self.config.axes:
            ax.set_xlabel('x', fontsize=self.config.label_size)
            ax.set_ylabel('y', fontsize=self.config.label_size)
        
        # Set equal aspect ratio for geometry problems
        if template.topic.lower() == 'geometry':
            ax.set_aspect('equal')
        
        # Auto-scale if enabled
        if self.config.auto_scale:
            ax.autoscale(True)
        
        # Add legend if enabled
        if self.config.legend:
            try:
                ax.legend(fontsize=self.config.label_size - 2)
            except:
                pass  # Skip if no labeled elements
    
    def _dict_to_template(self, template_dict: Dict[str, Any]) -> ProblemTemplate:
        """Convert dictionary to ProblemTemplate object"""
        # This would implement conversion from dict to ProblemTemplate
        # For now, simplified implementation
        return ProblemTemplate(
            topic=template_dict.get('topic', 'Custom'),
            subtopic=template_dict.get('subtopic', 'Problem'),
            difficulty=template_dict.get('difficulty', 'basic'),
            problem_type=template_dict.get('problem_type', 'custom'),
            given_elements=[],
            required_elements=[],
            relationships=[],
            problem_statement=template_dict.get('problem_statement', ''),
            solution_steps=template_dict.get('solution_steps', []),
            key_concepts=template_dict.get('key_concepts', []),
            parameter_ranges=template_dict.get('parameter_ranges', {}),
            randomizable=template_dict.get('randomizable', [])
        )