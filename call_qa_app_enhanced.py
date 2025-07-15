import asyncio
import os
import glob
import logging
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from typing import List, Optional
import re

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('graphiti_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Global Graphiti Instance (initialized once) ---
graphiti = None

class InputValidator:
    """Utility class for input validation and sanitization."""
    
    @staticmethod
    def validate_file_path(file_path: str) -> tuple[bool, str]:
        """Validate if file path exists and is readable."""
        if not file_path.strip():
            return False, "File path cannot be empty."
        
        if not os.path.exists(file_path):
            return False, f"File not found: '{file_path}'"
        
        if not os.path.isfile(file_path):
            return False, f"Path is not a file: '{file_path}'"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1)  # Try to read first character
            return True, "Valid file path"
        except Exception as e:
            return False, f"Cannot read file: {e}"
    
    @staticmethod
    def validate_query(query: str) -> tuple[bool, str]:
        """Validate search query."""
        if not query.strip():
            return False, "Query cannot be empty."
        
        if len(query.strip()) < 3:
            return False, "Query must be at least 3 characters long."
        
        if len(query) > 500:
            return False, "Query is too long (max 500 characters)."
        
        return True, "Valid query"
    
    @staticmethod
    def validate_choice(choice: str, valid_options: List[str]) -> tuple[bool, str]:
        """Validate user menu choice."""
        if not choice.strip():
            return False, "Please enter a choice."
        
        if choice not in valid_options:
            return False, f"Invalid choice. Please enter one of: {', '.join(valid_options)}"
        
        return True, "Valid choice"

