import asyncio
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import openai  # Add OpenAI import for LLM synthesis

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
        print(f"Searching Graphiti for relevant information for: '{query}'...")
        # Retrieve a good number of results. You might need to experiment with this.
        # A larger 'num_results' gives the LLM more context, but also costs more tokens.
        retrieved_results = await graphiti_client.search(query=query, num_results=10) # Increased to 10 for more context

        if retrieved_results:
            # -----------------------------------------------------------
            # NEW LOGIC: Synthesize results using LLM
            # -----------------------------------------------------------
            print("Found relevant information. Synthesizing a human-like answer...")

            # Concatenate the retrieved facts into a single string
            context_facts = []
            for i, res in enumerate(retrieved_results):
                # Handle different result types that may not have source_description
                source_info = getattr(res, 'source_description', 'Knowledge graph')
                context_facts.append(f"Fact {i+1}: {res.fact} (Source: {source_info})")

            context_str = "\n".join(context_facts)

            # Define the prompt for the LLM
            # This is crucial for guiding the LLM's response.
            # Experiment with different phrasings!
            prompt_messages = [
                {"role": "system", "content": "You are a helpful assistant specialized in summarizing information from call logs. Your goal is to provide a concise, coherent, and human-like answer to the user's question based ONLY on the provided context. Do not invent information. If the context does not contain enough information to answer the question fully, state that."},
                {"role": "user", "content": f"Based on the following facts from call logs, please answer the question:\n\nQuestion: {query}\n\nFacts:\n{context_str}\n\nCoherent Answer:"}
            ]

            # Make the LLM call
            try:
                # Ensure OPENAI_API_KEY is loaded correctly (handled by load_dotenv in initialize_graphiti)
                # You might need to explicitly set openai.api_key here if initialize_graphiti doesn't set it globally
                # or pass it as a parameter if using a client instance.
                # For simplicity, assuming os.getenv("OPENAI_API_KEY") makes it available to openai directly.

                openai_client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")) # Ensure this is async
                response = await openai_client.chat.completions.create(
                    model="gpt-4o-mini", # Use a cost-effective model like gpt-4o-mini or gpt-3.5-turbo
                    messages=prompt_messages,
                    temperature=0.7, # Adjust creativity; 0.7 is a good starting point
                    max_tokens=500 # Limit the length of the generated answer
                )

                synthesized_answer = response.choices[0].message.content.strip()

                print("\n--- Synthesized Answer ---")
                print(synthesized_answer)
                print("\n(Note: This answer is generated by an AI based on retrieved facts.)")
                print("\nFor raw facts or visual exploration, visit http://localhost:7474")

            except openai.APIError as e:
                print(f"❌ OpenAI API Error: {e}")
                print("Please check your OpenAI API key and ensure you have sufficient credits.")
            except Exception as e:
                print(f"❌ An unexpected error occurred during LLM synthesis: {e}")

            # -----------------------------------------------------------
            # END NEW LOGIC
            # -----------------------------------------------------------
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