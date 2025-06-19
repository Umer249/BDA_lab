# Azure AutoML App Deployment Script (PowerShell)
# This script deploys the AutoML application to Azure Container Instances

param(
    [string]$ResourceGroup = "automl-rg",
    [string]$Location = "eastus",
    [string]$RegistryName = "automlregistry$(Get-Random -Maximum 1000)",
    [string]$ImageName = "automl-app",
    [string]$ContainerName = "automl-container",
    [string]$AppName = "automl-web-app-$(Get-Random -Maximum 1000)"
)

Write-Host "🚀 Starting Azure deployment for AutoML application..." -ForegroundColor Green

# Check if Azure CLI is installed
try {
    az --version | Out-Null
    Write-Host "✅ Azure CLI is installed" -ForegroundColor Green
}
catch {
    Write-Host "❌ Azure CLI is not installed. Please install it first." -ForegroundColor Red
    Write-Host "Download from: https://aka.ms/installazurecliwindows" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Login to Azure (if not already logged in)
Write-Host "🔐 Checking Azure login status..." -ForegroundColor Cyan
try {
    az account show | Out-Null
    Write-Host "✅ Already logged into Azure" -ForegroundColor Green
}
catch {
    Write-Host "Please login to Azure:" -ForegroundColor Yellow
    az login
}

# Create resource group
Write-Host "📦 Creating resource group: $ResourceGroup" -ForegroundColor Cyan
az group create --name $ResourceGroup --location $Location

# Create Azure Container Registry
Write-Host "🏗️ Creating Azure Container Registry: $RegistryName" -ForegroundColor Cyan
az acr create `
    --resource-group $ResourceGroup `
    --name $RegistryName `
    --sku Basic `
    --admin-enabled true

# Get ACR login server
$AcrLoginServer = az acr show --name $RegistryName --query loginServer --output tsv
Write-Host "🔗 ACR Login Server: $AcrLoginServer" -ForegroundColor Cyan

# Build Docker image
Write-Host "🐳 Building Docker image..." -ForegroundColor Cyan
docker build -t $ImageName .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

# Tag image for ACR
Write-Host "🏷️ Tagging image for ACR..." -ForegroundColor Cyan
docker tag $ImageName "$AcrLoginServer/$ImageName`:latest"

# Get ACR credentials
Write-Host "🔑 Getting ACR credentials..." -ForegroundColor Cyan
$AcrUsername = az acr credential show --name $RegistryName --query username --output tsv
$AcrPassword = az acr credential show --name $RegistryName --query passwords[0].value --output tsv

# Login to ACR
Write-Host "🔐 Logging into ACR..." -ForegroundColor Cyan
echo $AcrPassword | docker login $AcrLoginServer --username $AcrUsername --password-stdin

# Push image to ACR
Write-Host "⬆️ Pushing image to ACR..." -ForegroundColor Cyan
docker push "$AcrLoginServer/$ImageName`:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker push failed!" -ForegroundColor Red
    exit 1
}

# Deploy to Azure Container Instances
Write-Host "🚀 Deploying to Azure Container Instances..." -ForegroundColor Cyan
az container create `
    --resource-group $ResourceGroup `
    --name $ContainerName `
    --image "$AcrLoginServer/$ImageName`:latest" `
    --cpu 2 `
    --memory 4 `
    --registry-login-server $AcrLoginServer `
    --registry-username $AcrUsername `
    --registry-password $AcrPassword `
    --ports 8501 `
    --dns-name-label $AppName `
    --environment-variables `
        STREAMLIT_SERVER_PORT=8501 `
        STREAMLIT_SERVER_ADDRESS=0.0.0.0 `
        STREAMLIT_SERVER_HEADLESS=true `
        STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Get the FQDN
$Fqdn = az container show --resource-group $ResourceGroup --name $ContainerName --query ipAddress.fqdn --output tsv

Write-Host ""
Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host "🌐 Your AutoML application is available at: http://$Fqdn:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Deployment Summary:" -ForegroundColor Cyan
Write-Host "  Resource Group: $ResourceGroup" -ForegroundColor White
Write-Host "  Container Registry: $RegistryName" -ForegroundColor White
Write-Host "  Container Instance: $ContainerName" -ForegroundColor White
Write-Host "  Application URL: http://$Fqdn:8501" -ForegroundColor White
Write-Host ""
Write-Host "🛠️ Management Commands:" -ForegroundColor Cyan
Write-Host "  View logs: az container logs --resource-group $ResourceGroup --name $ContainerName" -ForegroundColor White
Write-Host "  Restart: az container restart --resource-group $ResourceGroup --name $ContainerName" -ForegroundColor White
Write-Host "  Delete: az container delete --resource-group $ResourceGroup --name $ContainerName --yes" -ForegroundColor White
Write-Host ""
Write-Host "💰 Estimated monthly cost: $15-30 USD (2 CPU, 4GB RAM)" -ForegroundColor Yellow 