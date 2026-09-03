using './main.bicep'

//parameters file

param rgName = 'poc1-rg'
param location = 'eastus'
param searchServiceName = 'poc1-searchservice'

param sqlServerName = 'patient-data-sqlsvr'
param sqlAdminLogin = 'vaishnavi'
param sqlDatabaseName = 'patient-data-db'

param sqlAdminPassword = readEnvironmentVariable('SQL_ADMIN_PASSWORD')

param sql_location = 'eastasia'

param hubName = 'POC--1-ProjectHub' // AI Hub workspace name
param domainName = aiName // Custom subdomain for the workspace

param projectName = 'POC--1-Projects' // Project name

param modelDeployments = [
  {
    model: { name: 'gpt-4.1', version: '2025-04-14' }
    sku: { name: 'GlobalStandard', capacity: 250 }
  }
  {
    model: { name: 'text-embedding-3-small', version: '1' }
    sku: { name: 'GlobalStandard', capacity: 250 }
  }
]

param aiName = 'veapocfirst--aiservice'

param storageName = 'veademofiostore'
param logAnalyticsWorkspaceName = 'poc1-log-analytics-workspace'

param containerRegistryname = 'poc1containerreg'

param KeyVaultName = 'veademokey'

param semantic_location = 'westeurope'

param embeddingModel = 'text-embedding-3-small'

param modelName = 'gpt-4.1'

param searchIndexName = 'medical-docs-index'

param serpApiKey = readEnvironmentVariable('SERP_API_KEY')

param sqlServerURL = '${sqlServerName}.database.windows.net'

param uamiName = 'POCs-with-llmops'

param agentSubnetName =  'Agent-Subnet'

param peSubnetName =  'Hub-Subnet'

param vmSubnetName = 'VM'

param vnetName =  'poc-01-vnet'


param existingDnsZones = {
  'privatelink.services.ai.azure.com': ''
  'privatelink.openai.azure.com': ''
  'privatelink.cognitiveservices.azure.com': ''               
  'privatelink.search.windows.net': ''           
  'privatelink.blob.core.windows.net': ''                            
}


param adminUsername =  'vaishnavi'

param nicName =  'poc1-nic'

param nsgName =  'poc1-nsg'

param publicIpName =  'poc1-publicip'

param vmName =  'poc1-vm'

param adminPassword =  param adminPassword = readEnvironmentVariable('VM_ADMIN_PASSWORD')

param spTenantID =  '4f06e6e8-ae4a-4b64-882a-792a2a921809'

param spPrincipalID = '9a31d657-9d30-40b4-9c2d-7749f5b45562'

param spClientID = '0feadbbf-187f-4066-a0b0-5223cd00b83b'

param containerNames =  ['documents']
