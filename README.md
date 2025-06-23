# Azure AI Search with OpenAI & AI Foundry Lab Guide

This comprehensive lab guide will walk you through setting up and using Azure AI Search with Azure OpenAI, building a secure landing zone, and implementing a production-ready AI solution.

## Lab Objectives

By completing this lab, you will:

1. Understand Azure AI Search fundamentals and key concepts
2. Create and configure an Azure AI Search service
3. Build and manage search indexes and indexers
4. Implement vector search with embeddings
5. Use Azure AI Foundry to enhance search capabilities
6. Deploy a chat application using Azure OpenAI with search grounding
7. Set up a production-ready solution using the landing zone pattern

## Prerequisites

- Azure subscription with appropriate permissions
- Basic understanding of AI/ML concepts
- Familiarity with Azure portal
- Basic knowledge of REST APIs and JSON
- Code editor (VS Code recommended)

## Lab Modules

1. **Module 1: Azure AI Search Fundamentals**
   - Understanding Azure AI Search architecture
   - Key concepts: indexes, indexers, and analyzers
   - Search service tiers and scaling considerations
   - Security and RBAC for Azure AI Search

2. **Module 2: Creating and Configuring Azure AI Search**
   - Provisioning an Azure AI Search service
   - Setting up proper authentication
   - Configuring network isolation and private endpoints
   - Monitoring and logging setup

3. **Module 3: Building Search Indexes**
   - Index schema design best practices
   - Creating indexes via Azure Portal
   - Creating indexes programmatically with REST API
   - Adding scoring profiles and customizing relevance

4. **Module 4: Configuring Indexers**
   - Understanding indexer components and capabilities
   - Setting up data sources (Blob Storage, Cosmos DB)
   - Configuring incremental indexing
   - Managing indexer schedules and monitoring

5. **Module 5: Vector Search Implementation**
   - Understanding vector search concepts
   - Creating embeddings with Azure OpenAI
   - Implementing vector search fields
   - Hybrid search approaches (vector + keyword)

6. **Module 6: Azure AI Foundry Integration**
   - Creating an AI Foundry project
   - Building search-enhanced prompt flows
   - Deploying flows to production endpoints
   - Testing and evaluating search quality

7. **Module 7: Building a Search-Grounded Chat Application**
   - Setting up Azure OpenAI resources
   - Integrating OpenAI with Azure AI Search
   - Implementing Retrieval Augmented Generation (RAG)
   - Managing chat context and history

8. **Module 8: Landing Zone Implementation**
   - Understanding the landing zone pattern
   - Implementing network isolation and security
   - Setting up proper RBAC and access control
   - Monitoring and observability configuration

## Getting Started

Follow the instructions in each module sequentially. Each module builds on the knowledge and resources from previous modules.

## Repository Structure

- **Modules/** - Detailed markdown guides for each module
- **CodeSamples/** - Python code examples for working with Azure AI Search
  - **SampleData/** - JSON files for demos and exercises
  - **InfraAsCode/** - Bicep templates for deploying the landing zone
    - **modules/** - Modular Bicep files for different Azure resources
  - **PromptFlows/** - Example Azure AI Foundry prompt flow implementations

## Sample Files Included

- **Schema Definitions** - Example schema.json for index creation
- **Sample Documents** - Test documents for indexing exercises
- **Skillset Configuration** - Example skillset definition for enrichment
- **Prompt Flows** - Complete RAG implementation with Azure AI Search
- **Infrastructure as Code** - Full landing zone implementation with:
  - Networking (VNet, Subnets, NSGs)
  - Azure AI Search (with private endpoints)
  - Azure OpenAI (with managed identity)
  - App Service (for hosting web applications)
  - Security (Key Vault, RBAC assignments)

Happy learning!