class ResultFormatter:
    """Utility class for formatting search results and output."""
    
    @staticmethod
    def format_search_results(results, query: str) -> str:
        """Format search results in a clean, readable manner."""
        if not results:
            return f"\n🔍 No results found for: '{query}'\n" + "─" * 50
        
        output = []
        output.append(f"\n🔍 Found {len(results)} result(s) for: '{query}'")
        output.append("═" * 60)
        
        for i, res in enumerate(results, 1):
            output.append(f"\n📊 Result {i}:")
            output.append(f"  💡 Fact: {res.fact}")
            
            # Handle different result types that may not have source_description
            if hasattr(res, 'source_description'):
                output.append(f"  📁 Source: {res.source_description}")
            else:
                output.append(f"  📁 Source: Knowledge graph")
            
            if hasattr(res, 'created_at'):
                output.append(f"  📅 Created: {res.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if hasattr(res, 'relevance_score'):
                score_emoji = "🎯" if res.relevance_score > 0.8 else "🎪" if res.relevance_score > 0.6 else "🎨"
                output.append(f"  {score_emoji} Relevance: {res.relevance_score:.2f}")
            
            output.append("─" * 40)
        
        output.append(f"\n💡 Tip: Explore the full graph at http://localhost:7474")
        output.append("═" * 60)
        
        return "\n".join(output)
    
    @staticmethod
    def format_upload_success(episode_name: str, content_length: int) -> str:
        """Format successful upload message."""
        return f"""
✅ SUCCESS: Call data uploaded successfully!
📝 Episode Name: {episode_name}
📊 Content Length: {content_length:,} characters
🌐 View graph at: http://localhost:7474
{'═' * 50}
"""

async def initialize_graphiti():
    """Initializes and returns the Graphiti client with enhanced error handling."""
    global graphiti
    if graphiti:
        logger.info("Graphiti already initialized.")
        return graphiti

    load_dotenv()

    # Validate environment variables
    required_vars = {
        "NEO4J_URI": os.getenv("NEO4J_URI"),
        "NEO4J_USER": os.getenv("NEO4J_USER"), 
        "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        error_msg = f"Missing environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        print("💡 Please check your .env file and ensure all required variables are set.")
        return None

    try:
        logger.info("Initializing Graphiti client...")
        graphiti = Graphiti(
            uri=required_vars["NEO4J_URI"],
            user=required_vars["NEO4J_USER"],
            password=required_vars["NEO4J_PASSWORD"]
        )
        
        print("🔄 Building Graphiti indices and constraints...")
        await graphiti.build_indices_and_constraints()
        
        logger.info("Graphiti client initialized successfully.")
        print("✅ Graphiti client ready!")
        return graphiti
        
    except Exception as e:
        error_msg = f"Failed to initialize Graphiti: {e}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        print("💡 Ensure Neo4j is running and credentials are correct.")
        return None

async def upload_single_file(graphiti_client: Graphiti, file_path: str, source_prefix: str = "") -> bool:
    """Upload a single file to Graphiti."""
    is_valid, validation_msg = InputValidator.validate_file_path(file_path)
    if not is_valid:
        print(f"❌ {validation_msg}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            print(f"⚠️ File '{file_path}' is empty. Skipping.")
            return False
        
        episode_name = f"{source_prefix}{os.path.basename(file_path).split('.')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        source_description = f"Uploaded from file: {os.path.basename(file_path)}"
        
        logger.info(f"Uploading file: {file_path}")
        await graphiti_client.add_episode(
            name=episode_name,
            episode_body=content,
            source_description=source_description,
            reference_time=datetime.now(timezone.utc)
        )
        
        print(ResultFormatter.format_upload_success(episode_name, len(content)))
        logger.info(f"Successfully uploaded: {file_path}")
        return True
        
    except Exception as e:
        error_msg = f"Error uploading file '{file_path}': {e}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        return False

async def batch_upload_files(graphiti_client: Graphiti, pattern: str) -> int:
    """Upload multiple files matching a pattern."""
    try:
        files = glob.glob(pattern)
        if not files:
            print(f"⚠️ No files found matching pattern: '{pattern}'")
            return 0
        
        print(f"📁 Found {len(files)} file(s) matching pattern: '{pattern}'")
        successful_uploads = 0
        
        for file_path in files:
            success = await upload_single_file(graphiti_client, file_path, "batch_")
            if success:
                successful_uploads += 1
        
        print(f"\n📊 Batch upload complete: {successful_uploads}/{len(files)} files uploaded successfully.")
        return successful_uploads
        
    except Exception as e:
        logger.error(f"Error in batch upload: {e}")
        print(f"❌ Batch upload error: {e}")
        return 0

async def upload_call_data(graphiti_client: Graphiti):
    """Enhanced upload function with batch capabilities and better validation."""
    print("\n" + "═" * 50)
    print("📤 UPLOAD CALL DATA")
    print("═" * 50)
    print("1. Enter text directly")
    print("2. Upload single file")
    print("3. Batch upload multiple files")
    print("4. Return to main menu")

    choice = input("Enter your choice (1-4): ").strip()
    
    is_valid, validation_msg = InputValidator.validate_choice(choice, ['1', '2', '3', '4'])
    
    if not is_valid:
        print(f"❌ {validation_msg}")
        return
    
    if choice == '4':
        return
    elif choice == '1':
        await upload_direct_text(graphiti_client)
    elif choice == '2':
        await upload_single_file_interface(graphiti_client)
    elif choice == '3':
        await upload_batch_interface(graphiti_client)

async def upload_direct_text(graphiti_client: Graphiti):
    """Handle direct text input with improved validation."""
    print("\n📝 Enter call transcript/summary below.")
    print("💡 Type 'END' on a new line to finish.")
    print("💡 Type 'CANCEL' to cancel and return.")
    print("─" * 40)
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'END':
                break
            elif line.strip().upper() == 'CANCEL':
                print("❌ Upload cancelled.")
                return
            lines.append(line)
        except KeyboardInterrupt:
            print("\n❌ Upload cancelled.")
            return
    
    content = "\n".join(lines)
    if not content.strip():
        print("⚠️ No content provided. Upload cancelled.")
        return
    
    try:
        episode_name = f"direct_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        await graphiti_client.add_episode(
            name=episode_name,
            episode_body=content,
            source_description="Direct user input",
            reference_time=datetime.now(timezone.utc)
        )
        
        print(ResultFormatter.format_upload_success(episode_name, len(content)))
        logger.info(f"Successfully uploaded direct input: {len(content)} characters")
        
    except Exception as e:
        logger.error(f"Error uploading direct input: {e}")
        print(f"❌ Upload failed: {e}")

async def upload_single_file_interface(graphiti_client: Graphiti):
    """Interface for single file upload."""
    file_path = input("📁 Enter the path to the call data file: ").strip()
    await upload_single_file(graphiti_client, file_path)

async def upload_batch_interface(graphiti_client: Graphiti):
    """Interface for batch file upload."""
    print("\n📁 Batch File Upload")
    print("💡 Examples:")
    print("  - *.txt (all .txt files in current directory)")
    print("  - call*.txt (all files starting with 'call' and ending with '.txt')")
    print("  - /path/to/files/*.json (all .json files in specific directory)")
    
    pattern = input("🔍 Enter file pattern: ").strip()
    if not pattern:
        print("❌ No pattern provided.")
        return
    
    await batch_upload_files(graphiti_client, pattern)

async def search_with_filters(graphiti_client: Graphiti, query: str, source_filter: Optional[str] = None, 
                             days_back: Optional[int] = None, num_results: int = 5):
    """Enhanced search with filtering capabilities."""
    try:
        logger.info(f"Searching with query: '{query}', filters: source={source_filter}, days_back={days_back}")
        
        # For now, use basic search - advanced filtering would require custom Cypher queries
        results = await graphiti_client.search(query=query, num_results=num_results)
        
        # Apply post-search filtering if needed
        if source_filter:
            results = [r for r in results if hasattr(r, 'source_description') and source_filter.lower() in r.source_description.lower()]
        
        if days_back:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            results = [r for r in results if r.created_at >= cutoff_date]
        
        return results
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise e

async def ask_question_enhanced(graphiti_client: Graphiti):
    """Enhanced question interface - asks one question then returns to main menu."""
    print("\n" + "═" * 50)
    print("🤖 ASK QUESTIONS ABOUT YOUR CALL DATA")
    print("═" * 50)
    
    print("\n💬 Enter your question (or 'back' to return to main menu):")
    query = input("❓ ").strip()
    
    if query.lower() in ['exit', 'menu', 'back', '']:
        print("📋 Returning to main menu...")
        return
    elif query.lower() == 'filters':
        await show_filter_options()
        return
    
    is_valid, validation_msg = InputValidator.validate_query(query)
    if not is_valid:
        print(f"❌ {validation_msg}")
        return
    
    # Check for filter commands
    source_filter = None
    days_back = None
    num_results = 5
    
    # Simple filter parsing (could be enhanced)
    if "source:" in query.lower():
        parts = query.split("source:")
        if len(parts) > 1:
            source_filter = parts[1].split()[0]
            query = parts[0].strip()
    
    try:
        print(f"🔍 Searching for: '{query}'...")
        results = await search_with_filters(
            graphiti_client, query, source_filter, days_back, num_results
        )
        
        print(ResultFormatter.format_search_results(results, query))
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        print(f"❌ Search failed: {e}")
    
    print("\n📋 Question completed. Returning to main menu...")

async def show_filter_options():
    """Display available filter options."""
    print("\n🔧 SEARCH FILTER OPTIONS:")
    print("─" * 30)
    print("• Add 'source:filename' to search specific files")
    print("  Example: 'John's order source:call1'")
    print("• More advanced filters coming soon!")
    print("─" * 30)

async def main_menu():
    """Enhanced main menu with better error handling."""
    global graphiti
    
    print("🚀 Initializing Graphiti Call Q&A Application...")
    graphiti = await initialize_graphiti()
    if not graphiti:
        print("💥 Application cannot run without Graphiti connection. Exiting.")
        return

    while True:
        print("\n" + "═" * 60)
        print("🧠 GRAPHITI CALL Q&A APPLICATION - ENHANCED")
        print("═" * 60)
        print("1. 📤 Upload Call Data")
        print("2. 🤖 Ask Questions about Call Data")
        print("3. 📊 View Graph (opens Neo4j Browser)")
        print("4. 🚪 Exit")
        print("─" * 60)

        try:
            choice = input("🎯 Enter your choice (1-4): ").strip()
            
            is_valid, validation_msg = InputValidator.validate_choice(choice, ['1', '2', '3', '4'])
            if not is_valid:
                print(f"❌ {validation_msg}")
                continue

            if choice == '1':
                await upload_call_data(graphiti)
            elif choice == '2':
                await ask_question_enhanced(graphiti)
            elif choice == '3':
                print("🌐 Opening Neo4j Browser...")
                print("📍 URL: http://localhost:7474")
                print("🔑 Login: neo4j / password123")
                os.system("open http://localhost:7474")  # macOS
                # For Linux: os.system("xdg-open http://localhost:7474")
                # For Windows: os.system("start http://localhost:7474")
            elif choice == '4':
                print("\n👋 Thank you for using Graphiti Call Q&A!")
                print("📊 Your knowledge graph data is preserved in Neo4j.")
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main menu: {e}")
            print(f"❌ Unexpected error: {e}")

    # Cleanup
    if graphiti:
        try:
            await graphiti.close()
            logger.info("Graphiti connection closed successfully.")
        except Exception as e:
            logger.error(f"Error closing Graphiti connection: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        print("\n👋 Application terminated by user.")
    except Exception as e:
        logger.error(f"Application crashed: {e}")
        print(f"💥 Application error: {e}") 