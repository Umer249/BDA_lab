# 🌊 Azure Deployment Guide for AutoML Web Application

This guide provides multiple ways to deploy your AutoML application to Microsoft Azure.

## 📋 Prerequisites

### 1. Install Required Tools

#### Azure CLI

```powershell
# Windows (PowerShell as Administrator)
winget install Microsoft.AzureCLI

# Or download from: https://aka.ms/installazurecliwindows
```

#### Docker Desktop

- Download from: https://www.docker.com/products/docker-desktop
- Install and ensure Docker is running

#### Azure Subscription

- Get a free Azure account: https://azure.microsoft.com/free/
- $200 free credits for new users

### 2. Login to Azure

```bash
az login
```

## 🚀 Deployment Options

### Option 1: Automated Deployment (Recommended)

#### Using PowerShell (Windows)

```powershell
# Navigate to your project directory
cd D:\bda_class

# Run the automated deployment script
.\deployment\azure\deploy.ps1
```

#### Using Bash (Linux/Mac)

```bash
# Make the script executable
chmod +x deployment/azure/deploy.sh

# Run the deployment
./deployment/azure/deploy.sh
```

### Option 2: Manual Step-by-Step Deployment

#### Step 1: Create Resource Group

```bash
az group create --name automl-rg --location eastus
```

#### Step 2: Create Container Registry

```bash
az acr create \
    --resource-group automl-rg \
    --name automlregistry$(date +%s) \
    --sku Basic \
    --admin-enabled true
```

#### Step 3: Build and Push Docker Image

```bash
# Build the image
docker build -t automl-app .

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name automlregistry --query loginServer --output tsv)

# Tag for ACR
docker tag automl-app $ACR_LOGIN_SERVER/automl-app:latest

# Login to ACR
az acr login --name automlregistry

# Push image
docker push $ACR_LOGIN_SERVER/automl-app:latest
```

#### Step 4: Deploy to Container Instances

```bash
az container create \
    --resource-group automl-rg \
    --name automl-container \
    --image $ACR_LOGIN_SERVER/automl-app:latest \
    --cpu 2 \
    --memory 4 \
    --registry-login-server $ACR_LOGIN_SERVER \
    --registry-username $(az acr credential show --name automlregistry --query username --output tsv) \
    --registry-password $(az acr credential show --name automlregistry --query passwords[0].value --output tsv) \
    --ports 8501 \
    --dns-name-label automl-web-app-$(date +%s) \
    --environment-variables \
        STREAMLIT_SERVER_PORT=8501 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        STREAMLIT_SERVER_HEADLESS=true \
        STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Option 3: Infrastructure as Code (Bicep)

Using the included Bicep template for more advanced deployment:

```bash
# Deploy using Bicep template
az deployment group create \
    --resource-group automl-rg \
    --template-file deployment/azure/bicep/main.bicep \
    --parameters \
        containerImage=automlregistry.azurecr.io/automl-app:latest \
        dnsNameLabel=automl-app-$(date +%s)
```

### Option 4: Azure App Service (Alternative)

For a more managed approach:

```bash
# Create App Service Plan
az appservice plan create \
    --name automl-plan \
    --resource-group automl-rg \
    --sku B1 \
    --is-linux

# Create Web App
az webapp create \
    --resource-group automl-rg \
    --plan automl-plan \
    --name automl-webapp-$(date +%s) \
    --deployment-container-image-name automlregistry.azurecr.io/automl-app:latest
```

## 🔧 Configuration Options

### Environment Variables

You can customize the deployment by setting these environment variables:

```bash
# Container configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true

# AutoML configuration
MAX_MODEL_COUNT=10
DEFAULT_TASK_TYPE=classification

# Azure Storage (optional for persistence)
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_STORAGE_CONTAINER_NAME=automl-models
```

### Resource Sizing

| Configuration | CPU | Memory | Monthly Cost\* |
| ------------- | --- | ------ | -------------- |
| Small         | 1   | 2 GB   | $8-15          |
| Medium        | 2   | 4 GB   | $15-30         |
| Large         | 4   | 8 GB   | $30-60         |

\*Estimated costs for Container Instances in East US region

## 📊 Monitoring and Management

### View Application Logs

```bash
az container logs --resource-group automl-rg --name automl-container --follow
```

### Restart Container

```bash
az container restart --resource-group automl-rg --name automl-container
```

### Scale Resources

```bash
az container create \
    --resource-group automl-rg \
    --name automl-container-large \
    --cpu 4 \
    --memory 8 \
    --image automlregistry.azurecr.io/automl-app:latest
