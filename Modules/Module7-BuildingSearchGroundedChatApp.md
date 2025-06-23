# Module 7: Building a Search-Grounded Chat Application

## Introduction

In this module, you'll build a complete chat application that integrates Azure OpenAI with Azure AI Search for Retrieval Augmented Generation (RAG). This approach grounds the language model's responses in your specific data, improving accuracy and relevance while reducing hallucinations.

You'll create an end-to-end solution that directly connects Azure OpenAI to Azure AI Search without requiring Azure AI Foundry, giving you more flexibility and direct control over the integration.

## Learning Objectives

By the end of this module, you will be able to:

- Configure Azure OpenAI for direct integration with Azure AI Search
- Understand and implement the RAG pattern for grounded responses
- Build a web application that connects to Azure OpenAI
- Customize the chat experience with advanced features

## Understanding the RAG Pattern

Retrieval Augmented Generation (RAG) combines retrieval systems with generative models:

1. **Retrieval**: When a user asks a question, relevant information is retrieved from a knowledge store (Azure AI Search)

2. **Augmentation**: The retrieved information is combined with the user's query

3. **Generation**: The LLM generates a response based on both the query and retrieved information

![RAG Pattern Diagram](../images/rag-pattern.png)

### Benefits of RAG

- **Accuracy**: Grounds responses in factual information
- **Freshness**: Uses up-to-date information (not just training data)
- **Control**: Ensures responses reflect your specific data
- **Cost efficiency**: Reduces token consumption by focusing the model

## Step 1: Configuring Azure OpenAI for Data Integration

### Task: Configure Azure OpenAI with Azure AI Search

Azure OpenAI provides direct integration with Azure AI Search through its API. This is sometimes referred to as "bring your own data" or "Azure OpenAI on your data."

1. Ensure you have the necessary resources from previous modules:
   - Azure OpenAI service with a deployed model (e.g., gpt-35-turbo or gpt-4)
   - Azure AI Search service with an index containing your data
   - Proper authentication configured (preferably Microsoft Entra ID)

2. Test the integration through the Azure OpenAI Studio:
   
   a. Navigate to your Azure OpenAI resource in the Azure portal
   
   b. Click **Go to Azure OpenAI Studio**
   
   c. In the left navigation, select **Chat playground**
   
   d. Click **Add your data**
   
   e. Select **Add a data source** and choose **Azure AI Search**
   
   f. Configure your search integration:
      - **Subscription**: Select your subscription
      - **Azure AI Search service**: Select your search service
      - **Index**: Select the index you created in previous modules
      - **Authentication type**: Select API Key or Microsoft Entra ID
      - **Search dimensions**: If using vector search, specify the dimensions
      - **Search field mapping**: Map your search fields to the expected schema
      - **Vector search configuration**: Configure if using vector search
   
   g. Click **Next** to configure embedding details if needed
   
   h. Click **Next** to configure additional options:
      - **Enable Search strictness**: Adjust how strictly to filter model responses
      - **Restrict search results based on filter**: Optional filters
      - **Result quantity**: Number of search results to retrieve
   
   i. Click **Save** to complete the configuration

3. Test the integration:
   - Ask questions relevant to your data in the chat playground
   - Review how the model uses the retrieved information
   - Observe the citations and sources

## Step 2: Understanding the API Integration

### Task: Explore the API Structure for Data Grounding

To integrate Azure OpenAI with Azure AI Search in your own applications, you'll need to understand the API structure:

1. Examine the API request structure for Azure OpenAI with data:

