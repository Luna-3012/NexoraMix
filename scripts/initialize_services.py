import os
import sys
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_pipeline import run as run_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        'ANTHROPIC_API_KEY',
        'HF_API_TOKEN', 
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.warning("Some services may not work properly. Please check your .env file.")
        return False
    
    logger.info("All required environment variables are set")
    return True

def initialize_knowledge_base():
    """Initialize the brand knowledge base"""
    logger.info("Initializing brand knowledge base...")
    
    try:
        # Run the data pipeline to create embeddings and index
        run_pipeline()
        logger.info("Knowledge base initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize knowledge base: {e}")
        return False

def initialize_directories():
    """Create necessary directories"""
    directories = [
        "data/images",
        "data/chroma", 
        "data/embeddings",
        "data/processed"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def main():
    """Main initialization function"""
    logger.info("Starting Nexora Brand Mixologist initialization...")
    
    # Check environment
    env_ok = check_environment()
    
    # Create directories
    initialize_directories()
    
    # Initialize knowledge base
    kb_ok = initialize_knowledge_base()
    
    if env_ok and kb_ok:
        logger.info("✅ Initialization completed successfully!")
        logger.info("You can now start the backend server with: python backend/app.py")
    else:
        logger.warning("⚠️  Initialization completed with warnings.")
        logger.warning("Some services may not work properly.")
        logger.warning("Please check your environment configuration.")

if __name__ == "__main__":
    main()