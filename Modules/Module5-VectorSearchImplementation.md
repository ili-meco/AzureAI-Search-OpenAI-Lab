# Module 5: Vector Search Implementation

## Introduction

Vector search uses numerical vector embeddings to find similar content based on semantic meaning rather than exact keyword matches. This approach is particularly effective for natural language queries, recommendation systems, and similarity searches.

Azure AI Search enables vector search by storing embeddings in your index and performing similarity searches during query time. When combined with traditional keyword search (hybrid search), it can provide more relevant and contextually accurate results.

## Learning Objectives

By the end of this module, you will be able to:

- Understand vector embeddings and how they work in search
- Generate embeddings using Azure OpenAI
- Configure vector fields in an Azure AI Search index
- Implement vector, hybrid, and semantic-hybrid search

## Understanding Vector Search Concepts

### What Are Vector Embeddings?

Vector embeddings are numerical representations of content (text, images, etc.) in a high-dimensional space where similar items are positioned close to each other. For text, embeddings capture semantic meaning, allowing searches based on concepts rather than exact keywords.

![Vector Embeddings Visualization](../images/vector-embeddings.png)

### Vector Search vs. Keyword Search

| Feature | Vector Search | Keyword Search |
|---------|--------------|----------------|
| **Matching** | Semantic similarity | Exact term matching |
| **Query understanding** | Understands intent and context | Literal interpretation |
| **Language handling** | Better with natural language | Requires specific keywords |
| **Strength** | Finding conceptually related content | Precise term matching |

### Similarity Algorithms

Common similarity measures for vector search include:

1. **Cosine similarity**: Measures the cosine of the angle between vectors (most common)
2. **Euclidean distance**: Measures the straight-line distance between vectors
3. **Dot product**: Measures the product of the vector magnitudes and the cosine of the angle

Azure AI Search primarily uses cosine similarity for vector searches.

## Step 1: Setting Up Azure OpenAI for Embeddings

Vector search requires a model to generate embeddings. Azure OpenAI provides embedding models that are specifically designed for this purpose.

### Task: Create an Azure OpenAI Service

1. In the Azure portal, create an Azure OpenAI resource:
   - **Resource group**: Use `ai-search-lab-rg` (same as previous modules)
   - **Name**: Choose a unique name like `openai-<your-initials>`
   - **Region**: Select a region that supports Azure OpenAI (e.g., East US)
   - **Pricing tier**: Standard S0

2. Once created, go to your Azure OpenAI resource and deploy an embedding model:
   - Navigate to **Model Deployments**
   - Click **Create new deployment**
   - **Model**: `text-embedding-ada-002`
   - **Deployment name**: `text-embedding-ada-002`
   - **Version**: Select the latest available version
   - Click **Create**

### Understanding Embeddings in Azure OpenAI

The `text-embedding-ada-002` model:
- Generates 1536-dimensional embeddings
- Optimized for semantic search scenarios
- Can represent documents or queries as vectors

## Step 2: Creating an Index with Vector Fields

### Task: Define an Index Schema with Vector Support

Create an index that supports vector search using the Azure AI Search REST API:

```http
PUT https://<your-search-service-name>.search.windows.net/indexes/vector-demo-index?api-version=2023-11-01
Content-Type: application/json
api-key: <your-admin-api-key>

{
  "name": "vector-demo-index",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true,
      "searchable": false,
      "filterable": true,
      "retrievable": true
    },
    {
      "name": "title",
      "type": "Edm.String",
      "searchable": true,
      "retrievable": true
    },
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": true,
      "retrievable": true
    },
    {
      "name": "category",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "facetable": true,
      "retrievable": true
    },
    {
      "name": "contentVector",
      "type": "Collection(Edm.Single)",
      "dimensions": 1536,
      "vectorSearchConfiguration": "my-vector-config"
    },
    {
      "name": "titleVector",
      "type": "Collection(Edm.Single)",
      "dimensions": 1536,
      "vectorSearchConfiguration": "my-vector-config"
    }
  ],
  "vectorSearch": {
    "algorithms": {
      "hnsw": {
        "m": 4,
        "efConstruction": 400,
        "efSearch": 500,
        "metric": "cosine"
      }
    },
    "profiles": {
      "myHnswProfile": {
        "algorithm": "hnsw"
      }
    }
  },
  "vectorSearchConfigurations": {
    "my-vector-config": {
      "algorithmConfiguration": "myHnswProfile"
    }
  }
}
```