```json
{
  "messages": [
    {"role": "system", "content": "You are an AI assistant that helps people find information."},
    {"role": "user", "content": "What features does Azure AI Search support?"}
  ],
  "temperature": 0.3,
  "max_tokens": 800,
  "top_p": 0.95,
  "stream": false,
  "dataSources": [
    {
      "type": "AzureCognitiveSearch",
      "parameters": {
        "endpoint": "https://your-search-service.search.windows.net",
        "indexName": "your-index-name",
        "queryType": "vectorSimpleHybrid",
        "fieldsMapping": {
          "contentFields": ["content"],
          "titleField": "title",
          "urlField": "url",
          "filepathField": "filepath",
          "vectorFields": ["contentVector"]
        },
        "inScope": true,
        "roleInformation": "You are an AI assistant that helps people find information about Azure services.",
        "strictness": 3,
        "topNDocuments": 5,
        "embeddingDeploymentName": "text-embedding-ada-002",
        "filter": null
      }
    }
  ]
}
```

2. Key components in the request:
   - Standard chat messages array
   - LLM parameters (temperature, max_tokens, etc.)
   - `dataSources` array with search configuration
   - Search parameters (endpoint, index, field mappings)

3. Authentication options:
   - API key in header (`api-key: YOUR_API_KEY`)
   - Bearer token for Microsoft Entra ID (`Authorization: Bearer YOUR_TOKEN`)

## Step 3: Building a Web Application

### Task: Create a Chat Web Application

Let's build a simple web application that integrates Azure OpenAI with Azure AI Search using the sample-app-aoai-chatGPT repository as a reference:

1. Clone the repository structure:

```bash
mkdir chat-with-search
cd chat-with-search
mkdir backend
mkdir frontend
mkdir static
```

2. Create a Python backend (`backend/app.py`):

