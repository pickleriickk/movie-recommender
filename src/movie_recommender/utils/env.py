import os
from pathlib import Path
from dotenv import load_dotenv

def load_env():
    """Load environment variables from .env file in the project root"""
    # Get the project root directory (parent of src directory)
    root_dir = Path(__file__).parents[3]  # Go up 3 levels: utils -> movie_recommender -> src -> project_root
    env_path = root_dir / '.env'
    
    if not env_path.exists():
        raise FileNotFoundError(f".env file not found at {env_path}")
    
    load_dotenv(env_path)
    
    # Verify required environment variables
    required_vars = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}") 