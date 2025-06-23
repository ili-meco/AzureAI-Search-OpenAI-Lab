@description('The base name to use for the resources.')
param baseName string

@description('The location to deploy the resources.')
param location string = resourceGroup().location

@description('The tags to apply to the resources.')
param tags object = {}

@description('The address prefix for the virtual network.')
param vnetAddressPrefix string = '10.0.0.0/16'

@description('The address prefix for the search subnet.')
param searchSubnetAddressPrefix string = '10.0.1.0/24'

@description('The address prefix for the app service subnet.')
param appServiceSubnetAddressPrefix string = '10.0.2.0/24'

@description('The address prefix for the open ai subnet.')
param openAiSubnetAddressPrefix string = '10.0.3.0/24'

// Variables
var vnetName = 'vnet-${baseName}'
var searchNsgName = 'nsg-search-${baseName}'
var appServiceNsgName = 'nsg-appservice-${baseName}'
var openAiNsgName = 'nsg-openai-${baseName}'
var routeTableName = 'rt-${baseName}'
var searchSubnetName = 'snet-search-${baseName}'
var appServiceSubnetName = 'snet-appservice-${baseName}'
var openAiSubnetName = 'snet-openai-${baseName}'

// Network Security Groups
resource searchNsg 'Microsoft.Network/networkSecurityGroups@2023-05-01' = {
  name: searchNsgName
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowHttpsInbound'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: 'VirtualNetwork'
          destinationAddressPrefix: '*'
          sourcePortRange: '*'
          destinationPortRange: '443'
        }
      }
    ]
  }
}

resource appServiceNsg 'Microsoft.Network/networkSecurityGroups@2023-05-01' = {
  name: appServiceNsgName
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowHttpsInbound'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
          sourcePortRange: '*'
          destinationPortRange: '443'
        }
      }
    ]
  }
}

resource openAiNsg 'Microsoft.Network/networkSecurityGroups@2023-05-01' = {
  name: openAiNsgName
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowHttpsInbound'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: 'VirtualNetwork'
          destinationAddressPrefix: '*'
          sourcePortRange: '*'
          destinationPortRange: '443'
        }
      }
    ]
  }
}

// Route Table
resource routeTable 'Microsoft.Network/routeTables@2023-05-01' = {
  name: routeTableName
  location: location
  tags: tags
  properties: {
    disableBgpRoutePropagation: false
    routes: [
      {
        name: 'DefaultRoute'
        properties: {
          addressPrefix: '0.0.0.0/0'
          nextHopType: 'VirtualNetworkGateway'
        }
      }
    ]
  }
}

// Virtual Network
resource vnet 'Microsoft.Network/virtualNetworks@2023-05-01' = {
  name: vnetName
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressPrefix
      ]
    }
    subnets: [
      {
        name: searchSubnetName
        properties: {
          addressPrefix: searchSubnetAddressPrefix
          networkSecurityGroup: {
            id: searchNsg.id
          }
          routeTable: {
            id: routeTable.id
          }
          privateEndpointNetworkPolicies: 'Disabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
      {
        name: appServiceSubnetName
        properties: {
          addressPrefix: appServiceSubnetAddressPrefix
          networkSecurityGroup: {
            id: appServiceNsg.id
          }
          routeTable: {
            id: routeTable.id
          }
          delegations: [
            {
              name: 'delegation'
              properties: {
                serviceName: 'Microsoft.Web/serverFarms'
              }
            }
          ]
          privateEndpointNetworkPolicies: 'Disabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
      {
        name: openAiSubnetName
        properties: {
          addressPrefix: openAiSubnetAddressPrefix
          networkSecurityGroup: {
            id: openAiNsg.id
          }
          routeTable: {
            id: routeTable.id
          }
          privateEndpointNetworkPolicies: 'Disabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
    ]
  }
}

// Outputs
output vnetId string = vnet.id
output searchSubnetId string = resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, searchSubnetName)
output appServiceSubnetId string = resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, appServiceSubnetName)
output openAiSubnetId string = resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, openAiSubnetName)
