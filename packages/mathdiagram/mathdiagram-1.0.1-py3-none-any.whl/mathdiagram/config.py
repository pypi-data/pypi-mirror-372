"""
Configuration classes for MathDiagram library
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
from enum import Enum

class DiagramType(Enum):
    """Types of mathematical diagrams"""
    GEOMETRY = "geometry"
    ALGEBRA = "algebra" 
    TRIGONOMETRY = "trigonometry"
    CALCULUS = "calculus"
    STATISTICS = "statistics"
    NUMBER_THEORY = "number_theory"
    COORDINATE_GEOMETRY = "coordinate_geometry"

class UnitSystem(Enum):
    """Unit systems for measurements"""
    METRIC = "metric"
    IMPERIAL = "imperial" 
    ABSTRACT = "abstract"

@dataclass
class DiagramConfig:
    """
    Configuration for diagram generation
    
    Controls all aspects of diagram appearance and behavior.
    Can be customized for different use cases.
    """
    
    # Figure dimensions
    width: int = 10
    height: int = 8
    dpi: int = 300
    background_color: str = 'white'
    
    # Mathematical settings
    coordinate_system: str = 'cartesian'  # cartesian, polar, 3d
    units: UnitSystem = UnitSystem.ABSTRACT
    precision: int = 2
    
    # Visual appearance
    grid: bool = True
    axes: bool = True
    legend: bool = True
    title_size: int = 14
    label_size: int = 12
    
    # Text and labeling
    smart_text: bool = True
    font_family: str = 'sans-serif'
    text_color: str = 'black'
    
    # Layout and spacing
    margins: Dict[str, float] = field(default_factory=lambda: {
        'top': 0.1, 'bottom': 0.1, 'left': 0.1, 'right': 0.1
    })
    subplot_layout: Optional[Tuple[int, int]] = None
    tight_layout: bool = True
    
    # Advanced features
    auto_scale: bool = True
    constraint_solving: bool = True
    validation: bool = True
    
    # Output settings
    default_format: str = 'png'
    save_metadata: bool = True
    
    # Style presets
    style_preset: str = 'default'  # default, minimal, academic, presentation
    
    @classmethod
    def minimal(cls) -> 'DiagramConfig':
        """Minimal configuration for simple diagrams"""
        return cls(
            width=8,
            height=6,
            grid=False,
            legend=False,
            title_size=12,
            label_size=10,
            style_preset='minimal'
        )
    
    @classmethod
    def academic(cls) -> 'DiagramConfig':
        """Academic publication style"""
        return cls(
            width=10,
            height=8,
            dpi=600,  # High resolution for publications
            font_family='serif',
            title_size=16,
            label_size=14,
            grid=True,
            style_preset='academic'
        )
    
    @classmethod
    def presentation(cls) -> 'DiagramConfig':
        """Large, clear style for presentations"""
        return cls(
            width=12,
            height=9,
            title_size=18,
            label_size=16,
            grid=True,
            legend=True,
            style_preset='presentation'
        )
    
    def apply_preset(self):
        """Apply style preset modifications"""
        if self.style_preset == 'minimal':
            self.grid = False
            self.legend = False
        elif self.style_preset == 'academic':
            self.font_family = 'serif'
            self.dpi = 600
        elif self.style_preset == 'presentation':
            self.title_size = 18
            self.label_size = 16

@dataclass  
class ProblemConfig:
    """Configuration for problem generation"""
    
    # Difficulty settings
    difficulty: str = 'intermediate'  # basic, intermediate, advanced
    randomize: bool = True
    seed: Optional[int] = None
    
    # Content settings
    include_solution: bool = True
    include_steps: bool = True
    show_measurements: bool = True
    
    # Language/notation
    angle_units: str = 'degrees'  # degrees, radians
    decimal_places: int = 2
    use_symbols: bool = True  # Use mathematical symbols vs text
    
    # Problem complexity
    max_elements: int = 10
    max_constraints: int = 5
    allow_construction: bool = True