```python
import os
import json
import logging
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

app = Flask(__name__, static_folder="../static")
CORS(app)

# Configuration (in production, use environment variables)
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://your-openai-service.openai.azure.com")
AZURE_OPENAI_MODEL = os.environ.get("AZURE_OPENAI_MODEL", "gpt-35-turbo")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
AZURE_SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT", "https://your-search-service.search.windows.net")
AZURE_SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX", "your-index-name")
AZURE_OPENAI_EMBEDDING_MODEL = os.environ.get("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")

# Use managed identity for authentication in production
USE_MANAGED_IDENTITY = os.environ.get("USE_MANAGED_IDENTITY", "False").lower() == "true"

# System message to guide the assistant's behavior
SYSTEM_MESSAGE = """
You are a helpful AI assistant that helps people find information from the provided search results. 
Answer questions based solely on the search results provided. 
If the search results don't contain relevant information, acknowledge that you don't have enough information to answer.
Always cite your sources using [doc1], [doc2], etc. at the end of each relevant statement.
"""

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        # Get request data
        request_data = request.json
        messages = request_data.get("messages", [])
        
        # Ensure we have the system message
        if messages and messages[0]["role"] != "system":
            messages.insert(0, {"role": "system", "content": SYSTEM_MESSAGE})
        
        # Azure OpenAI API URL
        api_url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_MODEL}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
        
        # Prepare the request payload
        payload = {
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 800,
            "top_p": 0.95,
            "stream": False,
            "dataSources": [
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": AZURE_SEARCH_ENDPOINT,
                        "indexName": AZURE_SEARCH_INDEX,
                        "queryType": "vectorSimpleHybrid",
                        "fieldsMapping": {
                            "contentFields": ["content"],
                            "titleField": "title",
                            "urlField": "url",
                            "filepathField": "filepath",
                            "vectorFields": ["contentVector"]
                        },
                        "inScope": True,
                        "roleInformation": SYSTEM_MESSAGE,
                        "strictness": 3,
                        "topNDocuments": 5,
                        "embeddingDeploymentName": AZURE_OPENAI_EMBEDDING_MODEL,
                        "filter": None
                    }
                }
            ]
        }
        
        # Set up authentication
        headers = {"Content-Type": "application/json"}
        
        if USE_MANAGED_IDENTITY:
            # Use managed identity for authentication (recommended for production)
            credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(
                credential, "https://cognitiveservices.azure.com/.default"
            )
            headers["Authorization"] = f"Bearer {token_provider().token}"
        else:
            # Use API key authentication (simpler for development)
            api_key = os.environ.get("AZURE_OPENAI_KEY")
            headers["api-key"] = api_key
        
        # Make request to Azure OpenAI
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Extract citations and context from the response
        assistant_message = result["choices"][0]["message"]["content"]
        context = []
        citations = []
        
        # Extract citations from tool responses if available
        if "tool_calls" in result["choices"][0]["message"]:
            for tool_call in result["choices"][0]["message"]["tool_calls"]:
                if tool_call.get("type") == "function" and tool_call.get("function", {}).get("name") == "retrieval":
                    try:
                        retrieval_result = json.loads(tool_call["function"]["arguments"])
                        if "citations" in retrieval_result:
                            context.extend(retrieval_result["citations"])
                    except Exception as e:
                        logging.error(f"Error parsing tool call results: {e}")
        
        # If context is available in the response context field
        if "context" in result:
            try:
                search_results = result["context"]["data_sources"][0]["results"]
                for idx, citation in enumerate(search_results):
                    context.append({
                        "title": citation.get("title", f"Citation {idx+1}"),
                        "content": citation.get("content", ""),
                        "filepath": citation.get("filepath", ""),
                        "url": citation.get("url", "")
                    })
            except Exception as e:
                logging.error(f"Error extracting context: {e}")
        
        # Return the formatted response
        return jsonify({
            "message": assistant_message,
            "context": context,
            "citations": citations
        })
    
    except Exception as e:
        logging.error(f"Error processing chat request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

3. Create a simple frontend (`frontend/index.html`):

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search-Grounded Chat</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background-color: #0078d4;
            color: white;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .main-container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }
        
        .chat-container {
            flex: 7;
            display: flex;
            flex-direction: column;
            border-right: 1px solid #e0e0e0;
        }
        
        .citation-container {
            flex: 3;
            overflow-y: auto;
            padding: 1rem;
            background-color: #f9f9f9;
            display: none;
        }
        
        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            background-color: #f5f5f5;
        }
        
        .input-container {
            padding: 1rem;
            border-top: 1px solid #e0e0e0;
            background-color: white;
            display: flex;
        }
        
        .input-container textarea {
            flex: 1;
            padding: 0.5rem;
            border: 1px solid #ccc;
            border-radius: 4px;
            resize: none;
        }
        
        .input-container button {
            margin-left: 0.5rem;
        }
        
        .message {
            margin-bottom: 1rem;
            max-width: 80%;
        }
        
        .user-message {
            margin-left: auto;
            background-color: #0078d4;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 1rem 1rem 0 1rem;
            text-align: right;
        }
        
        .assistant-message {
            margin-right: auto;
            background-color: white;
            padding: 0.5rem 1rem;
            border-radius: 1rem 1rem 1rem 0;
            border: 1px solid #e0e0e0;
        }

        .citation-reference {
            font-size: 0.8rem;
            color: #0078d4;
            cursor: pointer;
            margin: 0 0.2rem;
        }
        
        .citation-panel {
            margin-bottom: 1rem;
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 1rem;
        }
        
        .citation-panel h5 {
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }
        
        .citation-panel p {
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        
        .thinking {
            margin-right: auto;
            background-color: #f0f0f0;
            color: #666;
            padding: 0.5rem 1rem;
            border-radius: 1rem;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Search-Grounded Chat</h1>
    </div>
    
    <div class="main-container">
        <div class="chat-container">
            <div id="messages" class="messages-container">
                <div class="message assistant-message">
                    Hello! I'm an AI assistant that can answer questions about your data. How can I help you today?
                </div>
            </div>
            <div class="input-container">
                <textarea id="userInput" placeholder="Type your message here..." rows="3"></textarea>
                <button id="sendButton" class="btn btn-primary">Send</button>
            </div>
        </div>
        <div id="citationPanel" class="citation-container">
            <h4>Sources</h4>
            <div id="citations"></div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const messagesContainer = document.getElementById('messages');
            const userInput = document.getElementById('userInput');
            const sendButton = document.getElementById('sendButton');
            const citationPanel = document.getElementById('citationPanel');
            const citationsContainer = document.getElementById('citations');
            
            let messages = [
                { role: "system", content: "You are a helpful AI assistant that helps people find information." }
            ];
            
            let activeCitations = [];
            
            userInput.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    sendMessage();
                }
            });
            
            sendButton.addEventListener('click', sendMessage);
            
            function sendMessage() {
                const userMessage = userInput.value.trim();
                if (!userMessage) return;
                
                // Add user message to UI
                addMessage('user', userMessage);
                
                // Add user message to messages array
                messages.push({ role: "user", content: userMessage });
                
                // Clear input
                userInput.value = '';
                
                // Show "thinking" indicator
                const thinkingElement = document.createElement('div');
                thinkingElement.className = 'message thinking';
                thinkingElement.textContent = 'Thinking...';
                messagesContainer.appendChild(thinkingElement);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                
                // Call API
                fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ messages: messages })
                })
                .then(response => response.json())
                .then(data => {
                    // Remove thinking indicator
                    messagesContainer.removeChild(thinkingElement);
                    
                    // Process response
                    if (data.error) {
                        addMessage('assistant', `Error: ${data.error}`);
                    } else {
                        // Add message to UI
                        addMessage('assistant', data.message);
                        
                        // Add to messages array
                        messages.push({ role: "assistant", content: data.message });
                        
                        // Update citations panel
                        updateCitations(data.context);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    messagesContainer.removeChild(thinkingElement);
                    addMessage('assistant', 'Sorry, there was an error processing your request.');
                });
            }
            
            function addMessage(role, content) {
                const messageElement = document.createElement('div');
                messageElement.className = `message ${role}-message`;
                
                if (role === 'assistant') {
                    // Process citations [doc1], [doc2], etc.
                    const processedContent = content.replace(/\[doc(\d+)\]/g, (match, docNum) => {
                        return `<span class="citation-reference" onclick="showCitation(${parseInt(docNum) - 1})">[${docNum}]</span>`;
                    });
                    messageElement.innerHTML = processedContent;
                } else {
                    messageElement.textContent = content;
                }
                
                messagesContainer.appendChild(messageElement);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            function updateCitations(citations) {
                if (!citations || citations.length === 0) {
                    citationPanel.style.display = 'none';
                    return;
                }
                
                activeCitations = citations;
                citationsContainer.innerHTML = '';
                
                citations.forEach((citation, index) => {
                    const citationElement = document.createElement('div');
                    citationElement.className = 'citation-panel';
                    citationElement.innerHTML = `
                        <h5>[${index + 1}] ${citation.title || 'Source ' + (index + 1)}</h5>
                        <p>${truncateText(citation.content, 300)}</p>
                    `;
                    citationsContainer.appendChild(citationElement);
                });
                
                citationPanel.style.display = 'block';
            }
            
            function truncateText(text, maxLength) {
                if (!text) return '';
                if (text.length <= maxLength) return text;
                return text.substring(0, maxLength) + '...';
            }
            
            // Make showCitation available globally
            window.showCitation = function(index) {
                if (!activeCitations || index >= activeCitations.length) return;
                
                citationsContainer.querySelectorAll('.citation-panel').forEach((panel, i) => {
                    if (i === index) {
                        panel.scrollIntoView({ behavior: 'smooth' });
                        panel.style.backgroundColor = '#e6f0ff';
                        setTimeout(() => {
                            panel.style.backgroundColor = '';
                        }, 2000);
                    }
                });
            };
        });
    </script>
</body>
</html>
```

