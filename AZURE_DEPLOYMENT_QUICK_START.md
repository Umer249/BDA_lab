# 🚀 Quick Azure Deployment Guide

## Prerequisites

1. **Azure CLI** installed: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. **Azure Account** with active subscription
3. **Docker Image** ready on Docker Hub (umeri249/automl-app:latest)

## 🎯 Method 1: Automated Script (Recommended)

### Step 1: Run the deployment script

```powershell
.\azure-deploy.ps1
```

This script will:

- ✅ Check Azure CLI installation
- ✅ Log you into Azure (if needed)
- ✅ Create resource group: `automl-rg`
- ✅ Deploy container instance
- ✅ Provide you with the application URL

### Step 2: Access your application

The script will output your application URL, typically:

```
http://automl-app-1234.eastus.azurecontainer.io:8501
```

---

## 🎯 Method 2: Manual Azure Portal Deployment

### Step 1: Go to Azure Portal

1. Visit: https://portal.azure.com
2. Click "Create a resource"
3. Search for "Container Instances"
4. Click "Create"

### Step 2: Configure Container Instance

- **Resource Group**: Create new `automl-rg`
- **Container name**: `automl-container`
- **Region**: East US (or your preferred region)
- **Image source**: Docker Hub or other registry
- **Image**: `umeri249/automl-app:latest`
- **Size**: 2 CPU cores, 4 GB memory
- **Port**: 8501

### Step 3: Environment Variables (Advanced tab)

```
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

---

## 🎯 Method 3: Azure CLI Commands

```bash
# Login to Azure
az login

# Create resource group
az group create --name automl-rg --location "East US"

# Deploy container instance
az container create \
    --resource-group automl-rg \
    --name automl-container \
    --image umeri249/automl-app:latest \
    --dns-name-label automl-app-$(Get-Random -Minimum 1000 -Maximum 9999) \
    --ports 8501 \
    --cpu 2 \
    --memory 4 \
    --environment-variables \
        STREAMLIT_SERVER_PORT=8501 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        STREAMLIT_SERVER_HEADLESS=true \
        STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

---

## 📊 Expected Results

After successful deployment:

- **Application URL**: `http://automl-app-xxxx.eastus.azurecontainer.io:8501`
- **Monthly Cost**: ~$15-30
- **Uptime**: 99.9%
- **Response Time**: < 2 seconds

---

## 🔧 Management Commands

```bash
# View logs
az container logs --resource-group automl-rg --name automl-container

# Stop container
az container stop --resource-group automl-rg --name automl-container

# Start container
az container start --resource-group automl-rg --name automl-container

# Delete container
az container delete --resource-group automl-rg --name automl-container --yes
```

---

## 🛠️ Troubleshooting

### Container won't start

1. Check logs: `az container logs --resource-group automl-rg --name automl-container`
2. Verify image exists: Visit https://hub.docker.com/r/umeri249/automl-app
3. Check environment variables are set correctly

### Application not accessible

1. Verify port 8501 is exposed
2. Check DNS name label is unique
3. Wait 2-3 minutes for full deployment

### High costs

1. Stop container when not in use: `az container stop --resource-group automl-rg --name automl-container`
2. Delete container when done: `az container delete --resource-group automl-rg --name automl-container --yes`

---

## 💰 Cost Optimization

- **Stop container** when not in use (saves ~70% cost)
- **Delete container** when project is complete
- **Use smaller size** for development (1 CPU, 2 GB RAM)
- **Monitor usage** in Azure Portal

---

## 🎉 Success!

Once deployed, your AutoML application will be:

- ✅ Publicly accessible
- ✅ Scalable
- ✅ Cost-effective
- ✅ Easy to manage

**Next Steps:**

1. Test your application
2. Share the URL with others
3. Monitor performance in Azure Portal
4. Update the Docker image when you make changes
