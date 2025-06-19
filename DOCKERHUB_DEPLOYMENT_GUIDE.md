# 🐳 Docker Hub + Azure Deployment Guide

## Deploy AutoML App using Docker Hub (umeri249/automl-app)

This approach pushes your Docker image to Docker Hub and then deploys it to Azure Container Instances.

### 📋 Prerequisites

- Docker Hub account (username: `umeri249`)
- Azure account
- Docker Desktop running locally

---

## 🚀 Method 1: Automated Push to Docker Hub

### Step 1: Ensure Docker Desktop is Running

1. **Start Docker Desktop** manually (right-click → Run as administrator if needed)
2. **Wait for the whale icon** to appear in system tray showing "running"
3. **Verify Docker works**:

### Step 2: Push to Docker Hub (Automated)

```bash
# Run the automated script
.\push_to_dockerhub.bat
```

This script will:

1. ✅ Build your Docker image as `umeri249/automl-app:latest`
2. ✅ Login to Docker Hub (you'll need to enter your password)
3. ✅ Push the image to Docker Hub
4. ✅ Make it publicly available at `docker.io/umeri249/automl-app:latest`

### Step 3: Deploy to Azure using Docker Hub Image

#### Option A: One-Click Deploy Button

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fyourusername%2Fyourrepo%2Fmain%2Fazuredeploy-dockerhub.json)

#### Option B: Manual Azure Portal Steps

1. **Go to Azure Portal**: https://portal.azure.com
2. **Create Resource Group**: `automl-rg`
3. **Create Container Instance**:
   - **Image**: `umeri249/automl-app:latest`
   - **Image source**: `Docker Hub or other registry`
   - **CPU**: 2 cores
   - **Memory**: 4 GB
   - **Port**: 8501
   - **DNS label**: `automl-app-` + random numbers

---

## 🔧 Method 2: Manual Docker Commands

If the automated script doesn't work, run these commands manually:

### Step 1: Build the Image

```bash
docker build -t umeri249/automl-app:latest .
```

### Step 2: Login to Docker Hub

```bash
docker login --username umeri249
# Enter your Docker Hub password when prompted
```

### Step 3: Push to Docker Hub

```bash
docker push umeri249/automl-app:latest
```

### Step 4: Verify Upload

1. Go to **Docker Hub**: https://hub.docker.com/
2. Login with your credentials
3. Check that `umeri249/automl-app` repository exists
4. Verify the `latest` tag is present

---

## 🌊 Method 3: Alternative - GitHub Actions (If Local Docker Fails)

If Docker Desktop issues persist, create a GitHub Actions workflow:

### Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Add AutoML app for Docker Hub deployment"
git push origin main
```

### Step 2: Create GitHub Actions Workflow

Create `.github/workflows/docker-publish.yml`:

```yaml
name: Build and Push to Docker Hub

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: umeri249
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: umeri249/automl-app:latest
```

### Step 3: Add Docker Hub Token

1. Go to **Docker Hub** → **Account Settings** → **Security**
2. **Create Access Token**
3. In **GitHub** → **Settings** → **Secrets** → **Add** `DOCKERHUB_TOKEN`

---

## 🌐 Deploy to Azure Container Instances

### Using Azure Portal

1. **Search**: "Container instances"
2. **Create**:
   - **Resource group**: `automl-rg`
   - **Container name**: `automl-container`
   - **Image source**: `Docker Hub or other registry`
   - **Image**: `umeri249/automl-app:latest`
   - **Size**: 2 CPU, 4 GB RAM
   - **Networking**: Public, Port 8501
   - **DNS label**: `automl-app-12345`

### Environment Variables (Advanced tab)

```
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

---

## ✅ Expected Results

### After Successful Push to Docker Hub:

- **Image available at**: `docker.io/umeri249/automl-app:latest`
- **Public repository**: Anyone can pull this image
- **Size**: ~1-2 GB (estimated)

### After Azure Deployment:

- **Application URL**: `http://automl-app-12345.eastus.azurecontainer.io:8501`
- **Cost**: ~$15-30/month
- **Availability**: 99.9% uptime

---

## 🛠️ Troubleshooting

### Docker Build Fails

```bash
# Check Docker is running
docker version

# Check Dockerfile syntax
docker build --no-cache -t test-build .
```

### Docker Push Fails

```bash
# Re-login to Docker Hub
docker logout
docker login --username umeri249

# Check image exists locally
docker images | grep umeri249
```

### Azure Container Fails to Start

1. **Check logs** in Azure Portal → Container Instance → Logs
2. **Verify image** exists on Docker Hub
3. **Check environment variables** are set correctly
4. **Verify port** 8501 is exposed

---

## 💰 Cost Comparison

| Method                           | Monthly Cost | Setup Time | Complexity |
| -------------------------------- | ------------ | ---------- | ---------- |
| Docker Hub + Container Instances | $15-30       | 15 min     | Easy       |
| Azure Container Registry + ACI   | $20-35       | 25 min     | Medium     |
| Azure App Service                | $18-25       | 20 min     | Medium     |

**Recommended**: Docker Hub approach for simplicity and cost-effectiveness!

---

## 🎯 Next Steps After Deployment

1. ✅ **Test your application** at the Azure URL
2. ✅ **Update Docker image** when you make changes:
   ```bash
   docker build -t umeri249/automl-app:latest .
   docker push umeri249/automl-app:latest
   # Restart Azure Container Instance
   ```
3. ✅ **Set up monitoring** in Azure Portal
4. ✅ **Configure custom domain** (optional)
5. ✅ **Set up CI/CD** with GitHub Actions (optional)
