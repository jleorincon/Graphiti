#!/bin/bash

echo "🚀 Graphiti Example Runner"
echo "=========================="

# Check if API key is provided
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OpenAI API key not set!"
    echo ""
    echo "📝 To run this example:"
    echo "1. Get an API key from: https://platform.openai.com/api-keys"
    echo "2. Run: export OPENAI_API_KEY='your-key-here'"
    echo "3. Run: ./run_example.sh"
    echo ""
    echo "Or run directly with: OPENAI_API_KEY='your-key' ./run_example.sh"
    exit 1
fi

echo "✅ API key detected"
echo "🔧 Checking Neo4j status..."

# Check if Neo4j is running
if ! docker ps | grep -q neo4j; then
    echo "❌ Neo4j container not running!"
    echo "Starting Neo4j..."
    docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password123 neo4j:latest
    echo "⏳ Waiting for Neo4j to start..."
    sleep 10
fi

echo "✅ Neo4j is running"
echo "🏃 Running Graphiti example..."
echo ""

# Run the example
python3 graphiti_example.py 