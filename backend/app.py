from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import logging
import random
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Enhanced in-memory storage
combos_store = []
votes_store = {}

# Enhanced brand data with categories
BRAND_DATA = {
    "food": ["McDonald's", "Burger King", "KFC", "Subway", "Pizza Hut", "Domino's", "Taco Bell"],
    "beverages": ["Coca-Cola", "Pepsi", "Starbucks", "Red Bull", "Monster", "Dr Pepper"],
    "tech": ["Apple", "Samsung", "Google", "Microsoft", "Amazon", "Netflix", "Spotify"],
    "fashion": ["Nike", "Adidas", "Gucci", "Louis Vuitton", "H&M", "Zara", "Supreme"],
    "automotive": ["Tesla", "BMW", "Mercedes", "Toyota", "Ford", "Ferrari", "Lamborghini"]
}

# Enhanced combo generation templates
COMBO_TEMPLATES = {
    "competitive": {
        "adjectives": ["Ultimate", "Supreme", "Elite", "Champion", "Legendary", "Epic", "Dominant"],
        "nouns": ["Clash", "Battle", "Showdown", "Duel", "Championship", "Arena", "Combat"],
        "slogans": [
            "Where {product1} meets its match with {product2}",
            "The ultimate showdown: {product1} vs {product2}",
            "When {product1} challenges {product2} to greatness"
        ]
    },
    "collaborative": {
        "adjectives": ["Unified", "Harmonious", "Synergistic", "Blended", "United", "Fused", "Allied"],
        "nouns": ["Alliance", "Partnership", "Unity", "Harmony", "Fusion", "Bond", "Collaboration"],
        "slogans": [
            "Where {product1} and {product2} unite for greatness",
            "The perfect partnership of {product1} and {product2}",
            "When {product1} joins forces with {product2}"
        ]
    },
    "fusion": {
        "adjectives": ["Hybrid", "Merged", "Blended", "Integrated", "Combined", "Synthesized", "Evolved"],
        "nouns": ["Fusion", "Hybrid", "Evolution", "Synthesis", "Metamorphosis", "Transformation", "Revolution"],
        "slogans": [
            "The revolutionary fusion of {product1} and {product2}",
            "Where {product1} and {product2} become one",
            "The next evolution: {product1} meets {product2}"
        ]
    }
}

def get_brand_category(brand):
    """Determine the category of a brand"""
    brand_lower = brand.lower()
    for category, brands in BRAND_DATA.items():
        if any(b.lower() in brand_lower or brand_lower in b.lower() for b in brands):
            return category
    return "general"

def generate_enhanced_combo(product1, product2, mode="competitive"):
    """Enhanced combo generator with better logic"""
    try:
        # Get brand categories
        cat1 = get_brand_category(product1)
        cat2 = get_brand_category(product2)
        
        # Select appropriate template
        template = COMBO_TEMPLATES.get(mode, COMBO_TEMPLATES["competitive"])
        
        # Generate name
        adjective = random.choice(template["adjectives"])
        noun = random.choice(template["nouns"])
        name = f"{adjective} {noun}"
        
        # Generate slogan
        slogan = random.choice(template["slogans"]).format(
            product1=product1, 
            product2=product2
        )
        
        # Generate description based on categories
        if cat1 == cat2:
            description = f"A groundbreaking {cat1} experience that combines the best of {product1}'s heritage with {product2}'s innovation."
        else:
            description = f"An unprecedented cross-industry collaboration bringing together {product1}'s {cat1} expertise with {product2}'s {cat2} mastery."
        
        # Generate host reaction
        reactions = [
            f"This {name} is absolutely revolutionary! The way {product1} and {product2} complement each other is genius!",
            f"I've never seen anything like this {name} before. {product1} and {product2} create pure magic together!",
            f"The {name} represents the future of brand collaboration. {product1} and {product2} are a match made in heaven!",
            f"Incredible! This {name} shows how {product1} and {product2} can push boundaries together!"
        ]
        
        combo = {
            "id": str(uuid.uuid4()),
            "name": name,
            "slogan": slogan,
            "flavor_description": description,
            "host_reaction": f"Brand Mixologist: '{random.choice(reactions)}'",
            "components": {"a": product1, "b": product2},
            "mode": mode,
            "categories": {"a": cat1, "b": cat2},
            "created_at": datetime.utcnow().isoformat() + "Z",
            "votes": 0,
            "compatibility_score": random.randint(75, 98)
        }
        
        return combo
        
    except Exception as e:
        logger.error(f"Error generating combo: {e}")
        raise

