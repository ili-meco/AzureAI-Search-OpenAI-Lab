@description('The base name to use for the resources.')
param baseName string

@description('The location to deploy the resources.')
param location string = resourceGroup().location

@description('The tags to apply to the resources.')
param tags object = {}

// Networking module parameters
@description('The address prefix for the virtual network.')
param vnetAddressPrefix string = '10.0.0.0/16'

@description('The address prefix for the search subnet.')
param searchSubnetAddressPrefix string = '10.0.1.0/24'

@description('The address prefix for the app service subnet.')
param appServiceSubnetAddressPrefix string = '10.0.2.0/24'

@description('The address prefix for the open ai subnet.')
param openAiSubnetAddressPrefix string = '10.0.3.0/24'

// Azure AI Search parameters
@description('The SKU for the Azure AI Search service.')
@allowed([
  'basic'
  'standard'
  'standard2'
  'standard3'
])
param searchSku string = 'standard'

@description('Whether to create a private endpoint for the Azure AI Search service.')
param createPrivateEndpoint bool = true

// Azure OpenAI parameters
@description('The SKU for the Azure OpenAI service.')
param openAiSku string = 'S0'

@description('The name of the embedding model deployment.')
param embeddingModelDeploymentName string = 'text-embedding-ada-002'

@description('Pricing tier of the search service.')
@allowed([
  'Free'
  'Basic'
  'Standard'
  'Standard2'
  'Standard3'
])
param searchServiceSku string = 'Standard'

// Include modules
module networking 'modules/networking.bicep' = {
  name: 'networking-deployment'
  params: {
    baseName: baseName
    location: location
    tags: tags
    vnetAddressPrefix: vnetAddressPrefix
    searchSubnetAddressPrefix: searchSubnetAddressPrefix
    appServiceSubnetAddressPrefix: appServiceSubnetAddressPrefix
    openAiSubnetAddressPrefix: openAiSubnetAddressPrefix
  }
}

module openAi 'modules/openai.bicep' = {
  name: 'openai-deployment'
  params: {
    baseName: baseName
    location: location
    tags: tags
    sku: openAiSku
    embeddingModelDeploymentName: embeddingModelDeploymentName
    subnetId: networking.outputs.openAiSubnetId
    createPrivateEndpoint: createPrivateEndpoint
  }
}

module search 'modules/search.bicep' = {
  name: 'search-deployment'
  params: {
    baseName: baseName
    location: location
    tags: tags
    sku: searchSku
    subnetId: networking.outputs.searchSubnetId
    createPrivateEndpoint: createPrivateEndpoint
  }
}

module appService 'modules/appservice.bicep' = {
  name: 'appservice-deployment'
  params: {
    baseName: baseName
    location: location
    tags: tags
    subnetId: networking.outputs.appServiceSubnetId
    searchServiceEndpoint: search.outputs.searchServiceEndpoint
    openAiEndpoint: openAi.outputs.openAiEndpoint
  }
}

module security 'modules/security.bicep' = {
  name: 'security-deployment'
  params: {
    baseName: baseName
    location: location
    tags: tags
    searchServiceId: search.outputs.searchServiceId
    openAiServiceId: openAi.outputs.openAiServiceId
    appServicePrincipalId: appService.outputs.appServicePrincipalId
  }
}

// Outputs
output searchServiceEndpoint string = search.outputs.searchServiceEndpoint
output searchServiceId string = search.outputs.searchServiceId
output openAiEndpoint string = openAi.outputs.openAiEndpoint
output openAiServiceId string = openAi.outputs.openAiServiceId
output appServiceUrl string = appService.outputs.appServiceUrl
