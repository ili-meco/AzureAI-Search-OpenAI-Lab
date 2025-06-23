# Module 4: Configuring Indexers

## Introduction

Indexers in Azure AI Search automatically crawl data sources, extract searchable content, and populate search indexes. They simplify the process of ingesting data, making it faster to set up and maintain search solutions, especially when dealing with large volumes of data or regularly updated content.

In this module, you will learn how to configure and manage indexers for different data sources.

## Learning Objectives

By the end of this module, you will be able to:

- Create and configure data sources for indexers
- Set up and customize indexers for different content types
- Implement AI enrichment using skillsets
- Monitor and troubleshoot indexer operations

## Indexer Components Overview

An indexer setup consists of three main components:

1. **Data Source**: Defines the connection to your data
2. **Skillset** (optional): Defines AI enrichment steps
3. **Indexer**: Defines how data is extracted and loaded into an index

### Supported Data Sources

Azure AI Search indexers support multiple Azure data sources:

- Azure Blob Storage
- Azure Data Lake Storage Gen2
- Azure Cosmos DB
- Azure SQL Database
- Azure Table Storage
- Azure MySQL
- Azure PostgreSQL

## Step 1: Creating a Data Source Connection

### Task: Create an Azure Blob Storage Data Source

First, let's create a storage account and upload sample documents:

1. Navigate to the Azure portal and create a new storage account:
   - **Name**: Choose a unique name like `storageaisearch<random>`
   - **Performance**: Standard
   - **Redundancy**: Locally-redundant storage (LRS)
   - Other settings can remain as default

2. Create a blob container:
   - Container name: `documents`
   - Public access level: Private

