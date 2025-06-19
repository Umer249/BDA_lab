@description('Location for all resources')
param location string = resourceGroup().location

@description('Name of the container registry')
param registryName string = 'automlregistry${uniqueString(resourceGroup().id)}'

@description('Name of the container instance')
param containerInstanceName string = 'automl-container'

@description('DNS name label for the container instance')
param dnsNameLabel string = 'automl-app-${uniqueString(resourceGroup().id)}'

@description('Container image to deploy')
param containerImage string = 'automlregistry.azurecr.io/automl-app:latest'

@description('Number of CPU cores for the container')
param cpuCores int = 2

@description('Amount of memory in GB for the container')
param memoryInGb int = 4

// Container Registry
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: registryName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

// Container Instance
resource containerInstance 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: containerInstanceName
  location: location
  properties: {
    containers: [
      {
        name: 'automl-app'
        properties: {
          image: containerImage
          ports: [
            {
              port: 8501
              protocol: 'TCP'
            }
          ]
          environmentVariables: [
            {
              name: 'STREAMLIT_SERVER_PORT'
              value: '8501'
            }
            {
              name: 'STREAMLIT_SERVER_ADDRESS'
              value: '0.0.0.0'
            }
            {
              name: 'STREAMLIT_SERVER_HEADLESS'
              value: 'true'
            }
            {
              name: 'STREAMLIT_BROWSER_GATHER_USAGE_STATS'
              value: 'false'
            }
          ]
          resources: {
            requests: {
              cpu: cpuCores
              memoryInGB: memoryInGb
            }
          }
          livenessProbe: {
            httpGet: {
              path: '/_stcore/health'
              port: 8501
            }
            initialDelaySeconds: 60
            periodSeconds: 30
          }
          readinessProbe: {
            httpGet: {
              path: '/_stcore/health'
              port: 8501
            }
            initialDelaySeconds: 30
            periodSeconds: 10
          }
        }
      }
    ]
    osType: 'Linux'
    ipAddress: {
      type: 'Public'
      ports: [
        {
          port: 8501
          protocol: 'TCP'
        }
      ]
      dnsNameLabel: dnsNameLabel
    }
    imageRegistryCredentials: [
      {
        server: containerRegistry.properties.loginServer
        username: containerRegistry.name
        password: containerRegistry.listCredentials().passwords[0].value
      }
    ]
    restartPolicy: 'Always'
  }
  dependsOn: [
    containerRegistry
  ]
}

// Storage Account for persistent data
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'automlstorage${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
}

// File Share for models and reports
resource fileShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-01-01' = {
  name: '${storageAccount.name}/default/automl-data'
  properties: {
    shareQuota: 100
  }
}

// Log Analytics Workspace for monitoring
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'automl-logs-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Application Insights for application monitoring
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'automl-insights-${uniqueString(resourceGroup().id)}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// Outputs
output registryLoginServer string = containerRegistry.properties.loginServer
output containerInstanceFQDN string = containerInstance.properties.ipAddress.fqdn
output applicationUrl string = 'http://${containerInstance.properties.ipAddress.fqdn}:8501'
output storageAccountName string = storageAccount.name
output fileShareName string = fileShare.name 