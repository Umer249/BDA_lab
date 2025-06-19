@echo off
echo 🐳 Building and Pushing AutoML App to Docker Hub...
echo Username: umeri249

echo.
echo 1. Building Docker image...
docker build -t umeri249/automl-app:latest .

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker build failed! Make sure Docker Desktop is running.
    pause
    exit /b 1
)

echo.
echo 2. Logging into Docker Hub...
echo Please enter your Docker Hub password when prompted:
docker login --username umeri249

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker Hub login failed!
    pause
    exit /b 1
)

echo.
echo 3. Pushing image to Docker Hub...
docker push umeri249/automl-app:latest

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker push failed!
    pause
    exit /b 1
)

echo.
echo ✅ Successfully pushed to Docker Hub!
echo 🌐 Your image is now available at: docker.io/umeri249/automl-app:latest
echo.
echo 🚀 You can now use this image in Azure Container Instances:
echo    Image: umeri249/automl-app:latest
echo    Port: 8501
echo.
pause 