3. Upload sample documents:
   - Download sample documents from [this link](https://github.com/Azure-Samples/azure-search-sample-data/tree/main/clinical-trials-pdf-19)
   - Upload the PDF files to the `documents` container

4. Now create a data source connection in your search service:
   
   a. In the Azure portal, navigate to your search service
   
   b. Select **Data sources** from the left menu, then click **+ New data source**
   
   c. Configure the data source:
      - **Name**: `docs-datasource`
      - **Source**: Azure Blob Storage
      - **Connection string**: Select your storage account and provide the access key
      - **Container name**: `documents`
      - **Blob folder**: Leave blank (root of container)
      - **Description**: `Medical documents for search`
   
   d. Click **Create** to save the data source

### Using Microsoft Entra ID Authentication for Data Sources (Production Recommended)

For production environments, we recommend using Microsoft Entra ID authentication instead of connection strings with keys:

1. Ensure your search service has a system-assigned managed identity

2. Grant the managed identity appropriate permissions on your storage account:
   - Navigate to your storage account
   - Go to **Access control (IAM)**
   - Add role assignment:
     - Role: Storage Blob Data Reader
     - Assign access to: Managed identity
     - Select your search service's managed identity

3. Create the data source using Microsoft Entra ID authentication:

```http
POST https://<your-search-service-name>.search.windows.net/datasources?api-version=2023-11-01
Content-Type: application/json
api-key: <your-admin-api-key>

{
  "name": "docs-datasource-msi",
  "type": "azureblob",
  "credentials": { 
    "connectionString": null,
    "identity": "managed" 
  },
  "container": { "name": "documents" }
}
```

## Step 2: Creating a Basic Indexer

### Task: Create an Indexer Without AI Enrichment

1. In the Azure portal, navigate to your search service

2. Select **Indexers** from the left menu, then click **+ New indexer**

3. Configure the indexer settings:
   - **Name**: `docs-indexer`
   - **Data source**: Select the `docs-datasource` you created
   - **Target index**: Click **New index** to create a new index
     - **Index name**: `docs-index`
     - **Key field name**: `metadata_storage_path` (encoded base-64)
   
4. Configure field mappings:
   - Click **Customize target fields**
   - Azure AI Search will automatically detect content and metadata fields
   - Ensure the following fields are included:

     | Source Field | Target Field | Type | Attributes |
     |-------------|------------|------|------------|
     | `metadata_storage_path` | `id` | `Edm.String` | Key, Retrievable |
     | `metadata_storage_name` | `filename` | `Edm.String` | Retrievable, Searchable |
     | `metadata_content_type` | `contentType` | `Edm.String` | Retrievable, Filterable, Facetable |
     | `metadata_language` | `language` | `Edm.String` | Retrievable, Filterable |
     | `content` | `content` | `Edm.String` | Retrievable, Searchable |

5. Configure indexer settings:
   - **Schedule**: Choose Run on demand
   - **Base-64 Encode Keys**: Yes
   - **Batch Size**: 1000
   - **Max Failed Items**: 0
   - **Max Failed Items Per Batch**: 0

6. Click **Create** to create the indexer and index

7. Wait for the indexer to run and monitor its status

## Step 3: Creating an AI-Enriched Indexer with Skillsets

AI enrichment allows you to extract more value from your content using AI capabilities.

### Task: Create an Indexer with a Skillset

1. In the Azure portal, navigate to your search service

2. Select **Skillsets** from the left menu, then click **+ New skillset**

3. Configure the skillset:
   - **Name**: `docs-skillset`
   - **Cognitive Services resource**: Create or select an existing Cognitive Services resource
   - **Enrichment options**: Check the enrichments you want to apply:
     - Extract text content
     - Extract named entities (people, organizations, locations)
     - Extract key phrases
     - Detect language
     - Generate captions

4. Click **Next: Attach to indexer**

5. Create a new indexer or update an existing one:
   - **Name**: `docs-enriched-indexer`
   - **Data source**: Select your existing data source
   - **Target index**: Create a new index called `docs-enriched-index`
   - Configure field mappings to include the enriched fields:

     | Source Field | Target Field | Type | Attributes |
     |-------------|------------|------|------------|
     | `metadata_storage_path` | `id` | `Edm.String` | Key, Retrievable |
     | `metadata_storage_name` | `filename` | `Edm.String` | Retrievable, Searchable |
     | `content` | `content` | `Edm.String` | Retrievable, Searchable |
     | `organizations` | `organizations` | `Collection(Edm.String)` | Retrievable, Filterable, Facetable |
     | `locations` | `locations` | `Collection(Edm.String)` | Retrievable, Filterable, Facetable |
     | `keyphrases` | `keyphrases` | `Collection(Edm.String)` | Retrievable, Filterable, Facetable |
     | `language` | `language` | `Edm.String` | Retrievable, Filterable |

6. Configure indexer settings as before, then click **Submit**

### Using REST API for Advanced Skillset Configuration

For more complex skillsets, use the REST API:

```http
PUT https://<your-search-service-name>.search.windows.net/skillsets/docs-skillset?api-version=2023-11-01
Content-Type: application/json
api-key: <your-admin-api-key>

{
  "name": "docs-skillset",
  "description": "Extract entities, keyphrases, and language",
  "skills": [
    {
      "@odata.type": "#Microsoft.Skills.Text.EntityRecognitionSkill",
      "categories": ["Person", "Organization", "Location"],
      "defaultLanguageCode": "en",
      "inputs": [
        {
          "name": "text",
          "source": "/document/content"
        }
      ],
      "outputs": [
        {
          "name": "persons",
          "targetName": "persons"
        },
        {
          "name": "organizations",
          "targetName": "organizations"
        },
        {
          "name": "locations",
          "targetName": "locations"
        }
      ]
    },
    {
      "@odata.type": "#Microsoft.Skills.Text.KeyPhraseExtractionSkill",
      "defaultLanguageCode": "en",
      "inputs": [
        {
          "name": "text",
          "source": "/document/content"
        }
      ],
      "outputs": [
        {
          "name": "keyPhrases",
          "targetName": "keyphrases"
        }
      ]
    },
    {
      "@odata.type": "#Microsoft.Skills.Text.LanguageDetectionSkill",
      "inputs": [
        {
          "name": "text",
          "source": "/document/content"
        }
      ],
      "outputs": [
        {
          "name": "languageCode",
          "targetName": "language"
        }
      ]
    }
  ],
  "cognitiveServices": {
    "@odata.type": "#Microsoft.Azure.Search.CognitiveServicesByKey",
    "description": "Cognitive Services",
    "key": "<your-cognitive-services-key>"
  }
}
```

## Step 4: Configuring Incremental Indexing

Incremental indexing ensures only new or changed documents are processed, making indexing more efficient.

### Task: Configure Change Detection Policy

1. Create or update a data source with change detection:

```http
PUT https://<your-search-service-name>.search.windows.net/datasources/docs-datasource?api-version=2023-11-01
Content-Type: application/json
api-key: <your-admin-api-key>

{
  "name": "docs-datasource",
  "type": "azureblob",
  "credentials": {
    "connectionString": "DefaultEndpointsProtocol=https;AccountName=<account-name>;AccountKey=<account-key>;EndpointSuffix=core.windows.net"
  },
  "container": {
    "name": "documents"
  },
  "dataChangeDetectionPolicy": {
    "@odata.type": "#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy",
    "highWaterMarkColumnName": "metadata_storage_last_modified"
  }
}
```

2. For Azure SQL data sources, you can use SQL integrated change tracking:

```json
"dataChangeDetectionPolicy": {
  "@odata.type": "#Microsoft.Azure.Search.SqlIntegratedChangeTrackingPolicy"
}
```

## Step 5: Scheduling Indexer Runs

Indexers can run on demand or on a schedule:

### Task: Configure Indexer Schedule

Create or update an indexer with a schedule:

```http
PUT https://<your-search-service-name>.search.windows.net/indexers/docs-indexer?api-version=2023-11-01
Content-Type: application/json
api-key: <your-admin-api-key>

{
  "name": "docs-indexer",
  "dataSourceName": "docs-datasource",
  "targetIndexName": "docs-index",
  "schedule": {
    "interval": "PT1H",
    "startTime": "2023-09-01T00:00:00Z"
  }
}
```

This schedule runs the indexer every hour starting from the specified time.

## Step 6: Monitoring and Troubleshooting Indexers

### Task: Monitor Indexer Status

1. In the Azure portal, navigate to your indexer

2. View the indexer status and history:
   - Success/failure status
   - Document counts (succeeded, failed)
   - Error messages for failed documents
   - Execution duration

3. For more detailed logs, use the indexer status API:

```http
GET https://<your-search-service-name>.search.windows.net/indexers/docs-indexer/status?api-version=2023-11-01
api-key: <your-admin-api-key>
```

### Common Indexer Issues and Solutions

| Issue | Possible Solution |
|-------|------------------|
| Document failures | Check document size limits (< 32MB for indexing) |
| Index field mapping issues | Verify field names and types match between source and index |
| Skillset errors | Review cognitive services availability and quotas |
| Rate limiting | Spread indexing operations over time with smaller batch sizes |
| Permissions issues | Verify data source credentials and permissions |

## Lab Exercise: Creating an End-to-End Indexer Solution

### Exercise 1: Multi-Source Indexing

Create a solution that:

1. Creates an Azure Blob Storage container with sample data
2. Creates an Azure SQL Database with structured data
3. Configures indexers for both sources with appropriate field mappings
4. Implements a change detection policy for each source
5. Sets up a schedule for regular indexing

Document your implementation, including:
- Data source configurations
- Index schema
- Field mappings
- Indexer settings
- Monitoring approach

## Next Steps

In the next module, you'll learn how to implement vector search capabilities for semantic similarity and natural language understanding.

## Additional Resources

- [Create an indexer for Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-howto-create-indexers)
- [Indexing Azure Blob Storage with Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-howto-indexing-azure-blob-storage)
- [AI enrichment with cognitive skills in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/cognitive-search-concept-intro)
- [Configure incremental indexing in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-howto-incremental-index)
- [Monitor indexer status and results in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-howto-monitor-indexers)
