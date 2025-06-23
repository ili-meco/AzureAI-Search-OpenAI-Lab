"""
upload_documents.py
-------------------------
This script uploads documents with embeddings to an Azure AI Search index.

"""

import os
import json
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import IndexDocumentsBatch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure AI Search configuration
search_service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
search_service_key = os.environ["AZURE_SEARCH_ADMIN_KEY"]
search_index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]

def upload_documents(documents_file):
    """
    Upload documents to an Azure AI Search index.
    
    Args:
        documents_file (str): Path to the JSON file containing documents with embeddings
    """
    # Load documents from file
    with open(documents_file, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    print(f"Uploading {len(documents)} documents to index '{search_index_name}'...")
    
    # Create a SearchClient
    search_credential = AzureKeyCredential(search_service_key)
    search_client = SearchClient(
        endpoint=search_service_endpoint,
        index_name=search_index_name,
        credential=search_credential
    )
    
    # Upload documents in batches
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch_end = min(i + batch_size, len(documents))
        batch = documents[i:batch_end]
        
        try:
            # Create an upload batch
            upload_batch = IndexDocumentsBatch()
            upload_batch.actions = [
                {"action": "upload", "document": doc} for doc in batch
            ]
            
            # Upload the batch
            result = search_client.index_documents(batch=upload_batch)
            
            # Check for errors
            if not result.results:
                print(f"No results returned for batch {i//batch_size + 1}")
                continue
                
            succeeded = sum(1 for r in result.results if r.succeeded)
            print(f"Batch {i//batch_size + 1}: {succeeded}/{len(batch)} documents indexed successfully")
            
            # Log any errors
            for doc_result in result.results:
                if not doc_result.succeeded:
                    print(f"Error indexing document ID: {doc_result.key}, Error: {doc_result.error_message}")
        
        except Exception as e:
            print(f"Error uploading batch {i//batch_size + 1}: {str(e)}")
    
    print(f"Document upload completed for index '{search_index_name}'")

if __name__ == "__main__":
    # Path to your documents file with embeddings
    documents_file = "documents_with_embeddings.json"
    
    # Check if file exists
    if not os.path.exists(documents_file):
        print(f"Error: File '{documents_file}' not found.")
        print("Please run generate_embeddings.py first to create this file.")
        exit(1)
    
    # Upload documents to search index
    upload_documents(documents_file)
