import os
import logging
import requests
import time
import uuid
from typing import Optional

LOG = logging.getLogger(__name__)

HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
HF_IMAGE_MODEL = os.environ.get("HF_IMAGE_MODEL", "stabilityai/stable-diffusion-xl-base-1.0")
PLACEHOLDER = "src/frontend/static/placeholder.png"
IMG_DIR = os.environ.get("IMAGE_DIR", "data/images")
os.makedirs(IMG_DIR, exist_ok=True)

def _call_hf_image(prompt: str, out_path: str, width=512, height=512) -> Optional[str]:
    if not HF_API_TOKEN:
        LOG.warning("HF_API_TOKEN not configured - skipping image generation")
        return None
    
    url = f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": prompt, 
        "options": {"wait_for_model": True}, 
        "parameters": {"width": width, "height": height}
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        
        # HF returns image bytes (content) if configured; else might return base64 or JSON
        content_type = r.headers.get("content-type", "")
        if "image" in content_type:
            with open(out_path, "wb") as f:
                f.write(r.content)
            LOG.info(f"Successfully generated image: {out_path}")
            return out_path
            
        # Try JSON with base64
        data = r.json()
        if isinstance(data, dict) and "artifacts" in data:
            # some HF spaces return data.artifacts[0].base64
            art = data["artifacts"][0]
            b64 = art.get("base64")
            if b64:
                import base64
                try:
                    with open(out_path, "wb") as f:
                        f.write(base64.b64decode(b64))
                    LOG.info(f"Successfully generated image from base64: {out_path}")
                    return out_path
                except Exception as e:
                    LOG.error(f"Failed to decode base64 image data: {e}")
                    return None
                
        # Unrecognized response format
        LOG.error(f"Unrecognized HF response format. Content-Type: {content_type}, Response: {data}")
        return None
        
    except requests.exceptions.Timeout:
        LOG.error(f"HF image generation timed out after 60s for prompt: {prompt[:50]}...")
        return None
    except requests.exceptions.RequestException as e:
        LOG.error(f"HF API request failed: {e} for prompt: {prompt[:50]}...")
        return None
    except Exception as e:
        LOG.error(f"Unexpected error in HF image generation: {e} for prompt: {prompt[:50]}...")
        return None

def generate_image(prompt: str, filename: Optional[str] = None) -> str:
    if not prompt or not prompt.strip():
        LOG.warning("Empty prompt provided for image generation")
        return PLACEHOLDER
    
    prompt = prompt.strip()
    
    if not filename:
        # Generate unique filename using hash, timestamp, and UUID for guaranteed uniqueness
        prompt_hash = abs(hash(prompt))
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]  
        filename = f"{prompt_hash}_{timestamp}_{unique_id}.png"
    
    out_path = os.path.join(IMG_DIR, filename)

    # 1. HuggingFace inference
    path = _call_hf_image(prompt, out_path)
    if path:
        return path

    # 2. Local SD or other provider (not implemented) -> fallback
    LOG.warning(f"No image provider available for prompt: {prompt[:50]}..., returning placeholder")
    return PLACEHOLDER
