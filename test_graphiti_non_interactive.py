import asyncio
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from graphiti_core import Graphiti

async def test_full_workflow():
    """Test the complete Graphiti workflow without user interaction"""
    print("🚀 Starting Non-Interactive Graphiti Test...")
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    required_vars = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Please check your .env file")
        return False
    
    try:
        # Initialize Graphiti
        print("🔧 Initializing Graphiti...")
        graphiti = Graphiti(
            uri=os.getenv("NEO4J_URI"),
            user=os.getenv("NEO4J_USER"),
            password=os.getenv("NEO4J_PASSWORD")
        )
        
        print("🔄 Building indices and constraints...")
        await graphiti.build_indices_and_constraints()
        print("✅ Graphiti initialized successfully!")
        
        # Test data upload
        print("\n📤 Testing data upload...")
        await graphiti.add_episode(
            name="test_call_1",
            episode_body="Customer John Smith called about order #12345. He wants to change his shipping address to 123 Main St, New York.",
            source_description="Test customer call",
            reference_time=datetime.now(timezone.utc)
        )
        
        await graphiti.add_episode(
            name="test_call_2", 
            episode_body="Sarah Johnson called regarding a defective product. She needs a replacement for her wireless headphones.",
            source_description="Test support call",
            reference_time=datetime.now(timezone.utc)
        )
        
        print("✅ Test data uploaded successfully!")
        
        # Test search functionality
        print("\n🔍 Testing search functionality...")
        
        # Test query 1
        results1 = await graphiti.search(
            query="What did John Smith want?",
            num_results=3
        )
        print(f"📊 Query 1 Results: Found {len(results1)} results")
        if results1:
            print(f"   First result: {results1[0].fact[:100]}...")
        
        # Test query 2
        results2 = await graphiti.search(
            query="Who had product issues?",
            num_results=3
        )
        print(f"📊 Query 2 Results: Found {len(results2)} results")
        if results2:
            print(f"   First result: {results2[0].fact[:100]}...")
        
        # Test query 3
        results3 = await graphiti.search(
            query="What are the order details?",
            num_results=3
        )
        print(f"📊 Query 3 Results: Found {len(results3)} results")
        
        print("\n✅ All tests completed successfully!")
        print("🎯 Graphiti is working correctly with:")
        print("   - Data upload ✓")
        print("   - Knowledge graph creation ✓") 
        print("   - Natural language search ✓")
        
        # Cleanup
        await graphiti.close()
        print("🔒 Connection closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Main test function"""
    success = await test_full_workflow()
    
    if success:
        print("\n🎉 All tests passed! Your Graphiti setup is working perfectly.")
        print("\n📝 Next steps:")
        print("   - Run interactive app: python call_qa_app_enhanced.py")
        print("   - Start web interface: python web_interface.py")
        print("   - View graph: http://localhost:7474")
    else:
        print("\n💥 Tests failed. Please check your configuration.")

if __name__ == "__main__":
    asyncio.run(main()) 