# 🌊 Azure Portal Deployment Guide (No Shell Required)

## Deploy Your AutoML App Using Azure Portal Interface

### Prerequisites

- Azure account (get free $200 credits at https://azure.microsoft.com/free/)
- Your project files ready (we'll use Docker Hub instead of local Docker)

## 🚀 Method 1: Deploy to Azure Container Instances (Recommended)

### Step 1: Create Resource Group

1. Go to **Azure Portal**: https://portal.azure.com
2. Click **"Resource groups"** in the left menu
3. Click **"+ Create"**
4. Fill in:
   - **Subscription**: Your subscription
   - **Resource group name**: `automl-rg`
   - **Region**: `East US`
5. Click **"Review + Create"** → **"Create"**

### Step 2: Create Container Registry (to store your Docker image)

1. In Azure Portal, search **"Container registries"**
2. Click **"+ Create"**
3. Fill in:
   - **Resource group**: `automl-rg`
   - **Registry name**: `automlregistry` + random numbers (must be unique)
   - **Location**: `East US`
   - **SKU**: `Basic`
   - **Admin user**: `Enabled`
4. Click **"Review + Create"** → **"Create"**
5. **Wait for deployment to complete**

### Step 3: Build Docker Image in Azure (No Local Docker Needed!)

1. Go to your **Container Registry** resource
2. Click **"Tasks"** in the left menu
3. Click **"Quick run"**
4. Fill in:
   - **Source location**: `GitHub` or `Upload local context`
   - **Repository URL**: Your GitHub repo URL OR upload your project files
   - **Dockerfile**: `Dockerfile`
   - **Image name**: `automl-app:latest`
5. Click **"Run"**
6. **Wait for build to complete** (5-10 minutes)

### Step 4: Create Container Instance

1. In Azure Portal, search **"Container instances"**
2. Click **"+ Create"**
3. **Basics tab**:

   - **Resource group**: `automl-rg`
   - **Container name**: `automl-container`
   - **Region**: `East US`
   - **Image source**: `Azure Container Registry`
   - **Registry**: Select your registry (`automlregistry...`)
   - **Image**: `automl-app`
   - **Image tag**: `latest`
   - **Size**:
     - **CPU cores**: `2`
     - **Memory**: `4 GB`

4. **Networking tab**:

   - **Networking type**: `Public`
   - **DNS name label**: `automl-app-` + random numbers
   - **Ports**: `8501` (TCP)

5. **Advanced tab**:

   - **Environment variables**:
     ```
     STREAMLIT_SERVER_PORT = 8501
     STREAMLIT_SERVER_ADDRESS = 0.0.0.0
     STREAMLIT_SERVER_HEADLESS = true
     STREAMLIT_BROWSER_GATHER_USAGE_STATS = false
     ```
   - **Command override**: Leave empty

6. Click **"Review + Create"** → **"Create"**

### Step 5: Access Your Application

1. Go to your **Container Instance** resource
2. Copy the **FQDN** (something like `automl-app-123.eastus.azurecontainer.io`)
3. Open browser and go to: `http://[YOUR-FQDN]:8501`

---

## 🚀 Method 2: Azure App Service (Alternative)

### Step 1: Create App Service Plan

1. Search **"App Service plans"** in Azure Portal
2. Click **"+ Create"**
3. Fill in:
   - **Resource group**: `automl-rg`
   - **Name**: `automl-plan`
   - **Operating System**: `Linux`
   - **Region**: `East US`
   - **Pricing tier**: `B1 Basic` ($13/month)
4. Click **"Review + Create"** → **"Create"**

### Step 2: Create Web App

1. Search **"App Services"** in Azure Portal
2. Click **"+ Create"**
3. Fill in:
   - **Resource group**: `automl-rg`
   - **Name**: `automl-webapp-` + random numbers
   - **Publish**: `Container`
   - **Operating System**: `Linux`
   - **Region**: `East US`
   - **App Service Plan**: Select your plan
4. **Docker tab**:
   - **Options**: `Single Container`
   - **Image Source**: `Azure Container Registry`
   - **Registry**: Your registry
   - **Image**: `automl-app`
   - **Tag**: `latest`
5. Click **"Review + Create"** → **"Create"**

### Step 3: Configure App Settings

1. Go to your **App Service** resource
2. Click **"Configuration"** in the left menu
3. Add **Application Settings**:
   ```
   WEBSITES_PORT = 8501
   STREAMLIT_SERVER_PORT = 8501
   STREAMLIT_SERVER_ADDRESS = 0.0.0.0
   STREAMLIT_SERVER_HEADLESS = true
   ```
4. Click **"Save"**

---

## 🔧 If You Don't Have Docker Image Yet

### Option A: Use GitHub and Azure Build

1. **Push your project to GitHub**
2. In **Container Registry**, use **Tasks** → **Quick run**
3. Use your GitHub repository URL as source

### Option B: Use Pre-built Image (Quick Test)

1. For quick testing, you can use: `python:3.9-slim`
2. But you'll need to customize it later with your app

### Option C: Local Upload (If You Have Docker Working)

1. Build locally: `docker build -t automl-app .`
2. Tag for ACR: `docker tag automl-app [registry].azurecr.io/automl-app:latest`
3. Push: `docker push [registry].azurecr.io/automl-app:latest`

---

## 💰 Cost Estimation

### Container Instances

- **2 CPU, 4GB RAM**: ~$15-30/month
- **Container Registry**: ~$5/month
- **Total**: ~$20-35/month

### App Service

- **B1 Basic Plan**: ~$13/month
- **Container Registry**: ~$5/month
- **Total**: ~$18/month

---

## 🛠️ Management Through Portal

### View Logs

1. Go to your **Container Instance** or **App Service**
2. Click **"Logs"** in the left menu
3. View real-time logs

### Restart Application

1. Go to your resource
2. Click **"Restart"** button

### Monitor Performance

1. Go to your resource
2. Click **"Metrics"** for CPU, Memory usage
3. Set up **Alerts** for monitoring

### Update Application

1. Rebuild image in **Container Registry**
2. Restart your **Container Instance** or **App Service**

---

## 🎯 Recommended Path for You

**Since you can't use shell commands:**

1. ✅ **Create Resource Group** (5 minutes)
2. ✅ **Create Container Registry** (5 minutes)
3. ✅ **Upload your project to GitHub** (if not already)
4. ✅ **Use Container Registry Quick Run** to build image (10 minutes)
5. ✅ **Create Container Instance** using your image (5 minutes)
6. ✅ **Access your app** at the provided URL

**Total time**: ~25-30 minutes
**No command line needed** - everything through Azure Portal interface!
