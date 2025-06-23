@description('The base name to use for the resources.')
param baseName string

@description('The location to deploy the resources.')
param location string

@description('The tags to apply to the resources.')
param tags object = {}

@description('The Azure AI Search service resource ID.')
param searchServiceId string

@description('The Azure OpenAI service resource ID.')
param openAiServiceId string

@description('The principal ID of the App Service.')
param appServicePrincipalId string

// Use the built-in Azure Cognitive Search Data Contributor role definition
var searchRoleDefinitionId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8ebe5a00-799e-43f5-93ac-243d3dce84a7')

// Use the built-in Cognitive Services User role definition for OpenAI
var openAiRoleDefinitionId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908')

// Create Key Vault for storing sensitive configuration
resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: '${baseName}-kv'
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enabledForDeployment: true
    enabledForDiskEncryption: true
    enabledForTemplateDeployment: true
    accessPolicies: []
  }
}

// Reference to the existing Search Service
resource searchService 'Microsoft.Search/searchServices@2023-11-01' existing = {
  name: last(split(searchServiceId, '/'))
}

// RBAC assignment for App Service to access Azure AI Search
resource searchRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${appServicePrincipalId}-search-role')
  scope: searchService
  properties: {
    roleDefinitionId: searchRoleDefinitionId
    principalId: appServicePrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Reference to the existing OpenAI Service
resource openAiService 'Microsoft.CognitiveServices/accounts@2023-05-01' existing = {
  name: last(split(openAiServiceId, '/'))
}

// RBAC assignment for App Service to access Azure OpenAI
resource openAiRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${appServicePrincipalId}-openai-role')
  scope: openAiService
  properties: {
    roleDefinitionId: openAiRoleDefinitionId
    principalId: appServicePrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Create Key Vault Reader Role Assignment for App Service
resource keyVaultReaderRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${appServicePrincipalId}-kv-reader-role')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '21090545-7ca7-4776-b22c-e363652d74d2') // Key Vault Reader
    principalId: appServicePrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Create Key Vault Secrets User Role Assignment for App Service
resource keyVaultSecretsUserRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${appServicePrincipalId}-kv-secrets-user-role')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: appServicePrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Create a Network Security Group for additional security
resource nsg 'Microsoft.Network/networkSecurityGroups@2023-04-01' = {
  name: '${baseName}-nsg'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowHTTPS'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 100
          direction: 'Inbound'
        }
      }
    ]
  }
}

// Create a diagnostic setting for the Key Vault
resource keyVaultDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${keyVault.name}-diagnostics'
  scope: keyVault
  properties: {
    logs: [
      {
        category: 'AuditEvent'
        enabled: true
      }
      {
        category: 'AzurePolicyEvaluationDetails'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
    workspaceId: logAnalyticsWorkspace.id
  }
}

// Create Log Analytics Workspace if needed
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${baseName}-security-logs'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

output keyVaultName string = keyVault.name
output keyVaultId string = keyVault.id
output logAnalyticsWorkspaceId string = logAnalyticsWorkspace.id
