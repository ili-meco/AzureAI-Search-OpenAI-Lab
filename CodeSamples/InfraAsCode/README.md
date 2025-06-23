# Infrastructure as Code Templates for Azure AI Search Landing Zone

This directory contains Bicep templates for deploying an Azure AI Search landing zone pattern, including necessary network security components and Azure OpenAI integration.

## Files Overview

1. `main.bicep` - Main deployment template for Azure AI Search landing zone
2. `modules/networking.bicep` - Network resources for the landing zone
3. `modules/search.bicep` - Azure AI Search resource and configuration
4. `modules/openai.bicep` - Azure OpenAI resources and configuration
5. `modules/appservice.bicep` - App Service for hosting web applications
6. `modules/security.bicep` - Security configurations for Azure AI Search
7. `parameters.json` - Parameters for the main deployment template

## Deployment Instructions

1. Update the `parameters.json` file with your specific values
2. Run the following Azure CLI command:

```bash
az login
az account set --subscription <your-subscription-id>
az deployment sub create --location <location> --template-file main.bicep --parameters @parameters.json
```

## Security Considerations

These templates implement the following security features:
- Private endpoints for Azure AI Search
- Network isolation using NSGs
- RBAC configurations for Azure AI Search
- Managed identities for secure authentication

## Requirements

- Azure CLI version 2.40.0 or later
- Active Azure subscription with appropriate permissions
- Network connectivity to Azure