@app.route("/")
def home():
    return jsonify({
        "message": "Nexora Brand Mixologist API",
        "status": "healthy",
        "version": "2.0.0",
        "endpoints": ["/generate", "/leaderboard", "/vote", "/health", "/brands"]
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
        
        combo = generate_enhanced_combo(product1, product2, mode)
        combos_store.append(combo)
        votes_store[combo["id"]] = 0
        
        logger.info(f"Generated combo: {combo['name']} (ID: {combo['id']})")
        
        return jsonify({
            "combo": combo,
            "message": "Combo generated successfully"
        })
        
    except Exception as e:
        logger.exception(f"Error in generate endpoint: {e}")
        return jsonify({"error": "Failed to generate combo"}), 500

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    try:
        limit = min(int(request.args.get("limit", 10)), 50)
        
        # Sort combos by votes, then by compatibility score
        sorted_combos = sorted(
            combos_store, 
            key=lambda x: (x.get("votes", 0), x.get("compatibility_score", 0)), 
            reverse=True
        )
        top_combos = sorted_combos[:limit]
        
        logger.info(f"Retrieved {len(top_combos)} combos for leaderboard")
        
        return jsonify({
            "combos": top_combos,
            "total_count": len(combos_store),
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
        
        # Find and update combo
        for combo in combos_store:
            if combo["id"] == combo_id:
                combo["votes"] = combo.get("votes", 0) + 1
                votes_store[combo_id] = combo["votes"]
                
                logger.info(f"Vote registered for {combo_id}: {combo['votes']} total votes")
                
                return jsonify({
                    "status": "voted",
                    "votes": combo["votes"],
                    "combo_name": combo["name"],
                    "message": "Vote registered successfully"
                })
        
        return jsonify({"error": "Combo not found"}), 404
        
    except Exception as e:
        logger.exception(f"Error in vote endpoint: {e}")
        return jsonify({"error": "Failed to register vote"}), 500

@app.route("/brands", methods=["GET"])
def get_brands():
    """Get available brands by category"""
    try:
        category = request.args.get("category", "all")
        
        if category == "all":
            all_brands = []
            for brands in BRAND_DATA.values():
                all_brands.extend(brands)
            return jsonify({"brands": all_brands, "categories": list(BRAND_DATA.keys())})
        
        if category in BRAND_DATA:
            return jsonify({"brands": BRAND_DATA[category], "category": category})
        
        return jsonify({"error": "Invalid category"}), 400
        
    except Exception as e:
        logger.exception(f"Error in brands endpoint: {e}")
        return jsonify({"error": "Failed to retrieve brands"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "nexora-brand-mixologist",
        "version": "2.0.0",
        "combos_count": len(combos_store),
        "total_votes": sum(votes_store.values()),
        "uptime": "running"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # Add sample data for demo
    sample_combos = [
        generate_enhanced_combo("Coca-Cola", "Pepsi", "competitive"),
        generate_enhanced_combo("Nike", "Adidas", "competitive"),
        generate_enhanced_combo("Apple", "Samsung", "fusion")
    ]
    
    for combo in sample_combos:
        combo["votes"] = random.randint(1, 15)
        combos_store.append(combo)
        votes_store[combo["id"]] = combo["votes"]
    
    logger.info("Starting Nexora Brand Mixologist API...")
    app.run(debug=True, port=5000, host="0.0.0.0")