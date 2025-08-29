# ImageGen AI

A Python library for AI-powered image generation using Stable Diffusion models.

## Features

- Easy-to-use API for image generation
- Support for batch generation
- Memory management and optimization
- Metadata support for generated images
- Utility functions for image processing
- Configurable settings

## Installation

### From PyPI (when published)
```bash
pip install imagegen-ai
```

### From source
```bash
git clone <repository-url>
cd imagegen-ai
pip install -e .
```

## Quick Start

```python
from imagegen import ImageGenerator, save_image

# Initialize generator
generator = ImageGenerator()

# Generate an image
image = generator.generate(
    prompt="A beautiful sunset over mountains",
    width=512,
    height=512,
    seed=42
)

# Save the image
save_image(image, "sunset.png")
```

## Advanced Usage

### Batch Generation
```python
prompts = [
    "A futuristic city",
    "A peaceful forest",
    "A vintage car"
]

images = generator.generate_batch(prompts)
```

### Custom Configuration
```python
from imagegen import Config

config = Config(
    model_id="runwayml/stable-diffusion-v1-5",
    device="cuda",
    default_width=768,
    default_height=768
)

generator = ImageGenerator(
    model_id=config.model_id,
    device=config.device
)
```

### Creating Image Grids
```python
from imagegen.utils import create_grid

# Generate multiple images
images = generator.generate_batch(prompts)

# Create a grid
grid = create_grid(images, grid_size=(2, 2))
save_image(grid, "image_grid.png")
```

## API Reference

### ImageGenerator

Main class for image generation.

#### Methods

- `generate(prompt, **kwargs)` - Generate a single image
- `generate_batch(prompts, **kwargs)` - Generate multiple images
- `change_model(model_id)` - Switch to a different model
- `get_memory_usage()` - Get current memory usage
- `clear_memory()` - Clear GPU memory cache

### Utility Functions

- `save_image(image, filename, directory, metadata)` - Save a single image
- `save_images(images, base_filename, directory, metadata)` - Save multiple images
- `create_grid(images, grid_size, spacing)` - Create an image grid
- `batch_resize(images, size, method)` - Resize multiple images

## Requirements

- Python 3.8+
- PyTorch 1.13.0+
- CUDA-capable GPU (recommended)

## License

MIT License - see LICENSE file for details.

