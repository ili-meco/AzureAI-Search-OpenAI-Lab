# Module 2: Creating and Configuring Azure AI Search

## Introduction

In this module, you will learn how to provision and configure a secure Azure AI Search service. You will set up proper authentication, implement network isolation, and configure monitoring - all key elements of a production-ready search service.

## Learning Objectives

By the end of this module, you will be able to:

- Provision an Azure AI Search service with the appropriate tier
- Configure authentication using Microsoft Entra ID
- Implement network isolation using private endpoints
- Set up monitoring and logging

## Step 1: Provisioning an Azure AI Search Service

### Task: Create a Search Service

1. Sign in to the [Azure portal](https://portal.azure.com)

2. Click **Create a resource** and search for "Azure AI Search"

3. Click **Create** and configure the following settings:
   - **Subscription**: Select your Azure subscription
   - **Resource group**: Create a new resource group named `ai-search-lab-rg`
   - **Service name**: Choose a unique name like `aisearch-<your-initials>-<random-number>`
   - **Location**: Choose a region that supports Azure AI Search and Azure OpenAI (e.g., East US)
   - **Pricing tier**: Select "Standard (S1)" for this lab

4. Click **Review + create**, then **Create** after validation passes

5. Once deployment completes, click **Go to resource**

### Understanding Deployment Considerations

When deploying Azure AI Search for production workloads, consider:

- **Resource Organization**: Deploy in a workload-specific resource group
- **Region Selection**: Choose regions that support all related services (OpenAI, AI Foundry)
- **Service Naming**: Follow organization naming conventions for easier management
- **Tagging**: Apply appropriate tags for cost allocation and management

## Step 2: Configuring Authentication

Azure AI Search supports two primary authentication methods:

1. **API Keys** (simpler but less secure)
2. **Microsoft Entra ID** (recommended for production)

### Task A: Locate API Keys

1. In your search service, navigate to **Settings > Keys**
2. Note the **Primary admin key** and **Query key**
3. Understand the difference:
   - **Admin keys**: Full read/write access to the service
   - **Query keys**: Read-only access to indexes

### Task B: Configure Microsoft Entra ID Authentication

For production environments, Microsoft Entra ID is recommended:

1. In your search service, navigate to **Settings > Identity**

2. Under **System assigned**, set the status to **On** and click **Save**

3. Copy the **Object ID** that appears

4. Now create a custom role for search data operations:
   - Navigate to your subscription
   - Go to **Access control (IAM) > Add > Add custom role**
   - Name: "Search Service Data Reader"
   - Permissions: Add the following Data Actions:
     - `Microsoft.Search/searchServices/indexes/docs/read`
     - `Microsoft.Search/searchServices/indexes/read`

5. Assign the role:
   - In your search service, go to **Access control (IAM)**
   - Click **Add role assignment**
   - Select your custom role
   - Assign access to: **Managed identity**
   - Select your managed identity

## Step 3: Implementing Network Security

### Task A: Configure IP Firewall Rules

1. In your search service, navigate to **Settings > Networking**
2. Select **Selected networks**
3. Under **Firewall**, add your client IP address
4. Click **Save**

### Task B: Configure Private Endpoint (Optional)

For production environments, private endpoints are recommended:

1. In your search service, navigate to **Settings > Networking**

2. Under **Private endpoint connections**, click **+ Private endpoint**

3. Configure basic settings:
   - **Name**: `ai-search-private-endpoint`
   - **Region**: Same as your search service
   - Click **Next: Resource**

4. Configure resource:
   - **Resource type**: Microsoft.Search/searchServices
   - **Resource**: Your search service
   - **Target sub-resource**: searchService
   - Click **Next: Virtual Network**

5. Configure virtual network:
   - **Virtual network**: Create new or select existing
   - **Subnet**: Create new or select existing
   - Click **Next: DNS**

6. Configure DNS integration:
   - Keep **Integrate with private DNS zone** selected
   - Click **Review + create**, then **Create**

7. After deployment, verify the private endpoint connection in your search service

## Step 4: Setting Up Monitoring and Logging

### Task A: Configure Azure Monitor

1. In your search service, navigate to **Monitoring > Metrics**

2. Click **+ New chart** and select metrics to monitor:
   - Search Latency
   - Search Queries Per Second
   - Throttled Query Rate

3. Set appropriate time ranges and visualizations

### Task B: Enable Diagnostic Settings

1. In your search service, navigate to **Monitoring > Diagnostic settings**

2. Click **+ Add diagnostic setting**

3. Configure the following:
   - **Name**: `ai-search-diagnostics`
   - Select the logs you want to capture: 
     - OperationLogs
     - AllMetrics
   - **Destination details**: Choose Log Analytics workspace
   - Create a new Log Analytics workspace if needed

4. Click **Save**

## Step 5: Understanding Production Search Service Configuration

For production Azure AI Search deployments, consider these key security components:

1. **Network Isolation**:
   - Connected via private endpoints
   - No public internet access
   - Restricted to specific virtual networks

2. **Identity Management**:
   - Uses managed identities for authentication
   - RBAC with least privilege principle

3. **Data Protection**:
   - Customer-managed keys for encryption
   - Data residency compliance

4. **Monitoring**:
   - Centralized logging
   - Integration with security monitoring

> **Note**: For a complete production architecture, refer to the [Azure OpenAI Landing Zone Accelerator](https://github.com/Azure/azure-openai-landing-zone/tree/main/foundation) which provides reference implementations for securing both Azure AI Search and Azure OpenAI services.

## Step 6: Importing and Vectorizing Data Directly

Azure AI Search provides an easy way to import data without manually creating indexes and indexers from scratch.

### Task: Import Data Using the Azure Portal

1. In your search service, click **Import data** from the Overview page

2. **Choose a data source**:
   - Select from various options like Azure Blob Storage, Azure Table Storage, Cosmos DB, SQL Database
   - For this lab, we'll use "Samples" and select "hotels-sample" for practice
   - In a real scenario, connect to your own data source containing your documents

3. **Add cognitive skills (optional)**:
   - Enable **Text AI** to extract additional insights
   - Select appropriate enrichment skills like key phrase extraction, entity recognition, or image analysis
   - You can also enable **Vector AI** for embedding generation using Azure OpenAI

4. **Customize target index**:
   - The wizard will suggest a schema based on your data
   - Modify field attributes (searchable, filterable, sortable, facetable)
   - Set up vector search configurations if using embeddings
   - Define scoring profiles for relevance tuning

5. **Create an indexer**:
   - Configure the schedule (one-time or recurring)
   - Define field mappings and transformations
   - Set up incremental indexing options

6. **Review and create**:
   - Verify all settings are correct
   - Click **Create** to deploy the data source, skillset, index, and indexer

### Task: Configure Vector Search During Import

To enable vector search capabilities during import:

1. In the **Add cognitive skills** section of the import wizard:
   - Enable **Vector AI**
   - Select an Azure OpenAI resource or use the built-in embedding model
   - Choose which fields to vectorize (typically text content fields)
   - Set dimensions and other vector parameters

2. In the **Customize target index** section:
   - Verify the vector fields are properly configured
   - Set up the vector search algorithm (default is HNSW)
   - Configure parameters like dimensions, metric type (cosine, euclidean, etc.)

3. After import, you can query using:
   - Keyword search
   - Vector search
   - Hybrid (combined keyword and vector)

### Benefits of Using Import Data

- **Simplified Setup**: Creates all necessary components in one workflow
- **Automatic Schema Detection**: Infers field types and properties
- **Guided Configuration**: Step-by-step wizard for proper setup
- **Integrated AI Enrichment**: Easily add cognitive skills and vector capabilities

### Typical Integration Architecture

```
┌────────────────────────────────────────────────────┐      
│                                                    │      
│  ┌───────────┐     ┌───────────┐     ┌─────────┐   │      
│  │           │     │           │     │         │   │      
│  │ Web App   ├────►│ Azure AI  ├────►│ Storage │   │      
│  │           │     │ Search    │     │         │   │         
│  └───────────┘     └─────┬─────┘     └─────────┘   │      
│                          │                         │      
│  ┌───────────┐           │                         │      
│  │           │           │                         │      
│  │ Azure     ├───────────┘                         │      
│  │ OpenAI    │                                     │      
│  └───────────┘                                     │      
│                                                    │      
└────────────────────────────────────────────────────┘
```

## Lab Exercise: Creating a Secure Search Service and Importing Data

### Exercise 1: Create and Secure a Search Service

1. Follow the steps above to create an Azure AI Search service

2. Configure the following security settings:
   - System-assigned managed identity
   - IP firewall rules to restrict access
   - Diagnostic logging to a Log Analytics workspace

3. Document:
   - Your search service URL
   - Resource ID
   - Configuration choices you made
   - Additional security features you would add for a production deployment

### Exercise 2: Import and Vectorize Sample Data

1. In your search service, click **Import data** from the Overview page

2. Choose a data source:
   - Select "Samples" and then "hotels-sample"
   - Review the data structure in the preview

3. Add cognitive skills:
   - Enable the **Vector AI** option
   - Choose the default embedding model
   - Select the "Description" field for vectorization

4. Customize the target index:
   - Review the automatically generated schema
   - Ensure the "Description" field has vector search enabled
   - Modify field attributes as needed (make relevant fields searchable and filterable)

5. Configure the indexer:
   - Accept the default settings for a one-time import
   - Click **Submit** to create all components and import the data

6. After import completes:
   - Go to **Indexes** and select your new index
   - Try a simple search query using the Search explorer
   - Document the difference between this approach and manually creating components

## Next Steps

In the next module, you'll learn how to create and configure search indexes to organize your searchable content.

## Additional Resources

- [Create an Azure AI Search service](https://learn.microsoft.com/en-us/azure/search/search-create-service-portal)
- [Configure Microsoft Entra ID for Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-security-overview#aad)
- [Configure IP firewall for Azure AI Search](https://learn.microsoft.com/en-us/azure/search/service-configure-firewall)
- [Configure private endpoints for Azure AI Search](https://learn.microsoft.com/en-us/azure/search/service-create-private-endpoint)
- [Monitor Azure AI Search](https://learn.microsoft.com/en-us/azure/search/monitor-azure-cognitive-search)
- [Import data wizard in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-import-data-portal)
- [Vector search in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/vector-search-overview)
- [Tutorial: Create a vector index and query it](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-create-index)
