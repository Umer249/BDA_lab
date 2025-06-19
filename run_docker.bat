@echo off
echo Building AutoML Docker Image...
docker build -t automl-app .

echo.
echo Checking if container exists...
docker stop automl-streamlit-app 2>nul
docker rm automl-streamlit-app 2>nul

echo.
echo Starting AutoML Container...
docker run -d ^
  --name automl-streamlit-app ^
  -p 8501:8501 ^
  -v %cd%\models:/app/models ^
  -v %cd%\reports:/app/reports ^
  -v %cd%\data:/app/data ^
  automl-app

echo.
echo Container started! Access your app at: http://localhost:8501
echo.
echo To check container status: docker ps
echo To view logs: docker logs automl-streamlit-app
echo To stop container: docker stop automl-streamlit-app
pause 