### Understanding Vector Search Configuration

The index configuration includes:

1. **Vector fields**: `contentVector` and `titleVector` with 1536 dimensions (matching the embedding model)

2. **HNSW algorithm configuration**:
   - `m`: Number of connections per node (higher values = better recall but more memory)
   - `efConstruction`: Quality of graph build (higher values = better quality but slower indexing)
   - `efSearch`: Search quality parameter (higher values = better recall but slower search)
   - `metric`: Similarity measure method (cosine, euclidean, dot product)

3. **Vector search profile**: Links the algorithm configuration to a named profile

4. **Vector search configuration**: Assigns the profile to specific vector fields

## Step 3: Generating Embeddings and Loading Documents

### Task: Generate Embeddings and Add Documents to the Index

Let's create a Python script to:
1. Generate embeddings using Azure OpenAI
2. Add documents with embeddings to our search index

```python
import os
import openai
import json
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Azure OpenAI settings
openai.api_type = "azure"
openai.api_key = "<your-openai-api-key>"
openai.api_base = "https://<your-openai-service>.openai.azure.com"
openai.api_version = "2023-07-01-preview"

# Azure AI Search settings
search_endpoint = "https://<your-search-service>.search.windows.net"
search_key = "<your-search-admin-key>"
index_name = "vector-demo-index"

# Sample documents
documents = [
    {
        "id": "1",
        "title": "Introduction to Azure AI Search",
        "content": "Azure AI Search is a cloud search service that gives developers APIs and tools for building rich search experiences over private, heterogeneous content in web, mobile, and enterprise applications.",
        "category": "Azure Services"
    },
    {
        "id": "2",
        "title": "Vector Search in Azure AI Search",
        "content": "Vector search uses machine learning algorithms to capture semantic meaning of content, enabling more accurate and contextually relevant search results than traditional keyword-based approaches.",
        "category": "Search Technology"
    },
    {
        "id": "3",
        "title": "Hybrid Search Approaches",
        "content": "Hybrid search combines the strengths of keywords and vectors, using both lexical matching and semantic understanding to deliver comprehensive search results.",
        "category": "Search Technology"
    }
]

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def generate_embeddings(text):
    """Generate embeddings for text using Azure OpenAI."""
    response = openai.Embedding.create(
        input=text,
        engine="text-embedding-ada-002"  # Use your deployment name
    )
    return response['data'][0]['embedding']

def index_documents():
    """Generate embeddings and index documents."""
    # Process documents and add embeddings
    docs_with_vectors = []
    
    for doc in documents:
        # Generate embeddings for title and content
        title_vector = generate_embeddings(doc["title"])
        content_vector = generate_embeddings(doc["content"])
        
        # Add vectors to the document
        doc_with_vectors = doc.copy()
        doc_with_vectors["titleVector"] = title_vector
        doc_with_vectors["contentVector"] = content_vector
        
        docs_with_vectors.append(doc_with_vectors)
    
    # Create the request body
    request_body = {
        "value": docs_with_vectors
    }
    
    # Index the documents
    headers = {
        'Content-Type': 'application/json',
        'api-key': search_key
    }
    
    response = requests.post(
        f"{search_endpoint}/indexes/{index_name}/docs/index?api-version=2023-11-01",
        headers=headers,
        json=request_body
    )
    
    if response.status_code == 200:
        print(f"Indexed {len(docs_with_vectors)} documents successfully")
    else:
        print(f"Error indexing documents: {response.text}")

if __name__ == "__main__":
    index_documents()
```

For a production scenario, use managed identity instead of API keys:

```python
# Replace API key authentication with managed identity
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential

credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token.token}'
}
```

## Step 4: Implementing Vector Queries

### Task: Test Vector Search Queries

Let's create a Python script to execute vector search queries:

