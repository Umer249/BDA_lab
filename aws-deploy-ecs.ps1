# AWS ECS Deployment Script for AutoML App
# This script deploys the Docker image to AWS ECS Fargate

param(
    [string]$ClusterName = "automl-cluster",
    [string]$ServiceName = "automl-service",
    [string]$TaskDefinitionName = "automl-task",
    [string]$DockerImage = "umeri249/automl-app:latest",
    [string]$Region = "us-east-1"
)

Write-Host "🚀 Starting AWS ECS Deployment..." -ForegroundColor Green
Write-Host "Cluster Name: $ClusterName" -ForegroundColor Yellow
Write-Host "Service Name: $ServiceName" -ForegroundColor Yellow
Write-Host "Docker Image: $DockerImage" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow

# Check if AWS CLI is installed
try {
    $awsVersion = aws --version
    Write-Host "✅ AWS CLI: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install it from: https://aws.amazon.com/cli/" -ForegroundColor Red
    exit 1
}

# Check if logged in to AWS
try {
    $identity = aws sts get-caller-identity --output json | ConvertFrom-Json
    Write-Host "✅ Logged in as: $($identity.Arn)" -ForegroundColor Green
} catch {
    Write-Host "🔐 Please configure AWS credentials..." -ForegroundColor Yellow
    aws configure
}

# Set AWS region
$env:AWS_DEFAULT_REGION = $Region

# Create ECS Cluster
Write-Host "📦 Creating ECS Cluster..." -ForegroundColor Blue
aws ecs create-cluster --cluster-name $ClusterName

# Create Task Definition
Write-Host "📋 Creating Task Definition..." -ForegroundColor Blue
$taskDefinition = @{
    family = $TaskDefinitionName
    networkMode = "awsvpc"
    requiresCompatibilities = @("FARGATE")
    cpu = "1024"
    memory = "2048"
    executionRoleArn = "ecsTaskExecutionRole"
    containerDefinitions = @(
        @{
            name = "automl-app"
            image = $DockerImage
            portMappings = @(
                @{
                    containerPort = 8501
                    protocol = "tcp"
                }
            )
            environment = @(
                @{
                    name = "STREAMLIT_SERVER_PORT"
                    value = "8501"
                },
                @{
                    name = "STREAMLIT_SERVER_ADDRESS"
                    value = "0.0.0.0"
                },
                @{
                    name = "STREAMLIT_SERVER_HEADLESS"
                    value = "true"
                },
                @{
                    name = "STREAMLIT_BROWSER_GATHER_USAGE_STATS"
                    value = "false"
                }
            )
            logConfiguration = @{
                logDriver = "awslogs"
                options = @{
                    "awslogs-group" = "/ecs/$TaskDefinitionName"
                    "awslogs-region" = $Region
                    "awslogs-stream-prefix" = "ecs"
                }
            }
        }
    )
}

$taskDefinition | ConvertTo-Json -Depth 10 | Out-File -FilePath "task-definition.json" -Encoding UTF8

# Create CloudWatch Log Group
Write-Host "📝 Creating CloudWatch Log Group..." -ForegroundColor Blue
aws logs create-log-group --log-group-name "/ecs/$TaskDefinitionName" --region $Region

# Register Task Definition
Write-Host "📝 Registering Task Definition..." -ForegroundColor Blue
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create Security Group
Write-Host "🔒 Creating Security Group..." -ForegroundColor Blue
$vpcId = aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query "Vpcs[0].VpcId" --output text
$securityGroupId = aws ec2 create-security-group --group-name "automl-sg" --description "Security group for AutoML app" --vpc-id $vpcId --query "GroupId" --output text

# Add inbound rule for port 8501
aws ec2 authorize-security-group-ingress --group-id $securityGroupId --protocol tcp --port 8501 --cidr 0.0.0.0/0

# Get default subnets
$subnets = aws ec2 describe-subnets --filters "Name=vpc-id,Values=$vpcId" --query "Subnets[0:2].SubnetId" --output text

# Create ECS Service
Write-Host "🚀 Creating ECS Service..." -ForegroundColor Blue
aws ecs create-service `
    --cluster $ClusterName `
    --service-name $ServiceName `
    --task-definition $TaskDefinitionName `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$subnets],securityGroups=[$securityGroupId],assignPublicIp=ENABLED}"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ ECS Deployment successful!" -ForegroundColor Green
    
    # Get service details
    $service = aws ecs describe-services --cluster $ClusterName --services $ServiceName --output json | ConvertFrom-Json
    
    Write-Host "📊 Service Status:" -ForegroundColor Yellow
    Write-Host "   Status: $($service.services[0].status)" -ForegroundColor White
    Write-Host "   Desired Count: $($service.services[0].desiredCount)" -ForegroundColor White
    Write-Host "   Running Count: $($service.services[0].runningCount)" -ForegroundColor White
    
    Write-Host "`n🔧 Useful Commands:" -ForegroundColor Yellow
    Write-Host "   View service: aws ecs describe-services --cluster $ClusterName --services $ServiceName" -ForegroundColor White
    Write-Host "   View tasks: aws ecs list-tasks --cluster $ClusterName --service-name $ServiceName" -ForegroundColor White
    Write-Host "   Stop service: aws ecs update-service --cluster $ClusterName --service $ServiceName --desired-count 0" -ForegroundColor White
    Write-Host "   Delete service: aws ecs delete-service --cluster $ClusterName --service $ServiceName --force" -ForegroundColor White
    
    # Save deployment info
    $deploymentInfo = @{
        ClusterName = $ClusterName
        ServiceName = $ServiceName
        TaskDefinitionName = $TaskDefinitionName
        DockerImage = $DockerImage
        Region = $Region
        SecurityGroupId = $securityGroupId
        DeploymentTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    
    $deploymentInfo | ConvertTo-Json | Out-File -FilePath "aws-deployment-info.json" -Encoding UTF8
    Write-Host "💾 Deployment info saved to: aws-deployment-info.json" -ForegroundColor Green
    
} else {
    Write-Host "❌ ECS Deployment failed!" -ForegroundColor Red
    Write-Host "Check the error messages above and try again." -ForegroundColor Red
} 