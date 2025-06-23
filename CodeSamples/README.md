# Vector Search Implementation Sample Code

This directory contains sample code to demonstrate vector search implementation using Azure AI Search and Azure OpenAI.

## Files:
1. `create_search_index.py` - Create a search index with vector fields
2. `generate_embeddings.py` - Generate embeddings for documents using Azure OpenAI
3. `upload_documents.py` - Upload documents with embeddings to the search index
4. `vector_search_client.py` - Client library for performing vector search queries
5. `sample_web_app.py` - A simple Flask web application for demonstrating search UI

## Getting Started:
1. Set up your environment variables in `.env`
2. Install the required packages using `pip install -r requirements.txt`
3. Run the scripts in sequence to set up your search index and upload documents
4. Try out vector search using the sample client or web app

For detailed instructions, see Module 5 in the main tutorial.

## Requirements
```
azure-search-documents>=11.4.0
azure-identity>=1.13.0
azure-ai-openai>=1.0.0
flask>=2.3.0
python-dotenv>=1.0.0
pandas>=2.0.0
numpy>=1.24.0
```
