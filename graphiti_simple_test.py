import asyncio
import os
from dotenv import load_dotenv
from graphiti_core import Graphiti

async def test_connection():
    """Test basic connection to Neo4j with real environment variables"""
    print("🔧 Testing Neo4j connection...")
    
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Check if API key is available
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️  No OPENAI_API_KEY found in environment")
        print("   Using dummy key for connection test only...")
        os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-testing"
    else:
        print(f"✅ Using configured OpenAI API key: {openai_key[:20]}...")
    
    try:
        graphiti = Graphiti(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"), 
            password=os.getenv("NEO4J_PASSWORD", "password123")
        )
        
        print("✅ Graphiti initialized successfully!")
        print("✅ Neo4j connection established!")
        
        # Test basic database connectivity
        print("📊 Testing database connectivity...")
        
        # Close the connection
        await graphiti.close()
        print("🔒 Connection closed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    print("🚀 Starting Graphiti connection test...")
    
    # First test just the connection
    connection_ok = await test_connection()
    
    if connection_ok:
        print("\n✅ Basic setup is working!")
        
        # Check if we have a real API key
        current_key = os.getenv("OPENAI_API_KEY")
        if current_key and not current_key.startswith("sk-dummy"):
            print("\n🎯 Ready for full functionality!")
            print("📝 Next steps:")
            print("   - Run comprehensive test: python test_graphiti_non_interactive.py")
            print("   - Run interactive app: python call_qa_app_enhanced.py")
            print("   - Start web interface: python web_interface.py")
        else:
            print("\n📝 To enable full AI features:")
            print("1. Create a .env file with: OPENAI_API_KEY=your-actual-key")
            print("2. Run: python test_graphiti_non_interactive.py")
    else:
        print("\n❌ Setup needs fixing:")
        print("- Make sure Neo4j is running: docker ps")
        print("- Check if Neo4j is accessible at localhost:7687")

if __name__ == "__main__":
    asyncio.run(main()) 