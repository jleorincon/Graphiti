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

### Call Q&A Applications

#### 🖥️ Terminal Application
Run the interactive command-line application:
```bash
python call_qa_app.py
```

#### 🌐 Enhanced Terminal Application (Phase 6)
Run the enhanced version with advanced features:
```bash
python call_qa_app_enhanced.py
```

New features in enhanced version:
- **Robust Input Validation**: Better error handling and user guidance
- **Batch File Upload**: Upload multiple files at once using patterns
- **Continuous Questioning**: Ask multiple questions without returning to menu
- **Search Filters**: Filter results by source, time, and other criteria
- **Improved Output**: Better formatted results with emojis and statistics
- **Comprehensive Logging**: Detailed application logs and error tracking

#### 🌍 Web Interface
Run the modern web-based interface:
```bash
# Install web dependencies first
pip install fastapi uvicorn jinja2 python-multipart

# Start the web server
python web_interface.py
```

Then open your browser to: **http://localhost:8000**

Web interface features:
- **Modern UI**: Beautiful, responsive web interface
- **Drag & Drop**: Easy file uploads with multiple file support
- **Real-time Search**: Instant knowledge graph queries
- **Mobile Friendly**: Works on desktop, tablet, and mobile devices
- **API Endpoints**: RESTful API for integration with other systems

#### Example Usage:
1. Upload call data (use provided sample files: `call1.txt`, `call2.txt`, `call3.txt`)
2. Ask questions like:
   - "What was John Doe's order number?"
   - "Which customers had product issues?"
   - "What sales inquiries came in this week?"

### Running Tests

```bash
python test_graphiti.py
# or
python graphiti_simple_test.py
```

## 📁 Project Structure

```
graphiti/
├── call_qa_app.py          # 🎯 Basic Q&A application (Terminal)
├── call_qa_app_enhanced.py # 🚀 Enhanced Q&A app (Phase 6 features)
├── web_interface.py        # 🌐 Modern web interface (FastAPI)
├── monitoring.py           # 📊 Comprehensive monitoring & analytics
├── config.py              # Configuration management
├── graphiti_example.py     # Basic example script
├── graphiti_simple_test.py # Simple test script
├── test_graphiti.py        # Test suite
├── run_example.sh          # Quick start script
├── requirements.txt        # Python dependencies (updated for Phase 6)
├── call1.txt              # Sample call data (John Doe)
├── call2.txt              # Sample call data (Sarah Miller)
├── call3.txt              # Sample call data (Michael Chen)
├── env.example            # Environment variables template
├── graphiti_app.log       # Application logs (auto-generated)
├── errors.log             # Error logs (auto-generated)
├── metrics.db             # Performance metrics database (auto-generated)
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

## 🚀 Deployment & Monitoring

### Local Development

1. Follow the installation steps above
2. Start Neo4j using Docker
3. Set your API keys in environment variables
4. Choose your preferred interface:
   - **Terminal**: `python call_qa_app.py` or `python call_qa_app_enhanced.py`
   - **Web**: `python web_interface.py` → http://localhost:8000

### 📊 Monitoring & Analytics

The enhanced applications include comprehensive monitoring:

```bash
# View application logs
tail -f graphiti_app.log

# Check error logs
tail -f errors.log

# Performance metrics are stored in metrics.db
# Access through the monitoring module
```

**Built-in Analytics:**
- Performance metrics tracking
- Usage statistics and insights
- System health monitoring
- Automatic recommendations
- Error tracking and alerting

### Production Deployment

For production deployment, consider:

1. **Database**: Use a managed Neo4j instance (Neo4j Aura, AWS Neptune, etc.)
2. **Environment Variables**: Use secure secret management
3. **Web Server**: Deploy FastAPI with proper ASGI server (Gunicorn + Uvicorn)
4. **Monitoring**: Set up log aggregation and metrics collection
5. **Security**: Enable HTTPS, rate limiting, and authentication

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Expose web interface port
EXPOSE 8000

# Run web interface by default
CMD ["python", "web_interface.py"]
```

### Docker Compose Example

```yaml
version: '3.8'
services:
  neo4j:
    image: neo4j:latest
    environment:
      NEO4J_AUTH: neo4j/password123
    ports:
      - "7474:7474"
      - "7687:7687"
  
  graphiti-app:
    build: .
    environment:
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: password123
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - neo4j
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