"""
generate_embeddings.py
-------------------------
This script generates embeddings for documents using Azure OpenAI.
The embeddings can then be used for vector search in Azure AI Search.

"""

import os
import json
import time
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI configuration
azure_openai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
azure_openai_key = os.environ["AZURE_OPENAI_KEY"]
azure_openai_embedding_deployment = os.environ["AZURE_OPENAI_EMBEDDING_NAME"]
azure_openai_api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=azure_openai_key,
    api_version=azure_openai_api_version,
    azure_endpoint=azure_openai_endpoint
)

def get_embeddings(text, model=azure_openai_embedding_deployment):
    """
    Get embeddings for a text string using Azure OpenAI.
    
    Args:
        text (str): The text to generate embeddings for
        model (str): The name of the embedding model deployment
        
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
        response = client.embeddings.create(
            input=text,
            model=model
        )
        
        # Extract the embedding vector
        embedding = response.data[0].embedding
        return embedding
    
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        # Return a zero vector in case of error
        return [0.0] * 1536

def process_documents(documents_file):
    """
    Process documents and add embeddings.
    
    Args:
        documents_file (str): Path to the JSON file containing documents
        
    Returns:
        list: Documents with embeddings added
    """
    # Load documents from file
    with open(documents_file, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    print(f"Processing {len(documents)} documents...")
    
    # Process each document
    for i, doc in enumerate(documents):
        if i > 0 and i % 10 == 0:
            print(f"Processed {i} documents...")
            # Add a small delay to avoid hitting rate limits
            time.sleep(0.5)
        
        # Generate embeddings for title and content
        title_embedding = get_embeddings(doc.get("title", ""))
        content_embedding = get_embeddings(doc.get("content", ""))
        
        # Add embeddings to the document
        doc["titleVector"] = title_embedding
        doc["contentVector"] = content_embedding
    
    print(f"Completed processing {len(documents)} documents with embeddings.")
    
    # Save documents with embeddings
    output_file = documents_file.replace('.json', '_with_embeddings.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    
    print(f"Documents with embeddings saved to {output_file}")
    
    return documents

if __name__ == "__main__":
    # Path to your documents file
    documents_file = "documents.json"
    
    # Check if file exists
    if not os.path.exists(documents_file):
        print(f"Error: File '{documents_file}' not found.")
        print("Please create a JSON file with your documents first.")
        exit(1)
    
    # Process documents and add embeddings
    documents_with_embeddings = process_documents(documents_file)
