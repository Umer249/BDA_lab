# 🚀 AWS Deployment Guide for AutoML App

## 🎯 **Deployment Options Comparison**

| Service         | Cost/Month | Setup Time | Difficulty | Scalability |
| --------------- | ---------- | ---------- | ---------- | ----------- |
| **ECS Fargate** | $15-25     | 10-15 min  | Medium     | Excellent   |
| **App Runner**  | $20-30     | 5-10 min   | Easy       | Good        |
| **EC2**         | $10-20     | 15-20 min  | Hard       | Excellent   |
| **Lambda**      | $5-15      | 20-30 min  | Hard       | Excellent   |

**Recommended**: **ECS Fargate** for best balance of cost, ease, and scalability!

---

## 🎯 **Option 1: AWS ECS Fargate (Recommended)**

### Prerequisites

1. **AWS Account** with active subscription
2. **AWS CLI** installed: https://aws.amazon.com/cli/
3. **Docker Image** ready: `umeri249/automl-app:latest`

### Step 1: Install AWS CLI

```powershell
# Download and install AWS CLI
winget install Amazon.AWSCLI
# OR download from: https://aws.amazon.com/cli/
```

### Step 2: Configure AWS

```powershell
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
```

### Step 3: Run Deployment Script

```powershell
.\aws-deploy-ecs.ps1
```

### Expected Results

- **Application URL**: Available through AWS Console
- **Cost**: ~$15-25/month
- **Setup Time**: 10-15 minutes

---

## 🎯 **Option 2: AWS App Runner (Easiest)**

### Step 1: Go to AWS App Runner Console

1. Visit: https://console.aws.amazon.com/apprunner/
2. Click "Create service"

### Step 2: Configure Service

- **Source**: Container registry
- **Provider**: Docker Hub
- **Image URI**: `umeri249/automl-app:latest`
- **Port**: 8501
- **CPU**: 1 vCPU
- **Memory**: 2 GB

### Step 3: Environment Variables

```
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Expected Results

- **Application URL**: Provided by App Runner
- **Cost**: ~$20-30/month
- **Setup Time**: 5-10 minutes

---

## 🎯 **Option 3: AWS EC2 (Most Control)**

### Step 1: Launch EC2 Instance

1. Go to EC2 Console: https://console.aws.amazon.com/ec2/
2. Click "Launch Instance"
3. Choose **Amazon Linux 2** AMI
4. Select **t3.small** (2 vCPU, 2 GB RAM)
5. Configure Security Group to allow port 8501

### Step 2: Install Docker

```bash
# Connect to your EC2 instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user
```

### Step 3: Run Container

```bash
# Pull and run your image
docker pull umeri249/automl-app:latest
docker run -d -p 8501:8501 \
  -e STREAMLIT_SERVER_PORT=8501 \
  -e STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
  -e STREAMLIT_SERVER_HEADLESS=true \
  -e STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
  umeri249/automl-app:latest
```

### Expected Results

- **Application URL**: `http://your-ec2-ip:8501`
- **Cost**: ~$10-20/month
- **Setup Time**: 15-20 minutes

---

## 🎯 **Option 4: AWS Lambda + API Gateway**

### Step 1: Create Lambda Function

1. Go to Lambda Console: https://console.aws.amazon.com/lambda/
2. Click "Create function"
3. Choose "Container image"
4. Upload your Docker image

### Step 2: Configure API Gateway

1. Create REST API
2. Create resource and method
3. Integrate with Lambda function

### Expected Results

- **Application URL**: API Gateway endpoint
- **Cost**: ~$5-15/month (pay per request)
- **Setup Time**: 20-30 minutes

---

## 📊 **Cost Comparison**

| Service         | Monthly Cost | Setup Time | Best For         |
| --------------- | ------------ | ---------- | ---------------- |
| **ECS Fargate** | $15-25       | 10-15 min  | Production apps  |
| **App Runner**  | $20-30       | 5-10 min   | Quick deployment |
| **EC2**         | $10-20       | 15-20 min  | Full control     |
| **Lambda**      | $5-15        | 20-30 min  | Serverless       |

---

## 🔧 **Management Commands**

### ECS Commands

```bash
# View service status
aws ecs describe-services --cluster automl-cluster --services automl-service

# Scale service
aws ecs update-service --cluster automl-cluster --service automl-service --desired-count 2

# Stop service
aws ecs update-service --cluster automl-cluster --service automl-service --desired-count 0

# Delete service
aws ecs delete-service --cluster automl-cluster --service automl-service --force
```

### App Runner Commands

```bash
# View service
aws apprunner describe-service --service-arn your-service-arn

# Pause service
aws apprunner pause-service --service-arn your-service-arn

# Resume service
aws apprunner resume-service --service-arn your-service-arn
```

---

## 🛠️ **Troubleshooting**

### ECS Issues

1. **Check task logs**: AWS Console → ECS → Tasks → Logs
2. **Verify security groups**: Allow port 8501
3. **Check task definition**: Ensure environment variables are set

### App Runner Issues

1. **Check service logs**: App Runner Console → Logs
2. **Verify image**: Ensure Docker image is public
3. **Check environment variables**: Ensure all required vars are set

### EC2 Issues

1. **Check security group**: Allow inbound traffic on port 8501
2. **Check Docker logs**: `docker logs container-id`
3. **Verify container is running**: `docker ps`

---

## 💰 **Cost Optimization**

### ECS Fargate

- **Stop service** when not in use (saves ~70% cost)
- **Use Spot instances** for development (saves ~60% cost)
- **Right-size resources** (1 vCPU, 2 GB RAM for dev)

### App Runner

- **Pause service** when not in use
- **Use smaller instance size** for development

### EC2

- **Stop instance** when not in use
- **Use Spot instances** for development
- **Use t3.small** instead of larger instances

---

## 🎉 **Success!**

Once deployed, your AutoML application will be:

- ✅ **Publicly accessible**
- ✅ **Scalable**
- ✅ **Cost-effective**
- ✅ **Easy to manage**

**Next Steps:**

1. Test your application
2. Set up monitoring and alerts
3. Configure auto-scaling (if needed)
4. Set up CI/CD pipeline

---

## 🔄 **Updating Your Application**

### Method 1: Update Docker Image

```bash
# Build new image
docker build -t umeri249/automl-app:latest .

# Push to Docker Hub
docker push umeri249/automl-app:latest

# Update ECS service
aws ecs update-service --cluster automl-cluster --service automl-service --force-new-deployment
```

### Method 2: GitHub Actions

The existing GitHub Actions workflow will automatically:

1. Build new Docker image
2. Push to Docker Hub
3. You can then update your AWS service

---

## 🏆 **Recommendation**

**For your use case, I recommend ECS Fargate** because:

- ✅ **Cost-effective** ($15-25/month)
- ✅ **Easy to manage** (no server management)
- ✅ **Highly scalable** (auto-scaling available)
- ✅ **Production-ready** (99.9% uptime SLA)
- ✅ **Good documentation** and community support

Would you like me to help you set up the ECS Fargate deployment?
