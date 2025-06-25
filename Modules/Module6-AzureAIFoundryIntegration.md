# Module 6: Azure AI Foundry Integration

## Introduction

Azure AI Foundry provides a comprehensive platform for building, deploying, and managing AI solutions at scale. When integrated with Azure AI Search, it enables powerful workflows for creating and deploying search-enhanced AI applications.

In this module, you'll learn how to use Azure AI Foundry to build RAG patterns that leverage Azure AI Search for grounding and deploy them to production endpoints.

## Learning Objectives

By the end of this module, you will be able to:

- Create and configure an Azure AI Foundry project
- Design RAG patterns that integrate with Azure AI Search
- Deploy AI assistants to managed online endpoints
- Integrate AI endpoints with web applications

## Understanding Azure AI Foundry

Azure AI Foundry is a unified platform for AI development that includes:

1. **Project Management**: Organize AI assets and resources
2. **AI Assistants**: Create conversational AI applications with RAG capabilities
3. **Model Catalog**: Repository of AI models and hub models
4. **Deployment Options**: Multiple ways to deploy AI solutions

### Key Components for Search Integration

- **Connections**: Configure access to Azure OpenAI and Azure AI Search
- **Assistants**: Create intelligent assistants with RAG capabilities 
- **Deployment Endpoints**: Host your assistants for production use

## Step 1: Setting Up Azure AI Foundry

### Task: Create Azure AI Foundry Resources

1. In the Azure portal, create an Azure AI resource:
   - **Resource group**: Use `ai-search-lab-rg` (same as previous modules)
   - **Name**: `ai-foundry-<your-initials>`
   - **Region**: Select a region that supports Azure AI (e.g., East US)

2. Set up network isolation for production environments:

   a. In your Azure AI resource, navigate to **Networking**
   
   b. Select **Private access**
   
   c. Configure private endpoints for secure connectivity
   
   d. Set up DNS configuration for your network environment

3. Launch the Azure AI Foundry portal:
   - Click **Launch studio** to open the AI Foundry interface
   - You'll be redirected to [https://ai.azure.com](https://ai.azure.com)

## Step 2: Creating a Project and Configuring Connections

### Task: Create a Project and Add Connections

1. In the AI Foundry portal, create a new project:
   - Click **+ New project**
   - Name: `search-enhanced-chat`
   - Description: `RAG-based chat using Azure AI Search`
   - Resource group: Select the resource group you've been using
   - Click **Create**

2. Add a connection to Azure OpenAI:
   - Navigate to **Project settings > Connections**
   - Click **+ Create**
   - Select **Azure OpenAI**
   - Name: `aoai-connection`
   - Azure subscription: Select your subscription
   - Azure OpenAI resource: Select your Azure OpenAI resource
   - Click **Next**
   - Select your API version (e.g., "2023-05-15")
   - Click **Create**

3. Add a connection to Azure AI Search:
   - Navigate to **Project settings > Connections**
   - Click **+ Create**
   - Select **Azure AI Search**
   - Name: `search-connection`
   - Azure subscription: Select your subscription
   - Azure AI Search resource: Select your search service
   - Click **Next**
   - Select authentication type (API Key or Microsoft Entra ID)
   - Click **Create**

## Step 3: Building a Search-Enhanced AI Assistant

### Task: Create an AI Assistant with RAG

1. In your project, navigate to **AI Assistants** in the left navigation

2. Click **+ Create** to create a new assistant

3. Choose **Custom Assistant** and click **Next**

4. Configure the basic settings:
   - **Name**: `search-enhanced-chat`
   - **Description**: `RAG-based chat using Azure AI Search`
   - **Instructions**: Provide clear instructions for how the assistant should behave

5. Select your Azure OpenAI model:
   - Choose a model like GPT-4o, GPT-4, or GPT-3.5 Turbo
   - Configure settings like temperature and max tokens

6. Under **Add data**, click **+ Add data source**
   - Select **Azure AI Search**
   - Connect your search service using the connection you created
   - Select your index
   - Configure the search parameters:
     - **Search type**: Hybrid (or vector if using vector search)
     - **Content field**: Field containing the document content (e.g., "content")
     - **Top K**: Number of results to return (e.g., 3-5)

7. Customize the system instructions for RAG:

```
You are a helpful AI assistant that uses a search system to find relevant information.
When answering questions, use ONLY the information from the search results provided.
If the search results don't contain enough information to answer the question fully, say so.
Always cite your sources using [doc1], [doc2], etc. at the end of the relevant sentences.
```

8. Test the assistant:
   - Click **Test** in the preview panel
   - Enter a sample query relevant to your data
   - Observe how the assistant retrieves information and generates a response
   - Adjust the configuration as needed to improve results

