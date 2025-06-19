# 🚀 One-Click Deploy to Azure

## Deploy Your AutoML App to Azure with One Click!

### ✨ Instant Deployment (No Shell, No Docker Desktop Required!)

Click the button below to deploy your AutoML application to Azure instantly:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fyourusername%2Fyourrepo%2Fmain%2Fazuredeploy.json)

### What This Button Does:

1. ✅ Creates Azure Resource Group
2. ✅ Creates Azure Container Registry
3. ✅ Creates Azure Container Instance
4. ✅ Configures all networking and environment variables
5. ✅ Provides you with a public URL

### After Clicking "Deploy to Azure":

1. **Sign in** to your Azure account
2. **Fill in parameters** (or use defaults):
   - **Subscription**: Choose your subscription
   - **Resource Group**: Create new `automl-rg`
   - **Region**: `East US` (or your preferred region)
   - **Container Registry Name**: Leave default (auto-generated)
   - **DNS Name Label**: Leave default (auto-generated)
   - **CPU Cores**: `2` (recommended)
   - **Memory**: `4 GB` (recommended)
3. **Click "Review + Create"**
4. **Click "Create"**
5. **Wait 5-10 minutes** for deployment to complete

### After Deployment Completes:

1. Go to **Outputs** tab in the deployment
2. Copy the **Application URL**
3. **BUT FIRST**: You need to build your Docker image!

---

## 🐳 Build Your Docker Image (Required Step)

Since the ARM template creates the infrastructure, you still need to build your Docker image:

### Option 1: Use Azure Portal (Recommended)

1. Go to your **Container Registry** resource
2. Click **"Tasks"** → **"Quick run"**
3. **Source**: Upload your project files OR use GitHub repo
4. **Dockerfile**: `Dockerfile`
5. **Image**: `automl-app:latest`
6. Click **"Run"**

### Option 2: GitHub Integration

1. **Push your project to GitHub**
2. In Container Registry → **Tasks** → **Quick run**
3. **Source location**: GitHub
4. **Repository URL**: Your GitHub repo URL
5. **Branch**: `main` or `master`
6. **Dockerfile**: `Dockerfile`
7. **Image**: `automl-app:latest`
8. Click **"Run"**

### Option 3: Manual Upload

1. Create a ZIP file with:
   - `Dockerfile`
   - `requirements.txt`
   - `app.py`
   - `src/` folder
   - `data/` folder (if needed)
2. In Container Registry → **Tasks** → **Quick run**
3. **Source**: Upload local context
4. Upload your ZIP file
5. Click **"Run"**

---

## 📋 Manual Alternative (If Button Doesn't Work)

### Step 1: Create Resources Manually

1. **Resource Group**:

   - Name: `automl-rg`
   - Region: `East US`

2. **Container Registry**:

   - Name: `automlregistry` + random numbers
   - SKU: `Basic`
   - Admin user: `Enabled`

3. **Container Instance**:
   - Name: `automl-container`
   - Image: `[registry].azurecr.io/automl-app:latest`
   - CPU: `2 cores`
   - Memory: `4 GB`
   - Port: `8501`
   - Environment variables:
     ```
     STREAMLIT_SERVER_PORT=8501
     STREAMLIT_SERVER_ADDRESS=0.0.0.0
     STREAMLIT_SERVER_HEADLESS=true
     STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
     ```

---

## 💰 Cost Breakdown

- **Container Registry**: ~$5/month
- **Container Instance (2 CPU, 4GB)**: ~$15-30/month
- **Total**: ~$20-35/month

## 🎯 Expected Timeline

- **Infrastructure deployment**: 5-10 minutes
- **Docker image build**: 5-10 minutes
- **Total**: 10-20 minutes to live application

## 🌐 Final Result

You'll get a URL like:

```
http://automl-app-abc123.eastus.azurecontainer.io:8501
```

**No Docker Desktop issues, no command line required!** 🎉
