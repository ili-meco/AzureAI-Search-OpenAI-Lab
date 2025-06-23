@description('The base name to use for the resources.')
param baseName string

@description('The location to deploy the resources.')
param location string = resourceGroup().location

@description('The tags to apply to the resources.')
param tags object = {}

@description('The SKU for the Azure OpenAI service.')
param sku string = 'S0'

@description('The name of the embedding model deployment.')
param embeddingModelDeploymentName string = 'text-embedding-ada-002'

@description('The subnet ID for the private endpoint.')
param subnetId string

@description('Whether to create a private endpoint for the Azure OpenAI service.')
param createPrivateEndpoint bool = true

// Variables
var openAiName = 'oai-${baseName}'
var privateDnsZoneName = 'privatelink.openai.azure.com'
var privateEndpointName = 'pe-${openAiName}'

// Azure OpenAI Service
resource openAiService 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openAiName
  location: location
  tags: tags
  kind: 'OpenAI'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: openAiName
    publicNetworkAccess: createPrivateEndpoint ? 'Disabled' : 'Enabled'
    networkAcls: {
      defaultAction: 'Deny'
      virtualNetworkRules: []
      ipRules: []
    }
  }
  sku: {
    name: sku
  }
}

// Embedding Model Deployment
resource embeddingModelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAiService
  name: embeddingModelDeploymentName
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-ada-002'
      version: '2'
    }
    raiPolicyName: 'Microsoft.Default'
    scaleSettings: {
      scaleType: 'Standard'
    }
  }
  sku: {
    name: 'Standard'
    capacity: 120
  }
}

// Private DNS Zone
resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = if (createPrivateEndpoint) {
  name: privateDnsZoneName
  location: 'global'
  tags: tags
}

// Private DNS Zone VNet Link
resource privateDnsZoneVnetLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = if (createPrivateEndpoint) {
  parent: privateDnsZone
  name: '${baseName}-link'
  location: 'global'
  tags: tags
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: split(subnetId, '/subnets/')[0]
    }
  }
}

// Private Endpoint
resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = if (createPrivateEndpoint) {
  name: privateEndpointName
  location: location
  tags: tags
  properties: {
    privateLinkServiceConnections: [
      {
        name: privateEndpointName
        properties: {
          privateLinkServiceId: openAiService.id
          groupIds: [
            'account'
          ]
        }
      }
    ]
    subnet: {
      id: subnetId
    }
  }
}

// Private DNS Zone Group
resource privateEndpointDnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-05-01' = if (createPrivateEndpoint) {
  parent: privateEndpoint
  name: 'openAiDnsGroup'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'config'
        properties: {
          privateDnsZoneId: privateDnsZone.id
        }
      }
    ]
  }
}

// Diagnostic Settings
resource openAiDiagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'openai-diagnostics'
  scope: openAiService
  properties: {
    workspaceId: logAnalyticsWorkspace.id
    logs: [
      {
        category: 'Audit'
        enabled: true
      }
      {
        category: 'RequestResponse'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

// Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'log-${baseName}-oai'
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

// Outputs
output openAiServiceId string = openAiService.id
output openAiEndpoint string = openAiService.properties.publicNetworkAccess == 'Enabled' 
  ? 'https://${openAiName}.openai.azure.com/' 
  : 'https://${openAiName}.privatelink.openai.azure.com/'
output openAiName string = openAiService.name
output embeddingModelDeploymentName string = embeddingModelDeployment.name
