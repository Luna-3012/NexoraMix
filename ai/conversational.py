import os
import json
import logging
import requests
from typing import Optional

LOG = logging.getLogger(__name__)

# Config (env)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-3-5-sonnet-20240620")

def _call_claude(prompt: str, max_tokens=200, temperature=0.8) -> Optional[str]:
    if not ANTHROPIC_API_KEY:
        return None
    url = "https://api.anthropic.com/v1/complete"
    headers = {"x-api-key": ANTHROPIC_API_KEY, "Content-Type": "application/json"}
    # Claude completion formulation (simple)
    body = {
        "model": CLAUDE_MODEL,
        "prompt": prompt,
        "max_tokens_to_sample": max_tokens,
        "temperature": temperature
    }
    try:
        r = requests.post(url, headers=headers, json=body, timeout=20)
        r.raise_for_status()
        out = r.json()
        return out.get("completion") or out.get("text") or None
    except Exception as e:
        LOG.debug("Claude call failed: %s", e)
        return None

def template_reply(prompt: str) -> str:
    # Minimal human-readable fallback
    return "Brand Mixologist: I love this combo! (No Claude API key available — showing template reply.)"

def generate_text(prompt: str, max_tokens=200, temperature=0.8) -> str:
    """
    Generate text using Claude only.
    """
    try:
        res = _call_claude(prompt, max_tokens=max_tokens, temperature=temperature)
        if res:
            return res
    except Exception as e:
        LOG.debug("Claude generation failed: %s", e)
    
    return template_reply(prompt)
