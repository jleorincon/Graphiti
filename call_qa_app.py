import asyncio
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType # Import EpisodeType for clarity

# --- Global Graphiti Instance (initialized once) ---
graphiti = None

async def initialize_graphiti():
    """Initializes and returns the Graphiti client."""
    global graphiti
    if graphiti:
        print("Graphiti already initialized.")
        return graphiti

    load_dotenv() # Load environment variables from .env

    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not all([neo4j_uri, neo4j_user, neo4j_password, openai_api_key]):
        print("Error: Missing one or more required environment variables (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, OPENAI_API_KEY). Check your .env file.")
        return None

    try:
        graphiti = Graphiti(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password
        )
        print("Graphiti client initialized successfully.")
        # Ensure indices are built (idempotent operation, safe to run multiple times)
        await graphiti.build_indices_and_constraints()
        print("Graphiti indices and constraints are ready.")
        return graphiti
    except Exception as e:
        print(f"Failed to initialize Graphiti: {e}")
        return None

async def upload_call_data(graphiti_client: Graphiti):
    """Handles uploading call data to Graphiti."""
    print("\n--- Upload Call Data ---")
    print("How would you like to provide the call data?")
    print("1. Enter text directly")
    print("2. Upload from a text file")

    choice = input("Enter your choice (1 or 2): ").strip()

    call_content = ""
    source_description = "User uploaded call data"
    call_name = f"call_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    reference_time = datetime.now(timezone.utc)

    if choice == '1':
        print("Please paste the call transcript/summary. Type 'END' on a new line to finish.")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == 'END':
                break
            lines.append(line)
        call_content = "\n".join(lines)
        if not call_content.strip():
            print("No content provided. Returning to main menu.")
            return
    elif choice == '2':
        file_path = input("Enter the path to the call data text file: ").strip()
        if not os.path.exists(file_path):
            print(f"Error: File not found at '{file_path}'. Returning to main menu.")
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                call_content = f.read()
            call_name = os.path.basename(file_path).split('.')[0] # Use filename as episode name
            source_description = f"Uploaded from file: {os.path.basename(file_path)}"
            print(f"Successfully loaded content from {file_path}")
        except Exception as e:
            print(f"Error reading file: {e}. Returning to main menu.")
            return
    else:
        print("Invalid choice. Returning to main menu.")
        return

    if call_content:
        try:
            print("Processing and adding episode to Graphiti...")
            await graphiti_client.add_episode(
                name=call_name,
                episode_body=call_content,
                source_description=source_description,
                reference_time=reference_time,
                # Consider adding a group_id if you want to partition data, e.g., per user or client
                # group_id="customer_calls"
            )
            print(f"✅ Call data successfully added to Graphiti as episode '{call_name}'.")
            print("You can view the graph at http://localhost:7474")
        except Exception as e:
            print(f"❌ Failed to add episode to Graphiti: {e}")
    else:
        print("No content to upload.")


async def ask_question(graphiti_client: Graphiti):
    """Handles asking questions and retrieving answers from Graphiti."""
    print("\n--- Ask a Question ---")
    query = input("Enter your question about the call data (type 'exit' to return): ").strip()

    if query.lower() == 'exit':
        return

    if not query:
        print("No question entered. Returning to main menu.")
        return

    try:
        print(f"Searching Graphiti for: '{query}'...")
        results = await graphiti_client.search(query=query, num_results=5) # Get top 5 results

        if results:
            print("\n--- Answers from Knowledge Graph ---")
            for i, res in enumerate(results):
                print(f"Result {i+1}:")
                print(f"  Fact: {res.fact}")
                print(f"  Source: {res.source_description}")
                print(f"  Created At: {res.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                if hasattr(res, 'relevance_score'):
                    print(f"  Relevance Score: {res.relevance_score:.2f}")
                print("-" * 30)
            print("For more details, explore the graph at http://localhost:7474")
        else:
            print("No relevant information found in the knowledge graph for your question.")

    except Exception as e:
        print(f"❌ An error occurred during search: {e}")


async def main_menu():
    """Displays the main menu and handles user choices."""
    global graphiti
    graphiti = await initialize_graphiti()
    if not graphiti:
        print("Application cannot run without a Graphiti connection. Exiting.")
        return

    while True:
        print("\n--- Graphiti Call Q&A Application ---")
        print("1. Upload Call Data")
        print("2. Ask a Question about Call Data")
        print("3. Exit")

        choice = input("Enter your choice (1, 2, or 3): ").strip()

        if choice == '1':
            await upload_call_data(graphiti)
        elif choice == '2':
            await ask_question(graphiti)
        elif choice == '3':
            print("Exiting application. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

    if graphiti:
        await graphiti.close() # Ensure Graphiti connection is closed on exit

if __name__ == "__main__":
    asyncio.run(main_menu()) 