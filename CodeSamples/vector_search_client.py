"""
vector_search_client.py
-------------------------
This script provides a client library for performing vector, hybrid, and semantic 
search queries against an Azure AI Search index with vector capabilities.

"""

import os
from typing import List, Dict, Any, Optional
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery, QueryType
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure AI Search configuration
search_service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
search_service_key = os.environ["AZURE_SEARCH_ADMIN_KEY"]
search_index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]

# Azure OpenAI configuration
azure_openai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
azure_openai_key = os.environ["AZURE_OPENAI_KEY"]
azure_openai_embedding_deployment = os.environ["AZURE_OPENAI_EMBEDDING_NAME"]
azure_openai_api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")

class VectorSearchClient:
    """Client library for performing vector search queries against Azure AI Search"""
    
    def __init__(self):
        """Initialize the vector search client"""
        # Initialize Azure AI Search client
        search_credential = AzureKeyCredential(search_service_key)
        self.search_client = SearchClient(
            endpoint=search_service_endpoint,
            index_name=search_index_name,
            credential=search_credential
        )
        
        # Initialize Azure OpenAI client for embeddings
        self.openai_client = AzureOpenAI(
            api_key=azure_openai_key,
            api_version=azure_openai_api_version,
            azure_endpoint=azure_openai_endpoint
        )
    
    def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for a text string using Azure OpenAI.
        
        Args:
            text (str): The text to generate embeddings for
            
        Returns:
            list: The embedding vector
        """
        # Handle empty or None text
        if not text or text.strip() == "":
            return [0.0] * 1536  # Return zero vector for empty text
        
        # Truncate text if too long
        if len(text) > 8000:
            text = text[:8000]
        
        try:
            # Call Azure OpenAI to get embeddings
            response = self.openai_client.embeddings.create(
                input=text,
                model=azure_openai_embedding_deployment
            )
            
            # Extract the embedding vector
            embedding = response.data[0].embedding
            return embedding
        
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            # Return a zero vector in case of error
            return [0.0] * 1536
    
    def vector_search(self, query: str, 
                     top: int = 5, 
                     vector_field: str = "contentVector") -> List[Dict[str, Any]]:
        """
        Perform a pure vector search.
        
        Args:
            query (str): The search query
            top (int): Number of results to return
            vector_field (str): The vector field to search against
            
        Returns:
            list: Search results
        """
        # Generate embeddings for the query
        query_vector = self.generate_embeddings(query)
        
        # Create vectorized query
        vector_query = VectorizedQuery(
            vector=query_vector,
            fields=[vector_field],
            k=top
        )
        
        # Perform vector search
        results = self.search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            select=["id", "title", "content", "category", "sourceUrl", "sourceName"],
            top=top
        )
        
        # Extract and return results
        return [dict(result) for result in results]
    
    def hybrid_search(self, query: str, 
                     top: int = 5, 
                     vector_field: str = "contentVector") -> List[Dict[str, Any]]:
        """
        Perform a hybrid search (combining vector and keyword search).
        
        Args:
            query (str): The search query
            top (int): Number of results to return
            vector_field (str): The vector field to search against
            
        Returns:
            list: Search results
        """
        # Generate embeddings for the query
        query_vector = self.generate_embeddings(query)
        
        # Create vectorized query
        vector_query = VectorizedQuery(
            vector=query_vector,
            fields=[vector_field],
            k=top
        )
        
        # Perform hybrid search
        results = self.search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=["id", "title", "content", "category", "sourceUrl", "sourceName"],
            top=top,
            query_type=QueryType.SIMPLE
        )
        
        # Extract and return results
        return [dict(result) for result in results]
    
    def semantic_search(self, query: str, 
                       top: int = 5, 
                       vector_field: str = "contentVector",
                       semantic_config: str = "semantic-config") -> List[Dict[str, Any]]:
        """
        Perform a semantic search (combining vector search with semantic reranking).
        
        Args:
            query (str): The search query
            top (int): Number of results to return
            vector_field (str): The vector field to search against
            semantic_config (str): The semantic configuration to use
            
        Returns:
            list: Search results
        """
        # Generate embeddings for the query
        query_vector = self.generate_embeddings(query)
        
        # Create vectorized query
        vector_query = VectorizedQuery(
            vector=query_vector,
            fields=[vector_field],
            k=top * 3  # Get more initial results for semantic reranking
        )
        
        # Perform semantic search
        results = self.search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=["id", "title", "content", "category", "sourceUrl", "sourceName"],
            query_type=QueryType.SEMANTIC,
            semantic_configuration_name=semantic_config,
            top=top
        )
        
        # Extract and return results
        return [dict(result) for result in results]

# Example usage
if __name__ == "__main__":
    # Create a search client
    search_client = VectorSearchClient()
    
    # Example query
    query = "What are the benefits of cloud computing?"
    
    print(f"Performing vector search for: '{query}'")
    vector_results = search_client.vector_search(query)
    print(f"Found {len(vector_results)} results")
    
    # Print first result
    if vector_results:
        print("\nTop result:")
        print(f"Title: {vector_results[0]['title']}")
        print(f"Source: {vector_results[0].get('sourceName', 'Unknown')}")
        print(f"Content snippet: {vector_results[0]['content'][:200]}...")
    
    # Perform hybrid search
    print(f"\nPerforming hybrid search for: '{query}'")
    hybrid_results = search_client.hybrid_search(query)
    
    # Print first hybrid result
    if hybrid_results:
        print("\nTop hybrid result:")
        print(f"Title: {hybrid_results[0]['title']}")
        print(f"Source: {hybrid_results[0].get('sourceName', 'Unknown')}")
        print(f"Content snippet: {hybrid_results[0]['content'][:200]}...")
