# MathDiagram

A generic mathematical diagram generation library for any topic. Create diagrams for geometry, algebra, trigonometry, statistics, and more without hardcoded values.

## Features

- **Generic system**: Create diagrams for ANY mathematical topic
- **No hardcoded values**: All parameters are configurable
- **Professional output**: High-quality matplotlib-based diagrams
- **Multiple topics**: Geometry, Algebra, Trigonometry, Statistics, Calculus
- **Flexible configuration**: Academic, minimal, and presentation styles
- **Batch generation**: Create multiple problems at once
- **Template system**: Extensible problem templates
- **Constraint solving**: Mathematical relationship validation

## Installation

```bash
pip install mathdiagram
```

## Quick Start

```python
from mathdiagram import MathDiagram

# Create a diagram generator
md = MathDiagram()

# Generate a geometry diagram with custom parameters
diagram = md.create_diagram("geometry", "circle_tangents", {
    "radius": 4,
    "external_point": (7, 5)
})

# Save the diagram
diagram.save("my_diagram.png")
```

## Advanced Usage

### Different Mathematical Topics

```python
# Algebra - Linear equation
diagram = md.create_diagram("algebra", "linear_equation", {
    "slope": 2.5,
    "y_intercept": -1
})

# Trigonometry - Angle of elevation
diagram = md.create_diagram("trigonometry", "angle_of_elevation", {
    "distance": 30,
    "angle_degrees": 45
})

# Statistics - Histogram
diagram = md.create_diagram("statistics", "histogram", {
    "data": [12, 15, 18, 20, 22, 25, 28, 30, 32, 35],
    "bins": 5
})
```

### Custom Configuration Styles

```python
from mathdiagram import DiagramConfig

# Academic style for publications
config = DiagramConfig.academic()
md = MathDiagram(config)

# Minimal style for clean diagrams
config = DiagramConfig.minimal() 
md = MathDiagram(config)

# Presentation style for slides
config = DiagramConfig.presentation()
md = MathDiagram(config)
```

### Random Problem Generation

```python
# Generate random problems for any topic
random_geometry = md.random_problem("geometry")
random_algebra = md.random_problem("algebra")
random_stats = md.random_problem("statistics")
```

### Batch Generation

```python
# Generate multiple diagrams for a topic
diagrams = md.batch_generate("geometry", count=5, output_dir="problems")
```

## Supported Topics

- **Geometry**: Circle tangents, triangles, polygons, constructions
- **Algebra**: Linear equations, quadratic functions, polynomials  
- **Trigonometry**: Angle problems, unit circle, wave functions
- **Statistics**: Histograms, box plots, scatter plots, distributions
- **Calculus**: Derivatives, integrals, limits (extensible)

## API Reference

### MathDiagram

Main class for diagram generation.

#### Methods

- `create_diagram(topic, subtopic, parameters)` - Create a custom diagram
- `random_problem(topic, difficulty)` - Generate random problem
- `batch_generate(topic, count, output_dir)` - Create multiple diagrams
- `list_topics()` - List available topics
- `list_subtopics(topic)` - List subtopics for a topic

### DiagramConfig

Configuration class for styling and behavior.

#### Presets

- `DiagramConfig.academic()` - High-resolution academic style
- `DiagramConfig.minimal()` - Clean, minimal style  
- `DiagramConfig.presentation()` - Large, clear presentation style

## Examples

### Geometry Problem
```python
# Create a circle tangent problem
diagram = md.create_diagram("geometry", "circle_tangents", {
    "radius": 3,
    "external_x": 6, 
    "external_y": 4
})
print(diagram.get_info()['problem_statement'])
```

### Algebra Graph
```python
# Create a linear equation graph
diagram = md.create_diagram("algebra", "linear_equation", {
    "slope": 1.5,
    "y_intercept": 2
})
```

### Statistics Visualization
```python  
# Create a data histogram
diagram = md.create_diagram("statistics", "histogram", {
    "data": [1, 2, 2, 3, 3, 3, 4, 4, 5],
    "bins": 5,
    "title": "Sample Data"
})
```

## Requirements

- Python 3.7+
- matplotlib>=3.3.0
- numpy>=1.18.0
- scipy>=1.5.0

## License

MIT License - see LICENSE file for details.