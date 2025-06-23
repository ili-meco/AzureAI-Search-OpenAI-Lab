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
      # Generate vector embedding for the query
    # Note: In an actual prompt flow, this would use promptflow.connections
    # For this lab example, we'll use the Azure OpenAI SDK directly
    from openai import AzureOpenAI
    
    aoai_connection = AzureOpenAI(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_version="2023-05-15",
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
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