## Step 4: Enhancing the AI Assistant

### Task: Configure Advanced RAG Features

1. Add query reformulation to improve search results:
   - Go to the assistant settings
   - Under the search configuration, enable query reformulation
   - This helps the assistant create better search queries from user questions
   - Test with complex queries to see the improvement

2. Add post-processing for answers:
   - In the assistant settings, enable answer refinement
   - This helps format responses and ensures proper citations
   - Test with queries that require information from multiple documents

3. Test the enhanced assistant with the same queries as before and observe improvements

## Step 5: Deploying the Assistant to a Production Environment

### Task: Deploy the Assistant to Production

1. In your assistant configuration, click the **Deploy** button

2. Choose **Create deployment**:
   - **Name**: `search-enhanced-chat-deployment`
   - **Description**: Add a detailed description
   - Select appropriate compute resources based on expected traffic
   - Click **Create**

3. Wait for the deployment to complete (this may take a few minutes)

4. Find your deployment endpoint details:
   - Go to **Deployments** in the left navigation
   - Select your deployment
   - Note the endpoint URL and authentication requirements

5. Test the deployed assistant:
   - Use the testing interface provided
   - Or use the API directly with appropriate authentication

## Step 6: Integrating with Web Applications

### Task: Create a Simple Web App that Uses the Deployed Assistant

For production environments, you'd typically integrate your assistant with a web application. Here's a sample Python application that demonstrates this integration:

```python
import requests
import os
from azure.identity import DefaultAzureCredential
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Configuration - replace with your actual values
endpoint_url = "https://your-deployment-endpoint.azurewebsites.net"
api_version = "2023-12-01-preview"

# Use managed identity for authentication in production
credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.json.get('query', '')
    conversation_history = request.json.get('history', [])
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    # Prepare the request for the assistant endpoint
    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json",
        "api-version": api_version
    }
    
    payload = {
        "messages": conversation_history + [{"role": "user", "content": user_query}]
    }
    
    # Call the assistant endpoint
    try:
        response = requests.post(f"{endpoint_url}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

This application:
1. Authenticates to your endpoint using managed identity
2. Forwards user queries to your prompt flow endpoint
3. Returns the responses to the frontend

## Step 7: Security Considerations for Production Deployments

For production deployments of Azure AI Foundry, consider these security best practices:

1. **Network Isolation**:
   - Private endpoints for all connections
   - No public internet access for production workloads
   - VNet integration for secure communication

2. **Identity Management**:
   - System-assigned managed identities for authentication
   - Role-based access control for resource access

3. **Resource Organization**:
   - Data, models, and inference separated
   - Clear boundaries between development and production

> **Note**: For production-ready infrastructure templates, refer to the [Azure OpenAI Landing Zone Accelerator](https://github.com/Azure/azure-openai-landing-zone/tree/main/foundation) which provides comprehensive security patterns.

### Reference Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  ┌────────────┐     ┌─────────────┐     ┌─────────┐  │
│  │            │     │             │     │         │  │
│  │ Web App    ├────►│ AI Foundry  ├────►│ Azure   │  │
│  │            │     │ Endpoint    │     │ Search  │  │
│  └────────────┘     └──────┬──────┘     └─────────┘  │
│                            │                         │
│                            ▼                         │
│                     ┌─────────────┐                  │
│                     │             │                  │
│                     │ Azure       │                  │
│                     │ OpenAI      │                  │
│                     │             │                  │
│                     └─────────────┘                  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## Lab Exercise: Creating a Search-Enhanced AI Solution

### Exercise: Build and Deploy a Complete Solution

Create a solution that:

1. Sets up an AI assistant using Azure AI Foundry
2. Connects it to your Azure AI Search index
3. Enhances the assistant with:
   - Query reformulation
   - Response filtering
   - Citation formatting
4. Deploys the assistant to a production environment
5. Creates a simple web application that integrates with the assistant

Document your implementation, including:
- Assistant configuration
- System prompt customizations
- Deployment configuration
- Sample queries and responses
- Integration approach with web applications

## Next Steps

In the next module, you'll learn how to build a complete search-grounded chat application using Azure OpenAI directly integrated with Azure AI Search.

## Additional Resources

- [Azure AI Foundry documentation](https://learn.microsoft.com/en-us/azure/ai-studio/)
- [Create AI Assistants](https://learn.microsoft.com/en-us/azure/ai-studio/concepts/assistants)
- [RAG pattern with AI Assistants](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/add-data-to-assistant)
- [Deploy AI solutions](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/deploy-models)
- [AI Foundry network isolation](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/configure-managed-network)
