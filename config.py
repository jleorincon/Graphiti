import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")

# AI API Keys (you'll need to set these as environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Print configuration status
def print_config():
    print("🔧 Configuration:")
    print(f"  Neo4j URI: {NEO4J_URI}")
    print(f"  Neo4j User: {NEO4J_USER}")
    print(f"  OpenAI API Key: {'✅ Set' if OPENAI_API_KEY else '❌ Not set'}")
    print(f"  Anthropic API Key: {'✅ Set' if ANTHROPIC_API_KEY else '❌ Not set'}")
    print(f"  Google API Key: {'✅ Set' if GOOGLE_API_KEY else '❌ Not set'}")
    print("")
    print("💡 Tip: Create a .env file in the root directory with your API keys")
    print("   Example: OPENAI_API_KEY=your_key_here") 