import asyncio
import os
from graphiti_core import Graphiti

async def main():
    # Initialize Graphiti with Neo4j
    graphiti = Graphiti(
        uri="bolt://localhost:7687",
        user="neo4j", 
        password="password123"  # This matches what we set in Docker
    )
    
    try:
        print("🚀 Starting Graphiti example...")
        
        # Add some information (episodes)
        print("📝 Adding episodes...")
        
        await graphiti.add_episode(
            name="user_conversation",
            content="John mentioned he loves playing tennis and works at Google",
            source_description="User chat"
        )
        
        await graphiti.add_episode(
            name="user_update", 
            content="John got promoted to Senior Engineer at Google",
            source_description="User update"
        )
        
        print("✅ Episodes added successfully!")
        
        # Search for information
        print("🔍 Searching for information...")
        
        results = await graphiti.search(
            query="What does John do for work?",
            num_results=5
        )
        
        print("📊 Search Results:")
        print(results)
        
        # Try another search
        results2 = await graphiti.search(
            query="What are John's hobbies?",
            num_results=5
        )
        
        print("\n🎾 Hobby Search Results:")
        print(results2)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Neo4j is running and accessible")
    
    finally:
        # Clean up
        await graphiti.close()
        print("🔒 Connection closed")

if __name__ == "__main__":
    asyncio.run(main()) 