4. Create a build script (`build.py`):

```python
import os
import shutil
import subprocess

def build_frontend():
    print("Building frontend...")
    # Copy the frontend files to the static folder
    if os.path.exists("frontend/index.html"):
        os.makedirs("static", exist_ok=True)
        shutil.copy2("frontend/index.html", "static/index.html")
    print("Frontend build complete")

def setup():
    print("Setting up the project...")
    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("AZURE_OPENAI_ENDPOINT=https://your-openai-service.openai.azure.com\n")
            f.write("AZURE_OPENAI_KEY=your-api-key\n")
            f.write("AZURE_OPENAI_MODEL=gpt-35-turbo\n")
            f.write("AZURE_OPENAI_API_VERSION=2023-12-01-preview\n")
            f.write("AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net\n")
            f.write("AZURE_SEARCH_KEY=your-search-key\n")
            f.write("AZURE_SEARCH_INDEX=your-index-name\n")
            f.write("AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-ada-002\n")
            f.write("USE_MANAGED_IDENTITY=False\n")
        print("Created .env file template. Please update with your own values.")

    # Install Python dependencies
    try:
        subprocess.run(["pip", "install", "flask", "flask-cors", "requests", "python-dotenv", "azure-identity"], check=True)
        print("Installed Python dependencies")
    except subprocess.CalledProcessError:
        print("Error installing dependencies. Please install manually: pip install flask flask-cors requests python-dotenv azure-identity")

if __name__ == "__main__":
    setup()
    build_frontend()
    print("\nBuild complete! Run 'python backend/app.py' to start the application.")
```