```

### Enable Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
    --app automl-insights \
    --location eastus \
    --resource-group automl-rg

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
    --app automl-insights \
    --resource-group automl-rg \
    --query instrumentationKey \
    --output tsv)

# Add to container environment
--environment-variables APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=$INSTRUMENTATION_KEY
```

## 🔒 Security Best Practices

### 1. Use Managed Identity

```bash
# Create managed identity
az identity create \
    --resource-group automl-rg \
    --name automl-identity

# Assign to container
--assign-identity /subscriptions/{subscription-id}/resourcegroups/automl-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/automl-identity
```

### 2. Enable HTTPS

```bash
# Use Azure Application Gateway or Front Door for SSL termination
az network application-gateway create \
    --name automl-gateway \
    --resource-group automl-rg \
    --cert-file your-certificate.pfx
```

### 3. Network Security

```bash
# Create virtual network
az network vnet create \
    --resource-group automl-rg \
    --name automl-vnet \
    --subnet-name automl-subnet

# Deploy container to subnet
--subnet /subscriptions/{subscription-id}/resourceGroups/automl-rg/providers/Microsoft.Network/virtualNetworks/automl-vnet/subnets/automl-subnet
```

## 🧪 Testing Your Deployment

### 1. Health Check

```bash
# Get the application URL
FQDN=$(az container show --resource-group automl-rg --name automl-container --query ipAddress.fqdn --output tsv)

# Test health endpoint
curl http://$FQDN:8501/_stcore/health
```

### 2. Load Testing

```bash
# Install Artillery (optional)
npm install -g artillery

# Create load test config
cat > load-test.yml << EOF
config:
  target: 'http://$FQDN:8501'
  phases:
    - duration: 60
      arrivalRate: 5
scenarios:
  - name: "Load test"
    requests:
      - get:
          url: "/"
EOF

# Run load test
artillery run load-test.yml
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check container logs
az container logs --resource-group automl-rg --name automl-container

# Check container events
az container show --resource-group automl-rg --name automl-container --query instanceView.events
```

#### 2. Out of Memory Errors

```bash
# Increase memory allocation
az container create \
    --memory 8 \
    # ... other parameters
```

#### 3. PyCaret Installation Issues

```bash
# Build with specific Python version
# Update Dockerfile:
FROM python:3.9-slim

# Install system dependencies for PyCaret
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libc6-dev
```

#### 4. Slow Performance

- Increase CPU allocation (--cpu 4)
- Use Premium storage for data persistence
- Enable Application Insights for performance monitoring

### Performance Optimization

#### 1. Enable Caching

```bash
# Add Redis cache
az redis create \
    --resource-group automl-rg \
    --name automl-cache \
    --location eastus \
    --sku Basic \
    --vm-size c0

# Update container with Redis connection
--environment-variables REDIS_CONNECTION_STRING=your_redis_connection
```

#### 2. Use Azure Storage for Models

```bash
# Create storage account
az storage account create \
    --resource-group automl-rg \
    --name automlstorage$(date +%s) \
    --sku Standard_LRS

# Create container for models
az storage container create \
    --name models \
    --account-name automlstorage
```

## 💰 Cost Optimization

### 1. Use Spot Instances (Container Instances)

```bash
# Deploy with spot pricing (when available)
az container create \
    --priority Spot \
    # ... other parameters
```

### 2. Auto-shutdown Schedule

```bash
# Create automation account for scheduling
az automation account create \
    --resource-group automl-rg \
    --name automl-automation
```

### 3. Monitor Costs

```bash
# Set up budget alerts
az consumption budget create \
    --resource-group automl-rg \
    --budget-name automl-budget \
    --amount 50 \
    --time-grain Monthly
```

## 📞 Support

- Azure Support: https://azure.microsoft.com/support/
- Container Instances Documentation: https://docs.microsoft.com/azure/container-instances/
- Pricing Calculator: https://azure.microsoft.com/pricing/calculator/

## 🎯 Next Steps

After successful deployment:

1. **Set up monitoring** with Application Insights
2. **Configure autoscaling** based on usage
3. **Implement CI/CD** with Azure DevOps or GitHub Actions
4. **Add custom domain** and SSL certificate
5. **Set up backup strategy** for models and data

---

**Need help?** Check the troubleshooting section or open an issue in the repository.
