# Module 1: Azure AI Search Fundamentals

## Introduction

Azure AI Search (formerly Azure Cognitive Search) is a cloud search service that provides developers with APIs and tools for building rich search experiences over private, heterogeneous content in web, mobile, and enterprise applications. It includes capabilities like full-text search, semantic search, vector search, and hybrid search.

This module will cover the fundamental concepts of Azure AI Search and prepare you for implementing a production-ready search solution.

## Learning Objectives

By the end of this module, you will be able to:

- Understand the core components of Azure AI Search
- Explain the difference between various search types
- Recognize when to use different search tiers
- Design a secure search architecture
- Apply content safety principles to search implementations

## Azure AI Search Architecture

Azure AI Search consists of several key components that work together:

![Azure AI Search Architecture](../images/search-architecture.png)

### Core Components

1. **Search Service**: The primary Azure resource that hosts your indexes, indexers, and other components.

2. **Indexes**: The primary data structure in Azure AI Search, similar to a database table. An index contains documents that are searchable by your applications.

3. **Indexers**: Optional components that can crawl a supported Azure data source for searchable content, extract data and metadata, and load it into an index.

4. **Data Sources**: External data repositories that provide content for indexers, such as Azure Blob Storage, Azure SQL, Azure Cosmos DB, etc.

5. **Skillsets**: Collections of enrichment steps that can be applied during indexing to extract or generate additional information from your data.

6. **Analyzers**: Components that process text during indexing and at query time, handling tasks like tokenization, stopword removal, and stemming.

## Search Types

Azure AI Search supports multiple search types:

### 1. Full-Text Search (Keyword Search)

Traditional search that finds documents containing specified terms. Supports:
- Term boosting
- Fuzzy search
- Proximity search
- Regular expressions
- Wildcard search

### 2. Semantic Search

Uses natural language understanding to improve search relevance:
- Understands intent and contextual meaning
- Re-ranks results based on semantic similarity
- Generates captions to highlight relevant passages
- Returns semantic answers when the index is configured properly

### 3. Vector Search

Uses numerical vector embeddings to find similar content:
- Based on neural network models that convert content to vector embeddings
- Measures similarity between vectors (often using cosine similarity)
- Excellent for "similar to this" scenarios and conceptual matching

### 4. Hybrid Search

Combines multiple search approaches:
- Combines results from keyword search and vector search
- Can provide more relevant results than either approach alone
- Configurable weights to balance between approaches

## Service Tiers

Azure AI Search offers different service tiers to meet various requirements:

| Tier | Purpose | Features |
|------|---------|----------|
| **Free** | Development and small-scale testing | Limited storage (50 MB), 3 indexes, no SLA |
| **Basic** | Small production workloads | Scales up to 2 GB per partition, up to 3 partitions |
| **Standard (S1, S2, S3)** | Production workloads | Higher capacity and performance |
| **Storage Optimized (L1, L2)** | Large index storage | Cost-effective for read-heavy workloads with large indexes |

Each tier varies in:
- Query throughput
- Index size limits
- Partition and replica count options
- High availability capabilities

## Security Considerations

### Authentication Methods

1. **API Keys**: Two types are available:
   - Admin keys (full control)
   - Query keys (read-only access to indexes)

2. **Microsoft Entra ID**: Recommended for production environments, supporting:
   - User identities
   - Service principals
   - Managed identities

### Network Security

1. **IP Firewall Rules**: Restrict access to specific IP ranges

2. **Private Endpoints**: Place your search service behind a virtual network for enhanced security

3. **Service Endpoints**: Secure traffic between your VNet and the search service

### Role-Based Access Control (RBAC)

Azure AI Search supports three built-in roles:
- **Search Service Contributor**: Create and manage search services but can't grant access
- **Search Index Data Reader**: Read data from indexes
- **Search Index Data Contributor**: Read, write, and delete data in indexes

## Monitoring and Logging

Monitoring options for Azure AI Search include:

1. **Azure Monitor**: Track metrics like query latency, queries per second, and throttled queries

2. **Search Traffic Analytics**: Analyze search patterns and user behavior

3. **Diagnostic Logs**: Capture operations and errors for troubleshooting

## Content Safety and Filtering

When implementing Azure AI Search with AI-generated content, content safety becomes a critical consideration:

### Content Filtering

1. **Default Filters**: Azure AI services include built-in content filtering capabilities that help detect and filter harmful content
   
2. **Custom Safety Filters**: Organizations can create custom safety filters to:
   - Define organization-specific policies
   - Control AI-generated content based on specific requirements
   - Implement custom moderation workflows

### Creating Custom Safety Filters

Custom safety filters in Azure AI Foundry allow you to:

1. **Define Categories**: Control specific categories of potentially harmful content:
   - Hate speech
   - Sexual content
   - Violence
   - Self-harm

2. **Set Thresholds**: Customize severity levels for each category (low, medium, high)

3. **Apply Filters**: Implement filters at various points:
   - During prompt processing
   - On generated responses
   - Within RAG-based search implementations

4. **Monitor and Refine**: Track filter effectiveness and adjust as needed

Custom safety filters are especially important when combining search results with generative AI responses, ensuring that all retrieved and generated content meets organizational standards.

## Lab Exercise: Exploring Azure AI Search Concepts

### Exercise 1: Exploring Azure AI Search Documentation

1. Visit the [Azure AI Search documentation](https://learn.microsoft.com/en-us/azure/search/)
2. Review the "What is Azure AI Search?" article
3. Explore the "How-to guides" section, focusing on:
   - Creating an index
   - Creating an indexer
   - Security configuration
4. Visit the [Content Filtering in Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/content-filtering) documentation to understand how content safety applies to AI-enhanced search

## Next Steps

In the next module, you'll learn how to provision and configure an Azure AI Search service with proper network isolation and security settings.

## Additional Resources

- [Azure AI Search Documentation](https://learn.microsoft.com/en-us/azure/search/)
- [Choose a pricing tier for Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-sku-tier)
- [Security in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-security-overview)
- [Monitoring Azure AI Search](https://learn.microsoft.com/en-us/azure/search/monitor-azure-cognitive-search)
- [Content Filtering in Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/content-filtering)
- [Creating Custom Safety Filters](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/content-filtering#create-and-use-a-custom-content-filter)
