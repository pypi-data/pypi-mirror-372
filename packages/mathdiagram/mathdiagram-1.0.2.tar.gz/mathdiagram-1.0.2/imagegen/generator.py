import torch
from PIL import Image
import numpy as np
from diffusers import StableDiffusionPipeline
from typing import Optional, Union, List
import os

class ImageGenerator:
    def __init__(self, model_id: str = "runwayml/stable-diffusion-v1-5", device: str = "auto"):
        self.model_id = model_id
        self.device = self._get_device(device)
        self.pipeline = None
        self._load_pipeline()
    
    def _get_device(self, device: str) -> str:
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
    
    def _load_pipeline(self):
        try:
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            self.pipeline = self.pipeline.to(self.device)
            self.pipeline.enable_attention_slicing()
        except Exception as e:
            raise RuntimeError(f"Failed to load model {self.model_id}: {str(e)}")
    
    def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_images: int = 1,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Union[Image.Image, List[Image.Image]]:
        if not self.pipeline:
            raise RuntimeError("Pipeline not loaded")
        
        if seed is not None:
            torch.manual_seed(seed)
        
        with torch.autocast(self.device):
            result = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_images_per_prompt=num_images,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            )
        
        images = result.images
        return images[0] if num_images == 1 else images
    
    def generate_batch(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[Image.Image]:
        images = []
        for prompt in prompts:
            image = self.generate(prompt, **kwargs)
            if isinstance(image, list):
                images.extend(image)
            else:
                images.append(image)
        return images
    
    def change_model(self, model_id: str):
        self.model_id = model_id
        self._load_pipeline()
    
    def get_memory_usage(self) -> dict:
        if torch.cuda.is_available():
            return {
                "allocated": torch.cuda.memory_allocated() / 1024**3,
                "reserved": torch.cuda.memory_reserved() / 1024**3,
                "device": self.device
            }
        return {"device": self.device, "memory": "N/A (CPU mode)"}
    
    def clear_memory(self):
        if torch.cuda.is_available():
            torch.cuda.empty_cache()