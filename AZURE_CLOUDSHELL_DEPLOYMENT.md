# 🌊 Azure Cloud Shell Deployment Guide

## Why Use Azure Cloud Shell?

- ✅ No local Docker installation required
- ✅ Azure CLI pre-installed
- ✅ Docker pre-installed
- ✅ Free to use (no additional charges)
- ✅ Bypasses all local Docker Desktop issues

## 🚀 Step-by-Step Deployment

### Step 1: Access Azure Cloud Shell

1. Go to **Azure Portal**: https://portal.azure.com
2. Click the **Cloud Shell icon** `>_` in the top navigation bar
3. Choose **Bash** when prompted
4. Wait for Cloud Shell to initialize

### Step 2: Upload Your Project Files

#### Option A: Upload via Cloud Shell Interface

1. In Cloud Shell, click the **Upload/Download** icon (folder icon)
2. Select **Upload**
3. Choose these key files from your project:
   - `Dockerfile`
   - `requirements.txt`
   - `app.py`
   - `azure_cloudshell_deploy.sh`
   - Any files in `src/` directory
   - Any files in `data/` directory (if needed)

#### Option B: Use Git (Recommended)

```bash
# Clone your repository (if it's on GitHub)
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo

# OR upload a zip file and extract
# Upload your project as a zip file, then:
unzip your-project.zip
cd your-project-folder
```

### Step 3: Run the Deployment Script

```bash
# Make the script executable
chmod +x azure_cloudshell_deploy.sh

# Run the deployment
./azure_cloudshell_deploy.sh
```

### Step 4: Monitor Deployment

The script will:

1. ✅ Create Azure Resource Group
2. ✅ Create Azure Container Registry
3. ✅ Build Docker image in Azure (no local Docker needed!)
4. ✅ Deploy to Azure Container Instances
5. ✅ Provide you with the application URL

### Step 5: Access Your Application

After deployment completes, you'll get a URL like:

```
http://automl-web-app-123456.eastus.azurecontainer.io:8501
```

## 💰 Cost Estimation

- **Container Registry**: ~$5/month
- **Container Instance (2 CPU, 4GB)**: ~$15-30/month
- **Total**: ~$20-35/month

## 🛠️ Management Commands

### View Application Logs

```bash
az container logs --resource-group automl-rg --name automl-container --follow
```

### Restart Container

```bash
az container restart --resource-group automl-rg --name automl-container
```

### Update Application

```bash
# Rebuild and redeploy
az acr build --registry automlregistry --image automl-app:latest .
az container restart --resource-group automl-rg --name automl-container
```

### Clean Up Resources

```bash
# Delete everything (stops all charges)
az group delete --name automl-rg --yes --no-wait
```

## 🔧 Troubleshooting

### If Upload Fails

- Try uploading files one by one
- Ensure file sizes are reasonable (<100MB each)
- Use Git clone if you have the project in a repository

### If Build Fails

- Check Dockerfile syntax
- Ensure all required files are present
- Review error messages in Cloud Shell

### If Container Doesn't Start

- Check logs: `az container logs --resource-group automl-rg --name automl-container`
- Verify environment variables
- Check port configuration

## 🌟 Advantages of This Approach

1. **No Local Dependencies**: Bypasses Docker Desktop issues
2. **Scalable**: Can easily scale up/down resources
3. **Reliable**: Azure infrastructure handles availability
4. **Cost-Effective**: Only pay for what you use
5. **Professional**: Publicly accessible URL for sharing

## 🎯 Next Steps After Deployment

1. Test your application at the provided URL
2. Set up custom domain (optional)
3. Configure SSL certificate (optional)
4. Set up monitoring and alerts
5. Configure auto-scaling (if needed)
