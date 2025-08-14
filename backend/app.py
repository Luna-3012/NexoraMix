from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import traceback
from datetime import datetime
from services.llama_service import llama_service
from services.claude_service import claude_service
from services.image_service import image_service
from services.supabase_service import supabase_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})


@app.route("/")
def home():
    return jsonify({
        "message": "Nexora Brand Mixologist API",
        "status": "healthy",
        "version": "3.0.0",
        "endpoints": ["/generate", "/leaderboard", "/vote", "/health"]
    })

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        product1 = data.get("product1", "").strip()
        product2 = data.get("product2", "").strip()
        mode = data.get("mode", "competitive")
        
        # Validation
        if not product1 or not product2:
            return jsonify({"error": "Both product1 and product2 are required"}), 400
        
        if len(product1) > 50 or len(product2) > 50:
            return jsonify({"error": "Brand names must be less than 50 characters"}), 400
        
        if product1.lower() == product2.lower():
            return jsonify({"error": "Please select two different brands"}), 400
        
        if mode not in ["competitive", "collaborative", "fusion"]:
            return jsonify({"error": "Invalid mode. Use: competitive, collaborative, or fusion"}), 400
        
        logger.info(f"Generating combo for {product1} + {product2} (mode: {mode})")
        
        # Step 1: Query LlamaIndex for brand information (with fallback)
        try:
            brand_info = llama_service.query_brands(product1, product2)
            logger.info("Successfully retrieved brand information from LlamaIndex")
        except Exception as e:
            logger.warning(f"LlamaIndex query failed, using fallback: {e}")
            brand_info = {
                'brand1_info': f"Popular brand {product1} with strong market presence",
                'brand2_info': f"Well-known brand {product2} with distinctive characteristics",
                'brand1_sources': [],
                'brand2_sources': []
            }
        
        # Step 2: Generate fusion concept with Claude (with fallback)
        try:
            fusion_data = claude_service.generate_brand_fusion(product1, product2, mode, brand_info)
            logger.info("Successfully generated fusion concept with Claude")
        except Exception as e:
            logger.warning(f"Claude generation failed, using fallback: {e}")
            fusion_data = {
                "name": f"{product1} × {product2}",
                "slogan": f"Where {product1} meets {product2}",
                "description": f"An innovative fusion of {product1} and {product2} in {mode} mode",
                "host_reaction": f"Brand Mixologist: 'This {product1} and {product2} combination is absolutely brilliant!'",
                "compatibility_score": 85,
                "unique_features": [
                    f"Combines {product1}'s signature style",
                    f"Incorporates {product2}'s innovation",
                    "Creates new market opportunities"
                ],
                "target_audience": "Innovation-seeking consumers",
                "image_prompt": f"A creative fusion of {product1} and {product2} products in a modern, appealing style"
            }
        
        # Step 3: Generate image with Stable Diffusion (with fallback)
        image_url = None
        try:
            if fusion_data.get("image_prompt"):
                image_url = image_service.generate_image(
                    fusion_data["image_prompt"], 
                    product1, 
                    product2
                )
                logger.info("Successfully generated image")
        except Exception as e:
            logger.warning(f"Image generation failed: {e}")
            # Use placeholder URL
            image_url = f"https://via.placeholder.com/512x512/4A90E2/FFFFFF?text={product1}+x+{product2}"
        
        # Step 4: Prepare combo data
        combo = {
            "name": fusion_data["name"],
            "slogan": fusion_data["slogan"],
            "flavor_description": fusion_data["description"],
            "host_reaction": fusion_data["host_reaction"],
            "components": {"a": product1, "b": product2},
            "mode": mode,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "votes": 0,
            "compatibility_score": fusion_data["compatibility_score"],
            "image_url": image_url,
            "unique_features": fusion_data.get("unique_features", []),
            "target_audience": fusion_data.get("target_audience", "")
        }
        
        # Step 5: Save to Supabase (with fallback)
        try:
            saved_combo = supabase_service.create_combo({
                "name": combo["name"],
                "slogan": combo["slogan"],
                "description": combo["flavor_description"],
                "product1": product1,
                "product2": product2,
                "mode": mode,
                "host_reaction": combo["host_reaction"],
                "image_url": image_url,
                "compatibility_score": combo["compatibility_score"]
            })
            
            if saved_combo:
                combo["id"] = saved_combo["id"]
                logger.info(f"Successfully saved combo to database: {combo['id']}")
            else:
                # Generate a temporary ID for the session
                combo["id"] = f"temp_{int(datetime.utcnow().timestamp())}"
                logger.warning("Failed to save to database, using temporary ID")
        except Exception as e:
            logger.warning(f"Database save failed: {e}")
            combo["id"] = f"temp_{int(datetime.utcnow().timestamp())}"
        
        logger.info(f"Successfully generated combo: {combo['name']} (ID: {combo.get('id', 'unknown')})")
        
        return jsonify({
            "combo": combo,
            "message": "Combo generated successfully"
        })
        
    except Exception as e:
        logger.exception(f"Unexpected error in generate endpoint: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Failed to generate combo. Please try again.",
            "details": str(e) if app.debug else None
        }), 500

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    try:
        limit = min(int(request.args.get("limit", 10)), 50)
        
        # Get combos from Supabase
        top_combos = supabase_service.get_leaderboard(limit)
        
        logger.info(f"Retrieved {len(top_combos)} combos for leaderboard")
        
        return jsonify({
            "combos": top_combos,
            "total_count": len(top_combos),
            "message": "Leaderboard retrieved successfully"
        })
        
    except Exception as e:
        logger.exception(f"Error in leaderboard endpoint: {e}")
        return jsonify({"error": "Failed to retrieve leaderboard"}), 500

@app.route("/vote", methods=["POST"])
def vote():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        combo_id = data.get("combo_id", "").strip()
        if not combo_id:
            return jsonify({"error": "combo_id is required"}), 400
        
        # Vote using Supabase
        success = supabase_service.vote_for_combo(combo_id)
        
        if success:
            return jsonify({
                "status": "voted",
                "message": "Vote registered successfully"
            })
        else:
            return jsonify({"error": "Failed to register vote"}), 500
        
    except Exception as e:
        logger.exception(f"Error in vote endpoint: {e}")
        return jsonify({"error": "Failed to register vote"}), 500

@app.route("/stats", methods=["GET"])
def get_stats():
    """Get overall statistics"""
    try:
        stats = supabase_service.get_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.exception(f"Error in stats endpoint: {e}")
        return jsonify({"error": "Failed to retrieve stats"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "nexora-brand-mixologist",
        "version": "3.0.0",
        "services": {
            "llama_index": llama_service.initialized,
            "claude": claude_service.client is not None,
            "image_generation": image_service.available,
            "supabase": supabase_service.client is not None
        },
        "uptime": "running",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # Initialize services and load brand data
    try:
        # Load brand knowledge base into LlamaIndex
        import json
        from pathlib import Path
        
        kb_file = Path("data/processed/brands_knowledge_base.json")
        if kb_file.exists():
            with open(kb_file, 'r', encoding='utf-8') as f:
                brand_data = json.load(f)
            llama_service.add_documents(brand_data)
            logger.info(f"Loaded {len(brand_data)} brands into LlamaIndex")
        else:
            logger.warning("Brand knowledge base not found - run the data pipeline first")
            
    except Exception as e:
        logger.error(f"Failed to initialize brand data: {e}")
    
    logger.info("Starting Nexora Brand Mixologist API v3.0...")
    app.run(debug=True, port=5000, host="0.0.0.0")