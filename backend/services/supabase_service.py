import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

LOG = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = bool(SUPABASE_URL and SUPABASE_KEY)
except ImportError:
    SUPABASE_AVAILABLE = False
    LOG.warning("Supabase library not available")

class SupabaseService:
    def __init__(self):
        self.client = None
        if SUPABASE_AVAILABLE:
            try:
                self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
                LOG.info("Supabase service initialized successfully")
            except Exception as e:
                LOG.error(f"Failed to initialize Supabase client: {e}")
                self.client = None
    
    def create_combo(self, combo_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new brand combo in Supabase"""
        
        if not self.client:
            LOG.warning("Supabase not available, skipping combo creation")
            return None
        
        try:
            # Prepare data for insertion
            insert_data = {
                "name": combo_data.get("name"),
                "slogan": combo_data.get("slogan"),
                "description": combo_data.get("description"),
                "product1": combo_data.get("product1"),
                "product2": combo_data.get("product2"),
                "mode": combo_data.get("mode", "competitive"),
                "votes": 0,
                "host_reaction": combo_data.get("host_reaction"),
                "image_url": combo_data.get("image_url"),
                "compatibility_score": combo_data.get("compatibility_score", 0)
            }
            
            result = self.client.table("brand_combos").insert(insert_data).execute()
            
            if result.data:
                LOG.info(f"Successfully created combo: {combo_data.get('name')}")
                return result.data[0]
            else:
                LOG.error("Failed to create combo - no data returned")
                return None
                
        except Exception as e:
            LOG.error(f"Failed to create combo in Supabase: {e}")
            return None
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top combos from Supabase"""
        
        if not self.client:
            return []
        
        try:
            result = self.client.table("brand_combos")\
                .select("*")\
                .order("votes", desc=True)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            LOG.error(f"Failed to get leaderboard from Supabase: {e}")
            return []
    
    def vote_for_combo(self, combo_id: str) -> bool:
        """Increment vote count for a combo"""
        
        if not self.client:
            return False
        
        try:
            # Use the RPC function to safely increment votes
            result = self.client.rpc("increment_votes", {"combo_id": combo_id}).execute()
            
            LOG.info(f"Successfully voted for combo: {combo_id}")
            return True
            
        except Exception as e:
            LOG.error(f"Failed to vote for combo {combo_id}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """Get overall statistics"""
        
        if not self.client:
            return {"totalCombos": 0, "totalVotes": 0}
        
        try:
            result = self.client.table("brand_combos")\
                .select("votes")\
                .execute()
            
            if result.data:
                total_combos = len(result.data)
                total_votes = sum(combo.get("votes", 0) for combo in result.data)
                
                return {
                    "totalCombos": total_combos,
                    "totalVotes": total_votes
                }
            else:
                return {"totalCombos": 0, "totalVotes": 0}
                
        except Exception as e:
            LOG.error(f"Failed to get stats from Supabase: {e}")
            return {"totalCombos": 0, "totalVotes": 0}

# Global service instance
supabase_service = SupabaseService()