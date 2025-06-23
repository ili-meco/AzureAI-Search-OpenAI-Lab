# RAG Chat Flow with Azure AI Search

## Overview

This prompt flow demonstrates a Retrieval Augmented Generation (RAG) pattern using Azure AI Search for retrieval and Azure OpenAI for generation.

## Input

- **user_query**: The user's question or query
- **chat_history**: (Optional) Array of previous chat interactions

## Flow Steps

### 1. Extract Search Query

```python
def extract_search_query(user_query, chat_history):
    """
    Extract a search query from the user's input to retrieve relevant documents.
    This helps when the user's query contains conversational elements or follow-up questions.
    """
    if not chat_history:
        return user_query
    
    # For follow-up questions, we need to extract the core search intent
    search_query = user_query
    
    # If this is a simple follow-up like "tell me more" or "can you elaborate",
    # we should look at the previous query for context
    if len(user_query.split()) < 5 or "more" in user_query.lower() or "elaborat" in user_query.lower():
        last_user_message = None
        # Find the last user message in the chat history
        for message in reversed(chat_history):
            if message.get("role") == "user":
                last_user_message = message.get("content")
                break
        
        if last_user_message:
            search_query = last_user_message + " " + user_query
    
    return search_query
```

### 2. Vector Search Query

```python
def vector_search(search_query):
    """
    Perform a vector search against Azure AI Search to find relevant documents.
    """
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    import os
    
    # Get search configuration from environment
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_key = os.environ.get("AZURE_SEARCH_KEY")
    index_name = os.environ.get("AZURE_SEARCH_INDEX")
    
    # Initialize the search client
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(search_key)
    )
    
    # Generate vector embedding for the query (simplified, in real scenario use Azure OpenAI)
    from promptflow.connections import AzureOpenAIConnection
    
    aoai_connection = AzureOpenAIConnection(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_base=os.environ.get("AZURE_OPENAI_ENDPOINT")
    )
    
    # Generate embeddings for the query
    embedding_response = aoai_connection.embeddings.create(
        model=os.environ.get("EMBEDDING_MODEL_DEPLOYMENT"),
        input=search_query
    )
    query_vector = embedding_response.data[0].embedding
    
    # Perform the search with hybrid approach
    search_results = search_client.search(
        search_text=search_query,  # Text search
        vector_queries=[{
            "vector": query_vector,
            "k": 3,
            "fields": "vectorEmbedding"
        }],
        select=["id", "title", "content", "category"],
        top=5
    )
    
    # Extract and format results
    documents = []
    for result in search_results:
        documents.append({
            "id": result["id"],
            "title": result["title"],
            "content": result["content"],
            "category": result["category"],
            "score": result["@search.score"]
        })
    
    return documents
```

### 3. Generate Response

```python
def generate_response(user_query, retrieved_documents, chat_history):
    """
    Generate a response using Azure OpenAI with retrieved documents as context.
    """
    import os
    from promptflow.connections import AzureOpenAIConnection
    
    # Initialize OpenAI connection
    aoai_connection = AzureOpenAIConnection(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_base=os.environ.get("AZURE_OPENAI_ENDPOINT")
    )
    
    # Prepare system message with context from retrieved documents
    system_message = "You are an AI assistant that helps answer questions about Azure AI Search. "
    system_message += "Base your answers on the following retrieved documents and cite your sources:\n\n"
    
    # Include retrieved documents in the system message
    for i, doc in enumerate(retrieved_documents, 1):
        system_message += f"Document {i}: {doc['title']}\n"
        system_message += f"Content: {doc['content']}\n\n"
    
    # Add citation instructions
    system_message += "\nWhen responding, please include citations to the relevant documents in your answer using [Document X] format."
    
    # Prepare messages for the API call
    messages = [
        {"role": "system", "content": system_message},
    ]
    
    # Add chat history if available
    if chat_history:
        for message in chat_history:
            messages.append(message)
    
    # Add current user query
    messages.append({"role": "user", "content": user_query})
    
    # Call Azure OpenAI
    response = aoai_connection.chat.completions.create(
        model=os.environ.get("GPT_MODEL_DEPLOYMENT"),
        messages=messages,
        temperature=0.5,
        max_tokens=800
    )
    
    return response.choices[0].message.content
```

## Output

- **response**: The AI-generated response with citations to the retrieved documents

## Deployment Instructions

1. Create and configure an Azure AI Search index with vector search capabilities
2. Set up an Azure OpenAI service with embedding and chat completion models
3. Configure environment variables for search and OpenAI credentials
4. Deploy this prompt flow as an endpoint using Azure AI Foundry
5. Integrate the endpoint with your client application

## Example Query

**User**: "How do I implement hybrid search in Azure AI Search?"

**Response**:
```
To implement hybrid search in Azure AI Search, you'll combine both keyword search and vector search capabilities to create a more comprehensive search experience [Document 4].

Here's how you can implement hybrid search:

1. Create an index with both searchable text fields and vector fields to support both approaches [Document 6].

2. For each document, store both the text content and its vector embeddings (which can be generated using Azure OpenAI Service) [Document 2].

3. When processing a search query, perform both:
   - Traditional keyword search against the text fields
   - Vector search by comparing the query's embedding against your documents' embeddings [Document 2, Document 4]

4. Combine and rank results using custom scoring profiles that can weight both keyword relevance and vector similarity [Document 4].

This hybrid approach is particularly effective for complex search scenarios where you need both exact matches (keyword search) and semantic understanding (vector search). For example, hybrid search can help overcome vocabulary mismatch problems or find conceptually related content even when keywords don't match exactly [Document 3, Document 4].

By implementing hybrid search, you'll get the benefits of both approaches: the precision of keyword search and the semantic understanding of vector search.

[Document 2, Document 3, Document 4, Document 6]
```
