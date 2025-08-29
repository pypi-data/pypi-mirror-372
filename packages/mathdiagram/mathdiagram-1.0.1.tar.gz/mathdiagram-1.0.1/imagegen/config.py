from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class Config:
    model_id: str = "runwayml/stable-diffusion-v1-5"
    device: str = "auto"
    default_width: int = 512
    default_height: int = 512
    default_steps: int = 20
    default_guidance_scale: float = 7.5
    output_dir: str = "./generated_images"
    cache_dir: Optional[str] = None
    
    def __post_init__(self):
        if self.cache_dir is None:
            self.cache_dir = os.path.expanduser("~/.cache/huggingface/transformers")
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    @classmethod
    def from_dict(cls, config_dict: dict):
        return cls(**{k: v for k, v in config_dict.items() if hasattr(cls, k)})
    
    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "device": self.device,
            "default_width": self.default_width,
            "default_height": self.default_height,
            "default_steps": self.default_steps,
            "default_guidance_scale": self.default_guidance_scale,
            "output_dir": self.output_dir,
            "cache_dir": self.cache_dir
        }