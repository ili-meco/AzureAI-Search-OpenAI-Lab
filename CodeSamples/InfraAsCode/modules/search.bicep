@description('The base name to use for the resources.')
param baseName string

@description('The location to deploy the resources.')
param location string = resourceGroup().location

@description('The tags to apply to the resources.')
param tags object = {}

@description('The SKU for the Azure AI Search service.')
@allowed([
  'free'
  'basic'
  'standard'
  'standard2'
  'standard3'
  'storage_optimized_l1'
  'storage_optimized_l2'
])
param sku string = 'standard'

@description('The subnet ID for the private endpoint.')
param subnetId string

@description('Whether to create a private endpoint for the Azure AI Search service.')
param createPrivateEndpoint bool = true

// Variables
var searchName = 'srch-${baseName}'
var privateDnsZoneName = 'privatelink.search.windows.net'
var privateEndpointName = 'pe-${searchName}'

// Azure AI Search Service
resource searchService 'Microsoft.Search/searchServices@2022-09-01' = {
  name: searchName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    hostingMode: contains(sku, 'storage_optimized') ? 'default' : 'default'
    partitionCount: 1
    replicaCount: 1
    publicNetworkAccess: createPrivateEndpoint ? 'disabled' : 'enabled'
    disableLocalAuth: true
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
  }
  sku: {
    name: sku
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
          privateLinkServiceId: searchService.id
          groupIds: [
            'searchService'
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
  name: 'searchServiceDnsGroup'
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
resource searchDiagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'search-diagnostics'
  scope: searchService
  properties: {
    workspaceId: logAnalyticsWorkspace.id
    logs: [
      {
        category: 'OperationLogs'
        enabled: true
      }
      {
        category: 'SearchServiceLogs'
        enabled: true
      }
      {
        category: 'SearchServiceHttpLogs'
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
  name: 'log-${baseName}'
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
output searchServiceId string = searchService.id
output searchServiceEndpoint string = searchService.properties.publicNetworkAccess == 'enabled' 
  ? 'https://${searchService.name}.search.windows.net' 
  : 'https://${searchService.name}.privatelink.search.windows.net'
output searchServiceName string = searchService.name
