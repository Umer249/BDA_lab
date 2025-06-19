#!/bin/bash

# Azure AutoML App Deployment Script
# This script deploys the AutoML application to Azure Container Instances

set -e

# Configuration
RESOURCE_GROUP="automl-rg"
LOCATION="eastus"
REGISTRY_NAME="automlregistry"
IMAGE_NAME="automl-app"
CONTAINER_NAME="automl-container"
APP_NAME="automl-web-app"

echo "🚀 Starting Azure deployment for AutoML application..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first."
    exit 1
fi

# Login to Azure (if not already logged in)
echo "🔐 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "Please login to Azure:"
    az login
fi

# Create resource group
echo "📦 Creating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo "🏗️ Creating Azure Container Registry: $REGISTRY_NAME"
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $REGISTRY_NAME \
    --sku Basic \
    --admin-enabled true

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $REGISTRY_NAME --query loginServer --output tsv)
echo "🔗 ACR Login Server: $ACR_LOGIN_SERVER"

# Build and push Docker image
echo "🐳 Building Docker image..."
docker build -t $IMAGE_NAME .

echo "🏷️ Tagging image for ACR..."
docker tag $IMAGE_NAME $ACR_LOGIN_SERVER/$IMAGE_NAME:latest

echo "🔑 Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query passwords[0].value --output tsv)

echo "🔐 Logging into ACR..."
docker login $ACR_LOGIN_SERVER --username $ACR_USERNAME --password $ACR_PASSWORD

echo "⬆️ Pushing image to ACR..."
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:latest

# Deploy to Azure Container Instances
echo "🚀 Deploying to Azure Container Instances..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image $ACR_LOGIN_SERVER/$IMAGE_NAME:latest \
    --cpu 2 \
    --memory 4 \
    --registry-login-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --ports 8501 \
    --dns-name-label $APP_NAME \
    --environment-variables \
        STREAMLIT_SERVER_PORT=8501 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        STREAMLIT_SERVER_HEADLESS=true \
        STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Get the FQDN
FQDN=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query ipAddress.fqdn --output tsv)

echo "✅ Deployment completed successfully!"
echo "🌐 Your AutoML application is available at: http://$FQDN:8501"
echo ""
echo "📋 Deployment Summary:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Container Registry: $REGISTRY_NAME"
echo "  Container Instance: $CONTAINER_NAME"
echo "  Application URL: http://$FQDN:8501"
echo ""
echo "🛠️ Management Commands:"
echo "  View logs: az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
echo "  Restart: az container restart --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
echo "  Delete: az container delete --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --yes" 