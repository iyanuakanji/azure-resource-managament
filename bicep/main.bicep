targetScope = 'subscription'

@description('Azure region for the resource group.')
param location string = 'eastus'

@description('Name of the resource group to manage.')
param resourceGroupName string

resource resourceGroup 'Microsoft.Resources/resourceGroups@2025-04-01' = {
  name: resourceGroupName
  location: location
}

output resourceGroupId string = resourceGroup.id
