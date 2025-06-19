#!/bin/bash

# Azure Cloud Shell Deployment Script for AutoML App
# Run this in Azure Cloud Shell after uploading your project files

echo "🚀 Starting Azure deployment for AutoML application..."

# Configuration
RESOURCE_GROUP="automl-rg"
LOCATION="eastus"
REGISTRY_NAME="automlregistry$(date +%s)"
IMAGE_NAME="automl-app"
CONTAINER_NAME="automl-container"
APP_NAME="automl-web-app-$(date +%s)"

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

# Build Docker image using Azure Container Registry build
echo "🐳 Building Docker image in Azure..."
az acr build --registry $REGISTRY_NAME --image $IMAGE_NAME:latest .

# Get ACR credentials
echo "🔑 Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query passwords[0].value --output tsv)

# Deploy to Azure Container Instances
echo "🚀 Deploying to Azure Container Instances..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image "$ACR_LOGIN_SERVER/$IMAGE_NAME:latest" \
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

echo ""
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
echo ""
echo "💰 Estimated monthly cost: \$15-30 USD (2 CPU, 4GB RAM)" 