# Local Deployment Test Script for AutoML Web Application
# This script tests the Docker container locally before Azure deployment

param(
    [string]$ImageName = "automl-app",
    [int]$Port = 8501,
    [string]$ContainerName = "automl-test"
)

Write-Host "🧪 Testing AutoML Application Deployment Locally..." -ForegroundColor Green

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Stop and remove existing container if it exists
Write-Host "🧹 Cleaning up existing containers..." -ForegroundColor Cyan
docker stop $ContainerName 2>$null
docker rm $ContainerName 2>$null

# Build the Docker image
Write-Host "🐳 Building Docker image..." -ForegroundColor Cyan
docker build -t $ImageName .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker image built successfully" -ForegroundColor Green

# Run the container locally
Write-Host "🚀 Starting container locally..." -ForegroundColor Cyan
docker run -d `
    --name $ContainerName `
    -p ${Port}:8501 `
    -e STREAMLIT_SERVER_PORT=8501 `
    -e STREAMLIT_SERVER_ADDRESS=0.0.0.0 `
    -e STREAMLIT_SERVER_HEADLESS=true `
    -e STREAMLIT_BROWSER_GATHER_USAGE_STATS=false `
    $ImageName

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start container!" -ForegroundColor Red
    exit 1
}

# Wait for the application to start
Write-Host "⏳ Waiting for application to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Test if the application is responding
try {
    $response = Invoke-WebRequest -Uri "http://localhost:$Port" -TimeoutSec 30
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Application is responding!" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️ Application responded with status code: $($response.StatusCode)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Application is not responding. Checking logs..." -ForegroundColor Red
    docker logs $ContainerName
}

# Show container status
Write-Host ""
Write-Host "📊 Container Status:" -ForegroundColor Cyan
docker ps --filter "name=$ContainerName" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Show application URL
Write-Host ""
Write-Host "🌐 Application URL: http://localhost:$Port" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Test Commands:" -ForegroundColor Cyan
Write-Host "  View logs: docker logs $ContainerName" -ForegroundColor White
Write-Host "  Stop container: docker stop $ContainerName" -ForegroundColor White
Write-Host "  Remove container: docker rm $ContainerName" -ForegroundColor White
Write-Host ""

# Check resource usage
Write-Host "💻 Resource Usage:" -ForegroundColor Cyan
docker stats $ContainerName --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

Write-Host ""
Write-Host "🎉 Local testing complete!" -ForegroundColor Green
Write-Host "If everything looks good, you can now deploy to Azure using:" -ForegroundColor Yellow
Write-Host "  .\deployment\azure\deploy.ps1" -ForegroundColor White 