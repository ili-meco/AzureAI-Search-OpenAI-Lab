# Sample Data for Azure AI Search Lab

This directory contains sample files to help you complete the hands-on exercises in the Azure AI Search lab.

## Files Included

### `documents.json`

This file contains 10 sample documents about Azure AI Search and related concepts. You'll use these documents to:

- Create and populate a search index
- Generate vector embeddings
- Test search functionality
- Implement RAG patterns

Each document includes:
- Document ID
- Title
- Content
- Category
- Last updated timestamp 
- Empty vector embedding array (to be filled during the lab exercises)

### `schema.json`

This file provides a complete index schema definition that showcases:

- Field definitions with different data types
- Vector search configuration
- Semantic configuration
- Scoring profile definition
- Custom analyzers
- Suggester configuration
- CORS settings

### `skillset.json`

An example AI enrichment skillset that can be used with an indexer to:

- Extract entities (people, organizations, locations)
- Identify key phrases
- Split text into smaller chunks
- Analyze sentiment
- Generate vector embeddings (using Azure OpenAI)

## How to Use These Files

The lab modules will walk you through using these files in various exercises. Typically, you'll:

1. Upload documents to Azure Blob Storage or another data source
2. Create an index using the schema definition
3. Set up an indexer with the skillset to process the documents
4. Query the index using various search techniques
5. Integrate search with Azure OpenAI for RAG patterns

## Notes

- The vector embedding fields are intentionally empty and will be populated during exercises
- You'll need to replace placeholders (like `{your-openai-api-key}`) with your actual values
- These files are designed to work with the lab instructions in the Modules directory
