import os
import json
from PIL import Image
from typing import Optional, Union, List
from datetime import datetime
import hashlib

def save_image(
    image: Image.Image,
    filename: Optional[str] = None,
    directory: str = "./generated_images",
    metadata: Optional[dict] = None
) -> str:
    os.makedirs(directory, exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.png"
    
    if not filename.endswith(('.png', '.jpg', '.jpeg')):
        filename += '.png'
    
    filepath = os.path.join(directory, filename)
    
    if metadata:
        image.save(filepath, pnginfo=_create_png_info(metadata))
    else:
        image.save(filepath)
    
    return filepath

def save_images(
    images: List[Image.Image],
    base_filename: Optional[str] = None,
    directory: str = "./generated_images",
    metadata: Optional[dict] = None
) -> List[str]:
    filepaths = []
    
    for i, image in enumerate(images):
        if base_filename:
            name_parts = base_filename.split('.')
            if len(name_parts) > 1:
                filename = f"{'.'.join(name_parts[:-1])}_{i+1:03d}.{name_parts[-1]}"
            else:
                filename = f"{base_filename}_{i+1:03d}.png"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}_{i+1:03d}.png"
        
        filepath = save_image(image, filename, directory, metadata)
        filepaths.append(filepath)
    
    return filepaths

def load_model(model_path: str):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")
    
    return model_path

def create_prompt_hash(prompt: str, seed: Optional[int] = None) -> str:
    content = f"{prompt}_{seed}" if seed else prompt
    return hashlib.md5(content.encode()).hexdigest()[:8]

def _create_png_info(metadata: dict):
    from PIL.PngImagePlugin import PngInfo
    png_info = PngInfo()
    
    for key, value in metadata.items():
        if isinstance(value, (dict, list)):
            png_info.add_text(key, json.dumps(value))
        else:
            png_info.add_text(key, str(value))
    
    return png_info

def extract_metadata_from_image(filepath: str) -> dict:
    try:
        image = Image.open(filepath)
        metadata = {}
        
        if hasattr(image, 'text'):
            for key, value in image.text.items():
                try:
                    metadata[key] = json.loads(value)
                except json.JSONDecodeError:
                    metadata[key] = value
        
        return metadata
    except Exception as e:
        
        return {}

def batch_resize(
    images: List[Image.Image],
    size: tuple,
    method: str = "LANCZOS"
) -> List[Image.Image]:
    resize_method = getattr(Image.Resampling, method, Image.Resampling.LANCZOS)
    return [img.resize(size, resize_method) for img in images]

def create_grid(
    images: List[Image.Image],
    grid_size: Optional[tuple] = None,
    spacing: int = 10
) -> Image.Image:
    if not images:
        raise ValueError("No images provided")
    
    if grid_size is None:
        import math
        n = len(images)
        cols = int(math.ceil(math.sqrt(n)))
        rows = int(math.ceil(n / cols))
        grid_size = (cols, rows)
    
    cols, rows = grid_size
    img_width, img_height = images[0].size
    
    grid_width = cols * img_width + (cols - 1) * spacing
    grid_height = rows * img_height + (rows - 1) * spacing
    
    grid = Image.new('RGB', (grid_width, grid_height), (255, 255, 255))
    
    for idx, img in enumerate(images[:cols * rows]):
        row = idx // cols
        col = idx % cols
        
        x = col * (img_width + spacing)
        y = row * (img_height + spacing)
        
        grid.paste(img, (x, y))
    
    return grid