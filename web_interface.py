"""
FastAPI Web Interface for Graphiti Call Q&A Application
Provides a modern web UI for uploading call data and asking questions
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import os
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from typing import List, Optional
import uvicorn

# Try to import graphiti_core - will work when dependencies are installed
try:
    from graphiti_core import Graphiti
except ImportError:
    print("Note: graphiti_core not available in development environment")
    Graphiti = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Graphiti Call Q&A Web Interface",
    description="A web interface for uploading call data and querying knowledge graphs",
    version="1.0.0"
)

# Global Graphiti instance
graphiti_client = None

# Templates setup (we'll create a simple embedded template)
templates = Jinja2Templates(directory="templates") if os.path.exists("templates") else None

async def initialize_graphiti():
    """Initialize Graphiti client"""
    global graphiti_client
    
    if graphiti_client or not Graphiti:
        return graphiti_client
    
    load_dotenv()
    
    try:
        graphiti_client = Graphiti(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password123")
        )
        await graphiti_client.build_indices_and_constraints()
        logger.info("Graphiti client initialized successfully")
        return graphiti_client
    except Exception as e:
        logger.error(f"Failed to initialize Graphiti: {e}")
        return None

@app.on_event("startup")
async def startup_event():
    """Initialize Graphiti on startup"""
    await initialize_graphiti()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Graphiti Call Q&A</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
            }
            .header p {
                font-size: 1.1rem;
                opacity: 0.9;
            }
            .main-content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 0;
                min-height: 500px;
            }
            .upload-section, .query-section {
                padding: 40px;
                display: flex;
                flex-direction: column;
            }
            .upload-section {
                background: #f8fafc;
                border-right: 1px solid #e2e8f0;
            }
            .section-title {
                font-size: 1.5rem;
                margin-bottom: 20px;
                color: #334155;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .upload-form, .query-form {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            textarea, input[type="file"] {
                padding: 15px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            textarea:focus, input[type="file"]:focus {
                outline: none;
                border-color: #4f46e5;
            }
            textarea {
                resize: vertical;
                min-height: 120px;
                font-family: inherit;
            }
            .btn {
                padding: 15px 30px;
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(79, 70, 229, 0.3);
            }
            .results {
                margin-top: 30px;
                padding: 20px;
                background: #f1f5f9;
                border-radius: 10px;
                max-height: 400px;
                overflow-y: auto;
            }
            .result-item {
                background: white;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 8px;
                border-left: 4px solid #4f46e5;
            }
            .fact {
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 8px;
            }
            .metadata {
                font-size: 0.9rem;
                color: #64748b;
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #64748b;
            }
            .status-message {
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
                font-weight: 500;
            }
            .success {
                background: #dcfce7;
                color: #166534;
                border: 1px solid #bbf7d0;
            }
            .error {
                background: #fef2f2;
                color: #dc2626;
                border: 1px solid #fecaca;
            }
            @media (max-width: 768px) {
                .main-content {
                    grid-template-columns: 1fr;
                }
                .upload-section {
                    border-right: none;
                    border-bottom: 1px solid #e2e8f0;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Graphiti Call Q&A</h1>
                <p>Upload call data and ask intelligent questions using AI-powered knowledge graphs</p>
            </div>
            
            <div class="main-content">
                <!-- Upload Section -->
                <div class="upload-section">
                    <h2 class="section-title">📤 Upload Call Data</h2>
                    
                    <div class="upload-form">
                        <textarea 
                            id="callText" 
                            placeholder="Paste your call transcript or summary here..."
                        ></textarea>
                        
                        <button class="btn" onclick="uploadText()">Upload Text</button>
                        
                        <div style="text-align: center; margin: 20px 0; color: #64748b;">— OR —</div>
                        
                        <input type="file" id="fileInput" accept=".txt,.json,.csv" multiple>
                        <button class="btn" onclick="uploadFiles()">Upload Files</button>
                    </div>
                    
                    <div id="uploadStatus"></div>
                </div>
                
                <!-- Query Section -->
                <div class="query-section">
                    <h2 class="section-title">🤖 Ask Questions</h2>
                    
                    <div class="query-form">
                        <textarea 
                            id="queryText" 
                            placeholder="Ask a question about your call data...
                            
Examples:
• What was John's order number?
• Which customers had issues?
• What products were discussed?
• Who needs follow-up?"
                        ></textarea>
                        
                        <button class="btn" onclick="askQuestion()">Search Knowledge Graph</button>
                    </div>
                    
                    <div id="queryResults"></div>
                </div>
            </div>
        </div>
        
        <script>
            async function uploadText() {
                const text = document.getElementById('callText').value;
                const statusDiv = document.getElementById('uploadStatus');
                
                if (!text.trim()) {
                    showStatus('Please enter some text to upload.', 'error');
                    return;
                }
                
                statusDiv.innerHTML = '<div class="loading">Uploading...</div>';
                
                try {
                    const response = await fetch('/upload-text', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        showStatus(`✅ Successfully uploaded: ${result.episode_name}`, 'success');
                        document.getElementById('callText').value = '';
                    } else {
                        showStatus(`❌ Upload failed: ${result.detail}`, 'error');
                    }
                } catch (error) {
                    showStatus(`❌ Error: ${error.message}`, 'error');
                }
            }
            
            async function uploadFiles() {
                const fileInput = document.getElementById('fileInput');
                const files = fileInput.files;
                const statusDiv = document.getElementById('uploadStatus');
                
                if (files.length === 0) {
                    showStatus('Please select files to upload.', 'error');
                    return;
                }
                
                statusDiv.innerHTML = '<div class="loading">Uploading files...</div>';
                
                const formData = new FormData();
                for (let file of files) {
                    formData.append('files', file);
                }
                
                try {
                    const response = await fetch('/upload-files', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        showStatus(`✅ Successfully uploaded ${result.successful_uploads}/${result.total_files} files`, 'success');
                        fileInput.value = '';
                    } else {
                        showStatus(`❌ Upload failed: ${result.detail}`, 'error');
                    }
                } catch (error) {
                    showStatus(`❌ Error: ${error.message}`, 'error');
                }
            }
            
            async function askQuestion() {
                const query = document.getElementById('queryText').value;
                const resultsDiv = document.getElementById('queryResults');
                
                if (!query.trim()) {
                    showQueryResults('Please enter a question.', 'error');
                    return;
                }
                
                resultsDiv.innerHTML = '<div class="loading">Searching knowledge graph...</div>';
                
                try {
                    const response = await fetch('/search', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        displayResults(result.results, query);
                    } else {
                        showQueryResults(`❌ Search failed: ${result.detail}`, 'error');
                    }
                } catch (error) {
                    showQueryResults(`❌ Error: ${error.message}`, 'error');
                }
            }
            
            function displayResults(results, query) {
                const resultsDiv = document.getElementById('queryResults');
                
                if (!results || results.length === 0) {
                    resultsDiv.innerHTML = `
                        <div class="results">
                            <p>🔍 No results found for: "${query}"</p>
                            <p style="margin-top: 10px; color: #64748b;">Try uploading some call data first or rephrasing your question.</p>
                        </div>
                    `;
                    return;
                }
                
                let html = `
                    <div class="results">
                        <h3>🔍 Found ${results.length} result(s) for: "${query}"</h3>
                `;
                
                results.forEach((result, index) => {
                    html += `
                        <div class="result-item">
                            <div class="fact">${result.fact}</div>
                            <div class="metadata">
                                📁 Source: ${result.source_description}<br>
                                📅 Created: ${new Date(result.created_at).toLocaleString()}
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
                resultsDiv.innerHTML = html;
            }
            
            function showStatus(message, type) {
                const statusDiv = document.getElementById('uploadStatus');
                statusDiv.innerHTML = `<div class="status-message ${type}">${message}</div>`;
            }
            
            function showQueryResults(message, type) {
                const resultsDiv = document.getElementById('queryResults');
                resultsDiv.innerHTML = `<div class="status-message ${type}">${message}</div>`;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/upload-text")
async def upload_text(data: dict):
    """Upload text data to Graphiti"""
    if not graphiti_client:
        raise HTTPException(status_code=503, detail="Graphiti not available")
    
    text = data.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    try:
        episode_name = f"web_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        await graphiti_client.add_episode(
            name=episode_name,
            episode_body=text,
            source_description="Web interface upload",
            reference_time=datetime.now(timezone.utc)
        )
        
        return {
            "status": "success",
            "episode_name": episode_name,
            "content_length": len(text)
        }
        
    except Exception as e:
        logger.error(f"Error uploading text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-files")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload multiple files to Graphiti"""
    if not graphiti_client:
        raise HTTPException(status_code=503, detail="Graphiti not available")
    
    successful_uploads = 0
    errors = []
    
    for file in files:
        try:
            content = await file.read()
            text_content = content.decode('utf-8')
            
            if not text_content.strip():
                errors.append(f"File {file.filename} is empty")
                continue
            
            episode_name = f"file_{file.filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            await graphiti_client.add_episode(
                name=episode_name,
                episode_body=text_content,
                source_description=f"Web upload: {file.filename}",
                reference_time=datetime.now(timezone.utc)
            )
            
            successful_uploads += 1
            
        except Exception as e:
            errors.append(f"Error processing {file.filename}: {str(e)}")
    
    return {
        "status": "completed",
        "successful_uploads": successful_uploads,
        "total_files": len(files),
        "errors": errors
    }

@app.post("/search")
async def search_knowledge_graph(data: dict):
    """Search the knowledge graph"""
    if not graphiti_client:
        raise HTTPException(status_code=503, detail="Graphiti not available")
    
    query = data.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="No query provided")
    
    try:
        results = await graphiti_client.search(query=query, num_results=10)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "fact": result.fact,
                "source_description": result.source_description,
                "created_at": result.created_at.isoformat(),
                "relevance_score": getattr(result, 'relevance_score', None)
            })
        
        return {
            "status": "success",
            "results": formatted_results,
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    graphiti_status = "connected" if graphiti_client else "disconnected"
    return {
        "status": "healthy",
        "graphiti": graphiti_status,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting Graphiti Call Q&A Web Interface...")
    print("📍 Application will be available at: http://localhost:8000")
    print("🌐 Neo4j Browser: http://localhost:7474")
    
    uvicorn.run(
        "web_interface:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 