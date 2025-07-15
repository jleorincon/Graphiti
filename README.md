# Graphiti Call Q&A Application

A powerful knowledge graph application using **Graphiti** for processing call transcripts and enabling intelligent Q&A interactions. This project includes both command-line tools and a modern web interface for uploading call data and querying the knowledge graph.

## 🎯 What This Project Does

- **Process Call Transcripts**: Upload and analyze call transcripts to build a knowledge graph
- **Intelligent Q&A**: Ask questions about call content using natural language
- **Knowledge Graph**: Automatically extract entities, relationships, and insights from conversations
- **Web Interface**: Modern FastAPI-based web UI for easy interaction
- **Multiple AI Providers**: Support for OpenAI, Anthropic, and Google AI

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
1. **Python 3.8+** - [Download here](https://python.org/downloads/)
2. **Docker** - [Download here](https://docker.com/get-started/)
3. **Git** - [Download here](https://git-scm.com/downloads)

### Required API Keys (at least one)
- **OpenAI API Key** - [Get here](https://platform.openai.com/api-keys)
- **Anthropic API Key** - [Get here](https://console.anthropic.com/)
- **Google AI API Key** - [Get here](https://makersuite.google.com/app/apikey)

## 🚀 Step-by-Step Setup

### Step 1: Clone and Navigate to Project
```bash
git clone <your-repo-url>
cd Graphiti
```

### Step 2: Set Up Python Virtual Environment
```bash
# Create virtual environment
python -m venv graphiti-env

# Activate virtual environment
# On macOS/Linux:
source graphiti-env/bin/activate
# On Windows:
# graphiti-env\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Neo4j Database
```bash
# Start Neo4j using Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:latest

# Wait for Neo4j to start (about 30 seconds)
echo "Waiting for Neo4j to start..."
sleep 30
```

### Step 5: Configure Environment Variables
```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your API keys
nano .env  # or use your preferred editor
```

**Important**: Update your `.env` file with your actual API keys:
```env
# Neo4j Configuration (default values work with Docker setup above)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# AI API Keys (set at least one)
OPENAI_API_KEY=your_actual_openai_key_here
ANTHROPIC_API_KEY=your_actual_anthropic_key_here
GOOGLE_API_KEY=your_actual_google_key_here
```

### Step 6: Verify Setup
```bash
# Test the configuration
python -c "from config import print_config; print_config()"
```

You should see output showing your configuration status with ✅ for properly set API keys.

## 🎮 How to Use the Application

### Option 1: Quick Start with Example Script
```bash
# Make the run script executable
chmod +x run_example.sh

# Run the example (requires OPENAI_API_KEY)
export OPENAI_API_KEY='your-key-here'
./run_example.sh
```

### Option 2: Run Basic Example
```bash
python graphiti_example.py
```

### Option 3: Use Call Q&A Application (Command Line)
```bash
python call_qa_app.py
```

### Option 4: Launch Web Interface
```bash
python web_interface.py
```
Then open your browser to: `http://localhost:8000`

## 📁 Project Structure

```
Graphiti/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config.py                   # Configuration management
├── env.example                 # Environment variables template
├── .env                        # Your actual environment variables (create this)
│
├── graphiti_example.py         # Basic usage example
├── call_qa_app.py             # Main Q&A application
├── call_qa_app_enhanced.py    # Enhanced version with more features
├── web_interface.py           # FastAPI web interface
├── monitoring.py              # Performance monitoring tools
│
├── run_example.sh             # Quick start script
├── test_*.py                  # Test files
└── call*.txt                  # Sample call transcript files
```

## 🔧 Configuration Options

### Neo4j Database
- **URI**: `bolt://localhost:7687` (default)
- **Username**: `neo4j` (default)
- **Password**: `password123` (default for Docker setup)

### AI Providers
You can use any combination of:
- **OpenAI GPT models** (recommended for best results)
- **Anthropic Claude models**
- **Google Gemini models**

## 📖 Usage Examples

### 1. Processing Call Transcripts
```python
import asyncio
from call_qa_app import upload_call_file, ask_question

async def main():
    # Upload a call transcript
    await upload_call_file("call1.txt")
    
    # Ask questions about the call
    answer = await ask_question("What was discussed in the call?")
    print(answer)

asyncio.run(main())
```

### 2. Using the Web Interface
1. Start the web server: `python web_interface.py`
2. Open `http://localhost:8000` in your browser
3. Upload call transcript files (`.txt` format)
4. Ask questions in natural language
5. View extracted knowledge graph insights

### 3. Advanced Q&A Features
```python
# Ask specific questions
await ask_question("Who were the participants?")
await ask_question("What decisions were made?")
await ask_question("What are the action items?")
await ask_question("What topics were discussed?")
```

## 🛠 Troubleshooting

### Common Issues

**1. ModuleNotFoundError: No module named 'fastapi'**
```bash
# Make sure you activated your virtual environment
source graphiti-env/bin/activate
pip install -r requirements.txt
```

**2. Neo4j Connection Issues**
```bash
# Check if Neo4j is running
docker ps | grep neo4j

# If not running, start it
docker start neo4j

# Or recreate it
docker rm neo4j
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password123 neo4j:latest
```

**3. API Key Issues**
- Verify your API keys are correct in the `.env` file
- Check that you have sufficient credits/quota with your AI provider
- Test with: `python -c "from config import print_config; print_config()"`

**4. Permission Issues with Scripts**
```bash
chmod +x run_example.sh
```

### Environment Verification
Run this command to check your setup:
```bash
python -c "
import sys
print(f'Python version: {sys.version}')
try:
    import graphiti_core
    print('✅ graphiti_core installed')
except ImportError:
    print('❌ graphiti_core not installed')
try:
    import fastapi
    print('✅ fastapi installed')
except ImportError:
    print('❌ fastapi not installed - run pip install -r requirements.txt')
"
```

## 🔒 Security Considerations

- **Never commit your `.env` file** to version control
- **Rotate API keys regularly**
- **Use environment-specific configurations** for development vs production
- **Limit API key permissions** to only what's needed

## 📚 Additional Resources

- [Graphiti Core Documentation](https://github.com/getzep/graphiti)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your environment setup
3. Check the logs for error messages
4. Ensure all dependencies are properly installed

## 📝 Development Notes

- The project uses **async/await** patterns for better performance
- **Graphiti** handles the knowledge graph operations
- **FastAPI** provides the modern web interface
- **Neo4j** serves as the graph database backend
- Multiple **AI providers** are supported for flexibility

---

**Happy coding! 🎉** 