# Azure AI Foundry Prompt Flows for RAG

This directory contains sample prompt flows for implementing Retrieval Augmented Generation (RAG) patterns with Azure AI Search.

## Files Included

### `flow.yaml`

The main configuration file for the prompt flow, which defines:

- Inputs and outputs
- Node connections
- Environment variables
- Dependencies

### Component Python Scripts

- **`extract_search_query.py`**: Processes the user query to improve search relevance
- **`vector_search.py`**: Performs vector and keyword search against Azure AI Search
- **`generate_response.py`**: Creates AI responses with citations from search results

### `rag_chat_flow.md`

A detailed markdown documentation of the prompt flow with:

- High-level overview
- Code samples for each component
- Example queries and responses
- Deployment instructions

## How to Use These Files

Follow these steps to use these prompt flows in Azure AI Foundry:

1. **Create a new Prompt Flow project** in Azure AI Foundry
2. **Import the flow.yaml** file into your project
3. **Add the Python component files** to your project
4. **Configure environment variables** with your Azure AI Search and Azure OpenAI credentials
5. **Test the flow** with sample queries
6. **Deploy the flow** as an endpoint for integration with your applications

## Integration with Azure AI Search

These flows rely on an Azure AI Search index that contains:
- Regular searchable text fields
- Vector embeddings for semantic search
- Appropriate RBAC permissions for the Azure AI Foundry service

## Prerequisites

- Azure AI Search instance with vector search enabled
- Azure OpenAI Service with embedding and chat completion models
- Azure AI Foundry workspace with appropriate permissions
- Python packages: azure-search-documents, openai

## Notes

- The code examples simplify some error handling for clarity
- Use the Azure AI Foundry connection management for production credentials
- You can extend these flows with additional components for logging, filtering, etc.
- Consider implementing the flow inside an Azure App Service or Container App for a complete solution
