"""
create_search_index.py
-------------------------
This script creates an Azure AI Search index with vector capabilities
for use with embeddings from Azure OpenAI.

"""

import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SearchField,
    SemanticSearch,
    SemanticConfiguration,
    SemanticField,
    VectorSearchSimilarityAlgorithm
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure AI Search configuration
search_service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
search_service_key = os.environ["AZURE_SEARCH_ADMIN_KEY"]
search_index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]

def create_search_index():
    """
    Create a search index with vector search capabilities
    """
    # Create a SearchIndexClient
    search_credential = AzureKeyCredential(search_service_key)
    index_client = SearchIndexClient(
        endpoint=search_service_endpoint,
        credential=search_credential
    )
    
    # Define vector search configuration
    vector_search = VectorSearch(
        algorithms=[
            VectorSearchAlgorithmConfiguration(
                name="hnsw-vector-config",
                kind=VectorSearchSimilarityAlgorithm.HNSW,
                hnsw_parameters=HnswAlgorithmConfiguration(
                    m=4,
                    ef_construction=400,
                    ef_search=500,
                    metric="cosine"
                )
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-vector-config",
                vectorizer="none"
            )
        ]
    )
    
    # Define semantic search configuration
    semantic_search = SemanticSearch(
        configurations=[
            SemanticConfiguration(
                name="semantic-config",
                prioritized_fields={
                    "content_fields": [
                        SemanticField(field_name="content")
                    ],
                    "title_fields": [
                        SemanticField(field_name="title")
                    ]
                }
            )
        ]
    )

    # Define the index fields
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="title", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="sourceUrl", type=SearchFieldDataType.String),
        SimpleField(name="sourceName", type=SearchFieldDataType.String, filterable=True, facetable=True),
        # Vector field for the title embedding
        SearchField(
            name="titleVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=1536,
            vector_search_profile_name="vector-profile"
        ),
        # Vector field for the content embedding
        SearchField(
            name="contentVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=1536,
            vector_search_profile_name="vector-profile"
        )
    ]

    # Create the index
    index = SearchIndex(
        name=search_index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search
    )
    
    try:
        index_client.create_or_update_index(index)
        print(f"Index '{search_index_name}' created successfully.")
    except Exception as e:
        print(f"Error creating index: {str(e)}")

if __name__ == "__main__":
    create_search_index()
