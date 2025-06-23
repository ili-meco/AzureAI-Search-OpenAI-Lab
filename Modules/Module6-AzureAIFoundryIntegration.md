# Module 6: Azure AI Foundry Integration

## Introduction

Azure AI Foundry (formerly Azure Machine Learning Studio) provides a comprehensive platform for building, deploying, and managing AI solutions at scale. When integrated with Azure AI Search, it enables powerful workflows for creating and deploying search-enhanced AI applications.

In this module, you'll learn how to use Azure AI Foundry to build prompt flows that leverage Azure AI Search for grounding and deploy them to production endpoints.

## Learning Objectives

By the end of this module, you will be able to:

- Create and configure an Azure AI Foundry project
- Design prompt flows that integrate with Azure AI Search
- Deploy prompt flows to managed online endpoints
- Integrate prompt flows with web applications

## Understanding Azure AI Foundry

Azure AI Foundry is a unified platform for AI development that includes:

1. **Project Management**: Organize AI assets and resources
2. **Prompt Flow**: Visual tool for building AI workflows with LLMs
3. **Model Catalog**: Repository of AI models
4. **Deployment Options**: Multiple ways to deploy AI solutions

### Key Components for Search Integration

- **Connections**: Configure access to Azure OpenAI and Azure AI Search
- **Prompt Flow Tools**: Reusable components for search, LLM integration, etc.
- **Deployment Endpoints**: Host your flows for production use

## Step 1: Setting Up Azure AI Foundry

### Task: Create Azure AI Foundry Resources

1. In the Azure portal, create an Azure AI Foundry resource:
   - **Resource group**: Use `ai-search-lab-rg` (same as previous modules)
   - **Name**: `ai-foundry-<your-initials>`
   - **Region**: Select a region that supports Azure AI Foundry (e.g., East US)

2. Set up network isolation for production environments:

   a. In your AI Foundry resource, navigate to **Networking**
   
   b. Select **Private access**
   
   c. Configure private endpoints for secure connectivity
   
   d. Set up DNS configuration as required by your landing zone architecture

3. Launch the Azure AI Foundry portal:
   - Click **Launch studio** to open the AI Foundry portal
   - You'll be redirected to [https://ml.azure.com](https://ml.azure.com)

## Step 2: Creating a Project and Configuring Connections

### Task: Create a Project and Add Connections

1. In the AI Foundry portal, create a new project:
   - Click **+ Create new** > **Project**
   - Name: `search-enhanced-chat`
   - Description: `RAG-based chat using Azure AI Search`
   - Resource group: Select the resource group you've been using
   - Click **Create**

2. Add a connection to Azure OpenAI:
   - Navigate to **Settings > Connections**
   - Click **+ Create**
   - Select **Azure OpenAI**
   - Name: `aoai-connection`
   - Azure subscription: Select your subscription
   - Azure OpenAI resource: Select your Azure OpenAI resource
   - Click **Next**
   - Select your API version (e.g., "2023-07-01-preview")
   - Click **Create**

3. Add a connection to Azure AI Search:
   - Navigate to **Settings > Connections**
   - Click **+ Create**
   - Select **Azure AI Search**
   - Name: `search-connection`
   - Azure subscription: Select your subscription
   - Azure AI Search resource: Select your search service
   - Click **Next**
   - Select authentication type (API Key or Microsoft Entra ID)
   - Click **Create**

## Step 3: Building a Search-Enhanced Prompt Flow

### Task: Create a Chat with Your Data Prompt Flow

1. In your project, navigate to **Prompt flow** in the left navigation

2. Click **+ Create** to create a new flow

3. Under "Explore gallery", find "Chat with your data" and click **Clone**

4. Set the name to `search-enhanced-chat` and click **Clone**

5. Once the flow opens, examine its structure:
   - Input node: Accepts user query
   - LLM nodes: Processes queries and generates responses
   - Search nodes: Retrieves relevant information from Azure AI Search

6. Configure the connections for each node:

   a. Select the search node (labeled `retrieve` or similar)
   
   b. Under **Connection**, select your `search-connection`
   
   c. Configure the search parameters:
      - **Search service**: Your search service name
      - **Index name**: The index you created in previous modules
      - **Search type**: Hybrid (or vector if using vector search)
      - **Content field**: Field containing the document content (e.g., "content")
      - **Top K**: Number of results to return (e.g., 3-5)
   
   d. Select the LLM node (labeled `generate_answer` or similar)
   
   e. Under **Connection**, select your `aoai-connection`
   
   f. Configure the LLM parameters:
      - **Deployment**: Your GPT model deployment name
      - **API version**: Your API version
      - **Temperature**: 0.1-0.3 for factual responses
      - **Max tokens**: 1000 (or appropriate for your needs)

7. Customize the system prompt:
   - Find the node that defines the system prompt
   - Update it to better suit your use case, for example:

```
You are a helpful AI assistant that uses a search system to find relevant information.
When answering questions, use ONLY the information from the search results provided.
If the search results don't contain enough information to answer the question fully, say so.
Always cite your sources using [doc1], [doc2], etc. at the end of the relevant sentences.
```