```python
import openai
import requests
import json

# Configuration
openai.api_type = "azure"
openai.api_key = "<your-openai-api-key>"
openai.api_base = "https://<your-openai-service>.openai.azure.com"
openai.api_version = "2023-07-01-preview"

search_endpoint = "https://<your-search-service>.search.windows.net"
search_key = "<your-search-admin-key>"
index_name = "vector-demo-index"

def generate_embedding(text):
    """Generate embeddings for the query text."""
    response = openai.Embedding.create(
        input=text,
        engine="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

def vector_search(query_text, search_type="vector"):
    """Perform vector search with the given query."""
    # Generate query embedding
    query_vector = generate_embedding(query_text)
    
    # Prepare the search request
    headers = {
        'Content-Type': 'application/json',
        'api-key': search_key
    }

    if search_type == "vector":
        # Pure vector search
        body = {
            "search": query_text,
            "select": "id,title,content,category",
            "vectorQueries": [
                {
                    "vector": query_vector,
                    "fields": "contentVector",
                    "k": 3
                }
            ]
        }
    elif search_type == "hybrid":
        # Hybrid search (vector + keyword)
        body = {
            "search": query_text,
            "select": "id,title,content,category",
            "vectorQueries": [
                {
                    "vector": query_vector,
                    "fields": "contentVector",
                    "k": 3
                }
            ],
            "vectorFilterMode": "any" # or "all" to require both keyword and vector matches
        }
    else:
        # Semantic hybrid search
        body = {
            "search": query_text,
            "select": "id,title,content,category",
            "vectorQueries": [
                {
                    "vector": query_vector,
                    "fields": "contentVector",
                    "k": 3
                }
            ],
            "queryType": "semantic",
            "semanticConfiguration": "my-semantic-config",
            "vectorFilterMode": "any"
        }
    
    # Execute the search
    response = requests.post(
        f"{search_endpoint}/indexes/{index_name}/docs/search?api-version=2023-11-01",
        headers=headers,
        json=body
    )
    
    return response.json()

def run_test_queries():
    """Run test queries with different search types."""
    test_queries = [
        "What is vector search?",
        "How does Azure search work?",
        "Tell me about combined search approaches"
    ]
    
    search_types = ["vector", "hybrid"]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        
        for search_type in search_types:
            print(f"\n{search_type.capitalize()} Search Results:")
            results = vector_search(query, search_type)
            
            for result in results.get("value", []):
                print(f"Title: {result['title']}")
                print(f"Category: {result['category']}")
                print(f"Content: {result['content']}")
                print("---")

if __name__ == "__main__":
    run_test_queries()
```

### Understanding Search Types

1. **Pure Vector Search**:
   - Uses only vector similarity
   - Good for semantic understanding
   - May miss exact keyword matches

2. **Hybrid Search**:
   - Combines vector and keyword searches
   - Better recall than either method alone
   - Customizable with `vectorFilterMode`

3. **Semantic Hybrid Search**:
   - Adds semantic ranking on top of hybrid search
   - Generates captions and answers
   - Requires a semantic configuration

## Step 5: Setting Up Semantic Configuration

### Task: Add Semantic Configuration to the Index

To enable semantic-hybrid search, add a semantic configuration to the index:

```http
PUT https://<your-search-service-name>.search.windows.net/indexes/vector-demo-index?api-version=2023-11-01
Content-Type: application/json
api-key: <your-admin-api-key>

{
  "name": "vector-demo-index",
  "fields": [
    // ... existing fields ...
  ],
  "vectorSearch": {
    // ... existing vector configuration ...
  },
  "vectorSearchConfigurations": {
    // ... existing configurations ...
  },
  "semantic": {
    "configurations": [
      {
        "name": "my-semantic-config",
        "prioritizedFields": {
          "titleField": { "fieldName": "title" },
          "contentFields": [
            { "fieldName": "content" }
          ],
          "keywordsFields": [
            { "fieldName": "category" }
          ]
        }
      }
    ]
  }
}
```

## Lab Exercise: Building a Complete Vector Search Solution

### Exercise: Implement an End-to-End Vector Search Solution

Create a solution that:

1. Sets up an Azure OpenAI service with embedding model
2. Creates an Azure AI Search index with vector fields
3. Generates embeddings for a collection of documents
4. Implements search functionality with:
   - Pure vector search
   - Hybrid search
   - Semantic hybrid search (if your tier supports it)
5. Compares and evaluates the results of each approach

Document your implementation including:
- Index schema design
- Embedding generation approach
- Search query implementation
- Sample results from different search types
- Observations about query relevance and performance

## Next Steps

In the next module, you'll learn how to use Azure AI Foundry to build and deploy advanced AI solutions that leverage Azure AI Search.

## Additional Resources

- [Vector search in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/vector-search-overview)
- [Azure OpenAI embeddings models](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#embeddings-models)
- [Create and query a vector index](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-query)
- [Configure semantic ranking](https://learn.microsoft.com/en-us/azure/search/semantic-how-to-configure-semantic-ranking)
- [Hybrid search in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview)
