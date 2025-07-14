# Graphiti Knowledge Graph Project

A Python project using Graphiti to build and query knowledge graphs with Neo4j as the backend database.

## 🚀 Features

- **Knowledge Graph Storage**: Store and manage information as interconnected nodes and relationships
- **AI-Powered Search**: Query your knowledge graph using natural language
- **Neo4j Integration**: Robust graph database backend
- **Multiple AI Providers**: Support for OpenAI, Anthropic, and Google AI APIs

## 📋 Prerequisites

- Python 3.8+
- Docker (for Neo4j database)
- API key from at least one AI provider (OpenAI, Anthropic, or Google)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/graphiti.git
   cd graphiti
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv graphiti-env
   source graphiti-env/bin/activate  # On Windows: graphiti-env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   # Neo4j Configuration
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=password123
   
   # AI API Keys (set at least one)
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   GOOGLE_API_KEY=your_google_key_here
   ```

5. **Start Neo4j database:**
   ```bash
   docker run -d --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password123 \
     neo4j:latest
   ```

## 🏃 Usage

### Quick Start

Run the example script:
```bash
./run_example.sh
```

Or run directly with Python:
```bash
export OPENAI_API_KEY='your-key-here'
python graphiti_example.py
```

### Running Tests

```bash
python test_graphiti.py
# or
python graphiti_simple_test.py
```

## 📁 Project Structure

```
graphiti/
├── config.py              # Configuration management
├── graphiti_example.py     # Main example script
├── graphiti_simple_test.py # Simple test script
├── test_graphiti.py        # Test suite
├── run_example.sh          # Quick start script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

The project uses environment variables for configuration. See `config.py` for available options:

- `NEO4J_URI`: Neo4j database connection URI
- `NEO4J_USER`: Neo4j username
- `NEO4J_PASSWORD`: Neo4j password
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `GOOGLE_API_KEY`: Google AI API key

## 🚀 Deployment

### Local Development

1. Follow the installation steps above
2. Start Neo4j using Docker
3. Set your API keys in environment variables
4. Run the example scripts

### Production Deployment

For production deployment, consider:

1. **Database**: Use a managed Neo4j instance (Neo4j Aura, AWS Neptune, etc.)
2. **Environment Variables**: Use secure secret management
3. **Containerization**: Create a Dockerfile for your application
4. **CI/CD**: Set up automated testing and deployment

### Docker Deployment (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "graphiti_example.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Check the [Graphiti documentation](https://github.com/griptape-ai/graphiti-core)
- Open an issue for bugs or feature requests
- Review the example scripts for usage patterns

## 🔗 Links

- [Graphiti Core](https://github.com/griptape-ai/graphiti-core)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [OpenAI API](https://platform.openai.com/docs/) 