8. Test the flow:
   - Click **Test** in the toolbar
   - Enter a sample query relevant to your data
   - Observe how the system retrieves information and generates a response
   - Adjust the configuration as needed to improve results

## Step 4: Enhancing the Prompt Flow

### Task: Add Advanced Features to the Flow

1. Add query reformulation to improve search results:
   - Add a new LLM node before the search node
   - Configure it to reformulate the user's query for better search results
   - Connect it between the input and search nodes
   - Sample prompt:

```
Given the following user question, reformulate it into a search query that will retrieve the most relevant information from a search engine.
Make the query specific and include key terms from the original question.
Original question: {{user_query}}
Reformulated search query:
```

2. Add post-processing to improve answer quality:
   - Add an additional LLM node after the answer generation
   - Configure it to improve the answer formatting and clarity
   - Sample prompt:

```
The following is an AI-generated answer with citations.
Please improve this answer by:
1. Ensuring all information is factual and based on the search results
2. Making sure citations are properly formatted as [docN]
3. Removing any redundant information
4. Making the answer more concise and clear

Original answer:
{{generated_answer}}

Improved answer:
```

3. Test the enhanced flow with the same queries as before and observe improvements

## Step 5: Deploying the Prompt Flow to a Managed Endpoint

### Task: Deploy the Flow to a Managed Online Endpoint

1. In your prompt flow, click the **Deploy** button in the toolbar

2. Choose **Create endpoint**:
   - **Name**: `search-enhanced-chat-endpoint`
   - **Virtual machine**: Select an appropriate VM size (e.g., Standard_D2s_v3)
   - **Instance count**: 2 (for production reliability)
   - Click **Next**

3. Under **Output & connections**, ensure all connections are properly configured:
   - Verify that Azure OpenAI and Azure AI Search connections are selected
   - Click **Next**

4. Review the deployment settings and click **Deploy**

5. Wait for the deployment to complete (this may take 10-15 minutes)

6. Test the endpoint:
   - Once deployed, navigate to **Endpoints** in the left navigation
   - Select your endpoint
   - Go to the **Test** tab
   - Enter a sample query and observe the response

## Step 6: Integrating with Web Applications

### Task: Create a Simple Web App that Uses the Deployed Endpoint

For production environments, you'd typically integrate your prompt flow endpoint with a web application. Here's a sample Flask application that demonstrates this integration:

```python
from flask import Flask, request, jsonify, render_template
import requests
import os
from azure.identity import DefaultAzureCredential

app = Flask(__name__)

# Configuration
endpoint_url = "https://yourendpoint.inference.ml.azure.com/score"  # Replace with your endpoint URL

# Use managed identity for authentication in production
credential = DefaultAzureCredential()
token = credential.get_token("https://ml.azure.com/.default")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.json.get('query', '')
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    # Prepare the request for the prompt flow endpoint
    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": user_query
    }
    
    # Call the prompt flow endpoint
    try:
        response = requests.post(endpoint_url, headers=headers, json=payload)
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

## Step 7: Understanding the Landing Zone Approach

In a landing zone architecture, Azure AI Foundry is deployed with:

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

### Reference Architecture Diagram

```
┌───────────────────────────────────────────────────────────┐
│                 Application Landing Zone                  │
│                                                           │
│  ┌────────────┐     ┌─────────────┐     ┌─────────────┐   │
│  │            │     │             │     │             │   │
│  │ Web App    ├────►│ AI Foundry  ├────►│ Azure AI    │   │
│  │            │     │ Endpoint    │     │ Search      │   │
│  └────────────┘     └──────┬──────┘     └─────────────┘   │
│                            │                              │
│                            ▼                              │
│                     ┌─────────────┐                       │
│                     │             │                       │
│                     │ Azure       │                       │
│                     │ OpenAI      │                       │
│                     │             │                       │
│                     └─────────────┘                       │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

## Lab Exercise: Creating a Search-Enhanced AI Solution

### Exercise: Build and Deploy a Complete Solution

Create a solution that:

1. Sets up a prompt flow using the "Chat with Wikipedia" template
2. Modifies it to use your Azure AI Search index instead
3. Enhances the flow with:
   - Query reformulation
   - Response filtering
   - Citation formatting
4. Deploys the flow to a managed online endpoint
5. Creates a simple web application that integrates with the endpoint

Document your implementation, including:
- Prompt flow design
- System prompt customizations
- Deployment configuration
- Sample queries and responses
- Integration approach with web applications

## Next Steps

In the next module, you'll learn how to build a complete search-grounded chat application using Azure OpenAI directly integrated with Azure AI Search.

## Additional Resources

- [Azure AI Foundry documentation](https://learn.microsoft.com/en-us/azure/ai-studio/)
- [Prompt flow overview](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/flow-overview)
- [RAG pattern with prompt flow](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/retrieval-augmented-generation)
- [Deploy prompt flows](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/deploy-prompt-flow)
- [AI Studio - AzureML manage network isolation](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/configure-managed-network)
