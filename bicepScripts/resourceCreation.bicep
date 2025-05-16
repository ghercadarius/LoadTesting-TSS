param location string = resourceGroup().location

param loadTestName string = 'TSSLoadTest'

resource loadTest 'Microsoft.LoadTestService/loadTests@2024-12-01-preview' = {
  name: loadTestName
  location: location
}