5. Create a start script (`start.py`):

```python
import os
import subprocess
import platform
from dotenv import load_dotenv

def start_app():
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if .env exists and has the required variables
    if not os.path.exists(".env"):
        print("Error: .env file not found.")
        print("Please run 'python build.py' first and update the .env file with your Azure settings.")
        return

    print("Starting application...")
    
    # Build the frontend files
    subprocess.run(["python", "build.py"], check=True)
    
    # Start the backend
    print("Starting backend server...")
    subprocess.run(["python", "backend/app.py"], check=True)

if __name__ == "__main__":
    start_app()
```

## Step 4: Customizing the Chat Experience

### Task: Enhance the Chat Application with Advanced Features

Now, let's add advanced features to improve the chat experience:

1. Chat history management:

```python
# Add to backend/app.py

import uuid
from datetime import datetime

# In-memory chat storage (use a database in production)
chat_sessions = {}

@app.route("/api/chats", methods=["GET"])
def get_chats():
    """Get a list of chat sessions"""
    chat_list = [
        {
            "id": session_id,
            "title": session["title"],
            "created": session["created"]
        }
        for session_id, session in chat_sessions.items()
    ]
    return jsonify(chat_list)

@app.route("/api/chats", methods=["POST"])
def create_chat():
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    chat_sessions[session_id] = {
        "title": "New Chat",
        "created": datetime.now().isoformat(),
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE}
        ]
    }
    return jsonify({"id": session_id})

@app.route("/api/chats/<session_id>", methods=["GET"])
def get_chat(session_id):
    """Get messages for a specific chat session"""
    if session_id not in chat_sessions:
        return jsonify({"error": "Chat session not found"}), 404
    
    return jsonify({
        "id": session_id,
        "title": chat_sessions[session_id]["title"],
        "messages": chat_sessions[session_id]["messages"][1:]  # Exclude system message
    })

@app.route("/api/chats/<session_id>/message", methods=["POST"])
def add_message(session_id):
    """Add a message to a chat session and get a response"""
    if session_id not in chat_sessions:
        return jsonify({"error": "Chat session not found"}), 404
    
    request_data = request.json
    user_message = request_data.get("message", "")
    
    if not user_message.strip():
        return jsonify({"error": "Message cannot be empty"}), 400
    
    # Add user message to session
    chat_sessions[session_id]["messages"].append({
        "role": "user",
        "content": user_message
    })
    
    # Copy messages for API call
    messages = chat_sessions[session_id]["messages"].copy()
    
    # Call OpenAI API (similar to existing chat endpoint)
    # ...

    # Update chat title if it's the first message
    if len(chat_sessions[session_id]["messages"]) == 2:  # System + first user message
        chat_sessions[session_id]["title"] = user_message[:30] + ("..." if len(user_message) > 30 else "")
    
    return jsonify(response)
```

2. Advanced citation handling:

```javascript
// Add to frontend JavaScript

function processMessageWithCitations(message, citations) {
    // Extract citation patterns: [doc1], [doc2], etc.
    const regex = /\[doc(\d+)\]/g;
    let match;
    let processedMessage = message;
    let citationLinks = [];
    
    while ((match = regex.exec(message)) !== null) {
        const docNum = parseInt(match[1]);
        if (docNum <= citations.length) {
            const citation = citations[docNum - 1];
            citationLinks.push({
                placeholder: match[0],
                docIndex: docNum - 1,
                title: citation.title || `Source ${docNum}`
            });
        }
    }
    
    // Replace citations with interactive links
    citationLinks.forEach(link => {
        const html = `<span class="citation-reference" data-doc-index="${link.docIndex}">[${link.docIndex + 1}]</span>`;
        processedMessage = processedMessage.replace(link.placeholder, html);
    });
    
    return processedMessage;
}

function showFullCitation(index) {
    const citation = activeCitations[index];
    if (!citation) return;
    
    // Show modal with full citation content
    const modal = document.createElement('div');
    modal.className = 'citation-modal';
    modal.innerHTML = `
        <div class="citation-modal-content">
            <span class="close">&times;</span>
            <h3>${citation.title || `Source ${index + 1}`}</h3>
            <div class="citation-content">${citation.content}</div>
            ${citation.url ? `<p><a href="${citation.url}" target="_blank">View source</a></p>` : ''}
        </div>
    `;
    document.body.appendChild(modal);
    
    const closeBtn = modal.querySelector('.close');
    closeBtn.addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            document.body.removeChild(modal);
        }
    });
}
```

## Step 5: Deploying to Azure

### Task: Deploy the Chat Application to Azure

For production deployment, you can use Azure App Service:

1. Create an Azure App Service:
   - Navigate to the Azure portal
   - Create a new App Service
   - Choose Python runtime
   - Deploy your code using GitHub Actions or Azure DevOps

2. Configure environment variables in App Service:
   - Navigate to your App Service's Configuration
   - Add application settings for all required environment variables
   - Use Key Vault references for secrets

3. Set up managed identity for authentication:
   - Enable system-assigned managed identity for your App Service
   - Grant the necessary permissions to access Azure OpenAI and Azure AI Search

4. Add a sample deployment script (`deploy.py`):

```python
import os
import subprocess
import shutil

def prepare_deployment():
    # Create deployment folder
    os.makedirs("deploy", exist_ok=True)
    
    # Copy necessary files
    shutil.copy2("backend/app.py", "deploy/app.py")
    shutil.copy2("requirements.txt", "deploy/requirements.txt")
    
    # Create static folder and copy frontend files
    os.makedirs("deploy/static", exist_ok=True)
    shutil.copy2("static/index.html", "deploy/static/index.html")
    
    print("Deployment package prepared in 'deploy' folder")
    print("You can now upload this to Azure App Service.")

if __name__ == "__main__":
    prepare_deployment()
```

## Lab Exercise: Implementing RAG with Azure OpenAI

### Exercise: Build a Complete RAG Solution

Create a solution that:

1. Sets up Azure OpenAI and Azure AI Search integration
2. Builds a web application that:
   - Connects to Azure OpenAI with search integration
   - Displays search citations with document content
   - Manages chat sessions for users
   - Includes customization options for search behavior

Document your implementation, including:
- System architecture
- Authentication approach
- Search configuration
- Citation handling
- Performance optimizations
- Screenshots of the working application

## Next Steps

In the next module, you'll learn how to implement a comprehensive landing zone for your AI search solution that incorporates all security, networking, and governance best practices.

## Additional Resources

- [Azure OpenAI on Your Data](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/use-your-data)
- [RAG pattern implementation guide](https://learn.microsoft.com/en-us/azure/architecture/guide/ai/patterns/retrieval-augmented-generation)
- [Sample Chat Application with Azure OpenAI](https://github.com/microsoft/sample-app-aoai-chatGPT)
- [Azure OpenAI REST API reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference)
- [Azure App Service Authentication](https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization)
