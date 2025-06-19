# Azure Deployment Script for AutoML App
# This script deploys the Docker image to Azure Container Instances

param(
    [string]$ResourceGroupName = "automl-rg",
    [string]$Location = "East US",
    [string]$ContainerName = "automl-container",
    [string]$DnsNameLabel = "automl-app-$(Get-Random -Minimum 1000 -Maximum 9999)",
    [string]$DockerImage = "umeri249/automl-app:latest"
)

Write-Host "🚀 Starting Azure Deployment..." -ForegroundColor Green
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Yellow
Write-Host "Location: $Location" -ForegroundColor Yellow
Write-Host "Container Name: $ContainerName" -ForegroundColor Yellow
Write-Host "DNS Label: $DnsNameLabel" -ForegroundColor Yellow
Write-Host "Docker Image: $DockerImage" -ForegroundColor Yellow

# Check if Azure CLI is installed
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Host "✅ Azure CLI version: $($azVersion.'azure-cli')" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI not found. Please install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Red
    exit 1
}

# Check if logged in to Azure
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "✅ Logged in as: $($account.user.name)" -ForegroundColor Green
} catch {
    Write-Host "🔐 Please log in to Azure..." -ForegroundColor Yellow
    az login
}

# Create Resource Group
Write-Host "📦 Creating Resource Group..." -ForegroundColor Blue
az group create --name $ResourceGroupName --location $Location

# Deploy Container Instance
Write-Host "🐳 Deploying Container Instance..." -ForegroundColor Blue
az container create `
    --resource-group $ResourceGroupName `
    --name $ContainerName `
    --image $DockerImage `
    --dns-name-label $DnsNameLabel `
    --ports 8501 `
    --cpu 2 `
    --memory 4 `
    --environment-variables `
        STREAMLIT_SERVER_PORT=8501 `
        STREAMLIT_SERVER_ADDRESS=0.0.0.0 `
        STREAMLIT_SERVER_HEADLESS=true `
        STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
    
    # Get the application URL
    $container = az container show --resource-group $ResourceGroupName --name $ContainerName --output json | ConvertFrom-Json
    $appUrl = "http://$($container.ipAddress.fqdn):8501"
    
    Write-Host "🌐 Your application is available at:" -ForegroundColor Green
    Write-Host $appUrl -ForegroundColor Cyan
    
    Write-Host "📊 Container Status:" -ForegroundColor Yellow
    Write-Host "   State: $($container.provisioningState)" -ForegroundColor White
    Write-Host "   IP Address: $($container.ipAddress.ip)" -ForegroundColor White
    Write-Host "   FQDN: $($container.ipAddress.fqdn)" -ForegroundColor White
    
    # Save deployment info to file
    $deploymentInfo = @{
        ResourceGroup = $ResourceGroupName
        ContainerName = $ContainerName
        ApplicationUrl = $appUrl
        DockerImage = $DockerImage
        DeploymentTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    
    $deploymentInfo | ConvertTo-Json | Out-File -FilePath "azure-deployment-info.json" -Encoding UTF8
    Write-Host "💾 Deployment info saved to: azure-deployment-info.json" -ForegroundColor Green
    
} else {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host "Check the error messages above and try again." -ForegroundColor Red
}

Write-Host "`n🔧 Useful Commands:" -ForegroundColor Yellow
Write-Host "   View logs: az container logs --resource-group $ResourceGroupName --name $ContainerName" -ForegroundColor White
Write-Host "   Stop container: az container stop --resource-group $ResourceGroupName --name $ContainerName" -ForegroundColor White
Write-Host "   Start container: az container start --resource-group $ResourceGroupName --name $ContainerName" -ForegroundColor White
Write-Host "   Delete container: az container delete --resource-group $ResourceGroupName --name $ContainerName --yes" -ForegroundColor White 