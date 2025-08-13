import os
import logging
import requests
import time
import uuid
from typing import Optional
from pathlib import Path

LOG = logging.getLogger(__name__)

# Configuration
HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
HF_IMAGE_MODEL = os.environ.get("HF_IMAGE_MODEL", "stabilityai/stable-diffusion-xl-base-1.0")
IMG_DIR = Path("data/images")
IMG_DIR.mkdir(parents=True, exist_ok=True)

class ImageGenerationService:
    def __init__(self):
        self.api_token = HF_API_TOKEN
        self.model = HF_IMAGE_MODEL
        self.available = bool(self.api_token)
        
        if not self.available:
            LOG.warning("HuggingFace API token not configured - image generation will use placeholders")
    
    def generate_image(self, prompt: str, brand1: str, brand2: str) -> Optional[str]:
        """Generate an image using Stable Diffusion XL"""
        
        if not self.available:
            return self._get_placeholder_image(brand1, brand2)
        
        try:
            # Enhance the prompt for better results
            enhanced_prompt = self._enhance_prompt(prompt, brand1, brand2)
            
            # Generate unique filename
            timestamp = int(time.time())
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{brand1}_{brand2}_{timestamp}_{unique_id}.png"
            output_path = IMG_DIR / filename
            
            # Call HuggingFace API
            success = self._call_huggingface_api(enhanced_prompt, output_path)
            
            if success:
                LOG.info(f"Successfully generated image: {output_path}")
                return str(output_path)
            else:
                LOG.warning("Image generation failed, using placeholder")
                return self._get_placeholder_image(brand1, brand2)
                
        except Exception as e:
            LOG.error(f"Image generation error: {e}")
            return self._get_placeholder_image(brand1, brand2)
    
    def _enhance_prompt(self, prompt: str, brand1: str, brand2: str) -> str:
        """Enhance the prompt for better image generation"""
        
        # Add quality and style modifiers
        quality_terms = [
            "high quality", "professional photography", "studio lighting",
            "vibrant colors", "sharp focus", "detailed", "8k resolution"
        ]
        
        style_terms = [
            "modern design", "clean composition", "commercial photography",
            "product showcase", "brand identity", "marketing visual"
        ]
        
        enhanced = f"{prompt}, {', '.join(quality_terms[:3])}, {', '.join(style_terms[:2])}"
        
        # Add negative prompt elements
        negative_elements = [
            "blurry", "low quality", "distorted", "ugly", "bad anatomy",
            "text", "watermark", "signature", "logo overlay"
        ]
        
        enhanced += f" | Negative: {', '.join(negative_elements)}"
        
        return enhanced
    
    def _call_huggingface_api(self, prompt: str, output_path: Path) -> bool:
        """Call HuggingFace Inference API"""
        
        url = f"https://api-inference.huggingface.co/models/{self.model}"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        
        # Split prompt and negative prompt
        if " | Negative: " in prompt:
            main_prompt, negative_prompt = prompt.split(" | Negative: ", 1)
        else:
            main_prompt = prompt
            negative_prompt = "blurry, low quality"
        
        payload = {
            "inputs": main_prompt,
            "parameters": {
                "negative_prompt": negative_prompt,
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "width": 1024,
                "height": 1024
            },
            "options": {
                "wait_for_model": True,
                "use_cache": False
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            
            # Check if response is an image
            content_type = response.headers.get("content-type", "")
            if "image" in content_type:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                # Try to parse JSON response
                try:
                    result = response.json()
                    if "error" in result:
                        LOG.error(f"HuggingFace API error: {result['error']}")
                    else:
                        LOG.error(f"Unexpected response format: {result}")
                except:
                    LOG.error(f"Failed to parse API response: {response.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            LOG.error("HuggingFace API request timed out")
            return False
        except requests.exceptions.RequestException as e:
            LOG.error(f"HuggingFace API request failed: {e}")
            return False
        except Exception as e:
            LOG.error(f"Unexpected error in image generation: {e}")
            return False
    
    def _get_placeholder_image(self, brand1: str, brand2: str) -> str:
        """Generate a placeholder image URL"""
        # Use a placeholder service or return a default path
        placeholder_url = f"https://via.placeholder.com/1024x1024/4A90E2/FFFFFF?text={brand1}+x+{brand2}"
        return placeholder_url

# Global service instance
image_service = ImageGenerationService()