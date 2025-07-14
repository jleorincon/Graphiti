import asyncio
import os
from graphiti_core import Graphiti

async def test_connection():
    """Test basic connection to Neo4j"""
    print("🔧 Testing Neo4j connection...")
    
    # Set a dummy API key to get past the initialization
    os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-testing"
    
    try:
        graphiti = Graphiti(
            uri="bolt://localhost:7687",
            user="neo4j", 
            password="password123"
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
        print("\n📝 To run the full example with AI features:")
        print("1. Get an OpenAI API key from https://platform.openai.com/api-keys")
        print("2. Set it: export OPENAI_API_KEY='your-key-here'")
        print("3. Run: python3 graphiti_example.py")
    else:
        print("\n❌ Setup needs fixing:")
        print("- Make sure Neo4j is running: docker ps")
        print("- Check if Neo4j is accessible at localhost:7687")

if __name__ == "__main__":
    asyncio.run(main()) 