<<<<<<< HEAD
import os
import logging
import json
from typing import Dict, Any, Optional

LOG = logging.getLogger(__name__)

# Claude API configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = bool(ANTHROPIC_API_KEY)
except ImportError:
    ANTHROPIC_AVAILABLE = False
    LOG.warning("Anthropic library not available")

class ClaudeService:
    def __init__(self):
        self.client = None
        if ANTHROPIC_AVAILABLE:
            try:
                self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                LOG.info("Claude service initialized successfully")
            except Exception as e:
                LOG.error(f"Failed to initialize Claude client: {e}")
                self.client = None
    
    def generate_brand_fusion(self, brand1: str, brand2: str, mode: str, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a creative brand fusion using Claude"""
        
        if not self.client:
            return self._fallback_generation(brand1, brand2, mode)
        
        try:
            # Create detailed prompt for Claude
            prompt = self._create_fusion_prompt(brand1, brand2, mode, brand_info)
            
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1000,
                temperature=0.8,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse Claude's response
            content = response.content[0].text
            return self._parse_claude_response(content, brand1, brand2, mode)
            
        except Exception as e:
            LOG.error(f"Claude generation failed: {e}")
            return self._fallback_generation(brand1, brand2, mode)
    
    def _create_fusion_prompt(self, brand1: str, brand2: str, mode: str, brand_info: Dict[str, Any]) -> str:
        """Create a detailed prompt for Claude"""
        
        brand1_info = brand_info.get('brand1_info', f"Information about {brand1}")
        brand2_info = brand_info.get('brand2_info', f"Information about {brand2}")
        
        mode_descriptions = {
            'competitive': 'Create a competitive scenario where both brands battle for supremacy, highlighting their strengths in opposition',
            'collaborative': 'Design a strategic partnership where both brands work together, combining their unique strengths',
            'fusion': 'Imagine a complete merger where both brands become one new entity, blending their characteristics'
        }
        
        mode_desc = mode_descriptions.get(mode, mode_descriptions['competitive'])
        
        prompt = f"""You are a creative brand strategist and marketing genius. Your task is to create an innovative brand fusion concept.

BRAND 1: {brand1}
Background: {brand1_info}

BRAND 2: {brand2}
Background: {brand2_info}

FUSION MODE: {mode}
Approach: {mode_desc}

Create a detailed brand fusion concept with the following structure (respond in JSON format):

{{
  "name": "Creative fusion name (2-4 words)",
  "slogan": "Catchy marketing slogan (under 15 words)",
  "description": "Detailed description of the fusion concept (2-3 sentences)",
  "host_reaction": "Enthusiastic reaction from a brand expert host (1-2 sentences, start with 'Brand Mixologist:')",
  "compatibility_score": "Score from 75-98 representing how well these brands work together",
  "unique_features": ["3-5 unique features of this fusion"],
  "target_audience": "Primary target demographic",
  "image_prompt": "Detailed visual description for image generation (focus on products, colors, style, atmosphere)"
}}

Make it creative, marketable, and exciting! Focus on what makes this combination special and innovative."""

        return prompt
    
    def _parse_claude_response(self, content: str, brand1: str, brand2: str, mode: str) -> Dict[str, Any]:
        """Parse Claude's JSON response"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                # Ensure all required fields are present
                result = {
                    "name": parsed.get("name", f"{brand1} × {brand2}"),
                    "slogan": parsed.get("slogan", f"Where {brand1} meets {brand2}"),
                    "description": parsed.get("description", f"An innovative fusion of {brand1} and {brand2}"),
                    "host_reaction": parsed.get("host_reaction", f"Brand Mixologist: 'This {brand1} and {brand2} combination is absolutely brilliant!'"),
                    "compatibility_score": int(parsed.get("compatibility_score", 85)),
                    "unique_features": parsed.get("unique_features", []),
                    "target_audience": parsed.get("target_audience", "General consumers"),
                    "image_prompt": parsed.get("image_prompt", f"A creative fusion of {brand1} and {brand2} products in a modern, appealing style")
                }
                
                return result
                
        except Exception as e:
            LOG.error(f"Failed to parse Claude response: {e}")
        
        # Fallback if parsing fails
        return self._fallback_generation(brand1, brand2, mode)
    
    def _fallback_generation(self, brand1: str, brand2: str, mode: str) -> Dict[str, Any]:
        """Fallback generation when Claude is not available"""
        import random
        
        mode_templates = {
            'competitive': {
                'names': ['Ultimate Showdown', 'Epic Battle', 'Supreme Clash', 'Champion Duel'],
                'slogans': [
                    f'Where {brand1} meets its match with {brand2}',
                    f'The ultimate showdown: {brand1} vs {brand2}',
                    f'When {brand1} challenges {brand2} to greatness'
                ]
            },
            'collaborative': {
                'names': ['Perfect Alliance', 'United Force', 'Harmony Blend', 'Strategic Union'],
                'slogans': [
                    f'Where {brand1} and {brand2} unite for greatness',
                    f'The perfect partnership of {brand1} and {brand2}',
                    f'When {brand1} joins forces with {brand2}'
                ]
            },
            'fusion': {
                'names': ['Complete Fusion', 'Revolutionary Blend', 'Next Evolution', 'Ultimate Synthesis'],
                'slogans': [
                    f'The revolutionary fusion of {brand1} and {brand2}',
                    f'Where {brand1} and {brand2} become one',
                    f'The next evolution: {brand1} meets {brand2}'
                ]
            }
        }
        
        template = mode_templates.get(mode, mode_templates['competitive'])
        
        return {
            "name": random.choice(template['names']),
            "slogan": random.choice(template['slogans']),
            "description": f"An innovative {mode} concept bringing together the best of {brand1} and {brand2} in an unprecedented way.",
            "host_reaction": f"Brand Mixologist: 'This {brand1} and {brand2} {mode} is absolutely revolutionary! The synergy is incredible!'",
            "compatibility_score": random.randint(75, 95),
            "unique_features": [
                f"Combines {brand1}'s signature style",
                f"Incorporates {brand2}'s innovation",
                "Creates new market opportunities",
                "Appeals to diverse audiences"
            ],
            "target_audience": "Innovation-seeking consumers",
            "image_prompt": f"A creative fusion showing {brand1} and {brand2} products combined in a modern, sleek design with vibrant colors and professional lighting"
        }

# Global service instance
=======
import os
import logging
import json
from typing import Dict, Any, Optional

LOG = logging.getLogger(__name__)

# Claude API configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = bool(ANTHROPIC_API_KEY)
except ImportError:
    ANTHROPIC_AVAILABLE = False
    LOG.warning("Anthropic library not available")

class ClaudeService:
    def __init__(self):
        self.client = None
        if ANTHROPIC_AVAILABLE:
            try:
                self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                LOG.info("Claude service initialized successfully")
            except Exception as e:
                LOG.error(f"Failed to initialize Claude client: {e}")
                self.client = None
    
    def generate_brand_fusion(self, brand1: str, brand2: str, mode: str, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a creative brand fusion using Claude"""
        
        if not self.client:
            return self._fallback_generation(brand1, brand2, mode)
        
        try:
            # Create detailed prompt for Claude
            prompt = self._create_fusion_prompt(brand1, brand2, mode, brand_info)
            
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1000,
                temperature=0.8,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse Claude's response
            content = response.content[0].text
            return self._parse_claude_response(content, brand1, brand2, mode)
            
        except Exception as e:
            LOG.error(f"Claude generation failed: {e}")
            return self._fallback_generation(brand1, brand2, mode)
    
    def _create_fusion_prompt(self, brand1: str, brand2: str, mode: str, brand_info: Dict[str, Any]) -> str:
        """Create a detailed prompt for Claude"""
        
        brand1_info = brand_info.get('brand1_info', f"Information about {brand1}")
        brand2_info = brand_info.get('brand2_info', f"Information about {brand2}")
        
        mode_descriptions = {
            'competitive': 'Create a competitive scenario where both brands battle for supremacy, highlighting their strengths in opposition',
            'collaborative': 'Design a strategic partnership where both brands work together, combining their unique strengths',
            'fusion': 'Imagine a complete merger where both brands become one new entity, blending their characteristics'
        }
        
        mode_desc = mode_descriptions.get(mode, mode_descriptions['competitive'])
        
        prompt = f"""You are a creative brand strategist and marketing genius. Your task is to create an innovative brand fusion concept.

BRAND 1: {brand1}
Background: {brand1_info}

BRAND 2: {brand2}
Background: {brand2_info}

FUSION MODE: {mode}
Approach: {mode_desc}

Create a detailed brand fusion concept with the following structure (respond in JSON format):

{{
  "name": "Creative fusion name (2-4 words)",
  "slogan": "Catchy marketing slogan (under 15 words)",
  "description": "Detailed description of the fusion concept (2-3 sentences)",
  "host_reaction": "Enthusiastic reaction from a brand expert host (1-2 sentences, start with 'Brand Mixologist:')",
  "compatibility_score": "Score from 75-98 representing how well these brands work together",
  "unique_features": ["3-5 unique features of this fusion"],
  "target_audience": "Primary target demographic",
  "image_prompt": "Detailed visual description for image generation (focus on products, colors, style, atmosphere)"
}}

Make it creative, marketable, and exciting! Focus on what makes this combination special and innovative."""

        return prompt
    
    def _parse_claude_response(self, content: str, brand1: str, brand2: str, mode: str) -> Dict[str, Any]:
        """Parse Claude's JSON response"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                # Ensure all required fields are present
                result = {
                    "name": parsed.get("name", f"{brand1} × {brand2}"),
                    "slogan": parsed.get("slogan", f"Where {brand1} meets {brand2}"),
                    "description": parsed.get("description", f"An innovative fusion of {brand1} and {brand2}"),
                    "host_reaction": parsed.get("host_reaction", f"Brand Mixologist: 'This {brand1} and {brand2} combination is absolutely brilliant!'"),
                    "compatibility_score": int(parsed.get("compatibility_score", 85)),
                    "unique_features": parsed.get("unique_features", []),
                    "target_audience": parsed.get("target_audience", "General consumers"),
                    "image_prompt": parsed.get("image_prompt", f"A creative fusion of {brand1} and {brand2} products in a modern, appealing style")
                }
                
                return result
                
        except Exception as e:
            LOG.error(f"Failed to parse Claude response: {e}")
        
        # Fallback if parsing fails
        return self._fallback_generation(brand1, brand2, mode)
    
    def _fallback_generation(self, brand1: str, brand2: str, mode: str) -> Dict[str, Any]:
        """Fallback generation when Claude is not available"""
        import random
        
        mode_templates = {
            'competitive': {
                'names': ['Ultimate Showdown', 'Epic Battle', 'Supreme Clash', 'Champion Duel'],
                'slogans': [
                    f'Where {brand1} meets its match with {brand2}',
                    f'The ultimate showdown: {brand1} vs {brand2}',
                    f'When {brand1} challenges {brand2} to greatness'
                ]
            },
            'collaborative': {
                'names': ['Perfect Alliance', 'United Force', 'Harmony Blend', 'Strategic Union'],
                'slogans': [
                    f'Where {brand1} and {brand2} unite for greatness',
                    f'The perfect partnership of {brand1} and {brand2}',
                    f'When {brand1} joins forces with {brand2}'
                ]
            },
            'fusion': {
                'names': ['Complete Fusion', 'Revolutionary Blend', 'Next Evolution', 'Ultimate Synthesis'],
                'slogans': [
                    f'The revolutionary fusion of {brand1} and {brand2}',
                    f'Where {brand1} and {brand2} become one',
                    f'The next evolution: {brand1} meets {brand2}'
                ]
            }
        }
        
        template = mode_templates.get(mode, mode_templates['competitive'])
        
        return {
            "name": random.choice(template['names']),
            "slogan": random.choice(template['slogans']),
            "description": f"An innovative {mode} concept bringing together the best of {brand1} and {brand2} in an unprecedented way.",
            "host_reaction": f"Brand Mixologist: 'This {brand1} and {brand2} {mode} is absolutely revolutionary! The synergy is incredible!'",
            "compatibility_score": random.randint(75, 95),
            "unique_features": [
                f"Combines {brand1}'s signature style",
                f"Incorporates {brand2}'s innovation",
                "Creates new market opportunities",
                "Appeals to diverse audiences"
            ],
            "target_audience": "Innovation-seeking consumers",
            "image_prompt": f"A creative fusion showing {brand1} and {brand2} products combined in a modern, sleek design with vibrant colors and professional lighting"
        }

# Global service instance
>>>>>>> 0c35e51d1f88f94a184b1dd117166884ad88c5af
claude_service = ClaudeService()