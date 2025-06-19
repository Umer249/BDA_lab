# 🤖 AutoML Web Application

A comprehensive full-stack AutoML web application built with Streamlit that allows users to upload datasets, preprocess data, train multiple machine learning models, and deploy them for predictions.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Docker Deployment](#docker-deployment)
- [Azure Cloud Deployment](#azure-cloud-deployment)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🎯 Core Functionality

- **Data Upload & Analysis**: Support for CSV files with comprehensive data profiling
- **Data Preprocessing**: Handle missing values, encode categoricals, scale features, and feature selection
- **AutoML Training**: Automated machine learning using PyCaret with 15+ algorithms
- **Model Comparison**: Interactive comparison of model performance with visualizations
- **Model Management**: Save, load, and manage trained models with metadata tracking
- **Prediction Service**: Single and batch predictions with confidence scores
- **Report Generation**: PDF reports with project documentation and results

### 🛠️ Technical Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Docker Support**: Containerized deployment with Docker and Docker Compose
- **Cloud Ready**: Azure deployment scripts and configurations
- **Monitoring**: Health checks and application insights integration
- **Persistent Storage**: Model and report persistence with Azure Storage support
- **Responsive UI**: Modern Streamlit interface with custom CSS styling

## 🏗️ Architecture

```
automl-web-app/
├── src/                          # Core application modules
│   ├── __init__.py
│   ├── data_preprocessing.py     # Data preprocessing pipeline
│   ├── automl_engine.py         # AutoML training engine
│   ├── model_manager.py         # Model persistence and management
│   └── report_generator.py      # PDF report generation
├── deployment/                   # Deployment configurations
│   └── azure/                   # Azure-specific deployment files
│       ├── deploy.sh            # Azure deployment script
│       ├── azure-container-app.yml
│       └── bicep/
│           └── main.bicep       # Infrastructure as Code
├── models/                      # Saved models directory
├── reports/                     # Generated reports directory
├── data/                        # Sample data directory
├── app.py                       # Main Streamlit application
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose setup
└── README.md                    # This file
```

## 🚀 Quick Start

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd automl-web-app
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**

   ```bash
   streamlit run app.py
   ```

4. **Open in browser**
   Navigate to `http://localhost:8501`

### Docker Quick Start

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t automl-app .
docker run -p 8501:8501 automl-app
```

## 💻 Installation

### Prerequisites

- Python 3.9 or higher
- Docker (for containerized deployment)
- Azure CLI (for cloud deployment)

### Local Installation

1. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env file with your configurations
   ```

4. **Create required directories**
   ```bash
   mkdir -p models reports data logs
   ```

## 📖 Usage Guide

### 1. Data Upload & Analysis

- Upload CSV files using the file uploader
- View data preview and statistics
- Analyze missing values and data types
- Use the sample dataset for testing

### 2. Data Preprocessing

- Select target column and task type (classification/regression)
- Configure preprocessing options:
  - Missing value strategies (mean, median, mode, KNN)
  - Categorical encoding (label encoding, one-hot encoding)
  - Feature scaling (standard, min-max)
  - Feature selection (optional)
- Set train-test split ratio

### 3. AutoML Training

- Choose specific models or train all available algorithms
- Configure number of top models to keep
- Monitor training progress
- View model comparison results with interactive plots

### 4. Model Comparison & Selection

- Compare model performance metrics
- Evaluate individual models with detailed analysis
- Save best performing models with custom names

### 5. Making Predictions

- Select saved models from the model manager
- Single prediction: Enter feature values manually
- Batch prediction: Upload CSV file for multiple predictions
- Download prediction results

### 6. Model Management

- View all saved models with performance metrics
- Delete unwanted models
- Export model summaries
- Monitor storage usage

### 7. Report Generation

- Generate comprehensive PDF reports
- Include project information and model results
- Create deployment guides
- Download reports for documentation

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Manual Docker Commands

```bash
# Build image
docker build -t automl-app .

# Run container
docker run -d \
  --name automl-container \
  -p 8501:8501 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/reports:/app/reports \
  automl-app

# View logs
docker logs automl-container
```

## ☁️ Azure Cloud Deployment

### Prerequisites

- Azure CLI installed and configured
- Docker installed
- Azure subscription

### Automated Deployment

```bash
# Make the deployment script executable
chmod +x deployment/azure/deploy.sh

# Run the deployment script
./deployment/azure/deploy.sh
```

### Manual Azure Deployment

1. **Create Resource Group**

   ```bash
   az group create --name automl-rg --location eastus
   ```

2. **Create Container Registry**

   ```bash
   az acr create --resource-group automl-rg --name automlregistry --sku Basic
   ```

3. **Build and Push Image**

   ```bash
   az acr build --registry automlregistry --image automl-app .
   ```

4. **Deploy to Container Instances**
   ```bash
   az container create \
     --resource-group automl-rg \
     --name automl-container \
     --image automlregistry.azurecr.io/automl-app:latest \
     --cpu 2 \
     --memory 4 \
     --ports 8501
   ```

### Infrastructure as Code

Deploy using Bicep templates:

```bash
az deployment group create \
  --resource-group automl-rg \
  --template-file deployment/azure/bicep/main.bicep
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env` file:

- `STREAMLIT_SERVER_PORT`: Application port (default: 8501)
- `MAX_MODEL_COUNT`: Maximum number of models to keep
- `DEFAULT_TASK_TYPE`: Default ML task type
- `AZURE_STORAGE_*`: Azure Storage configuration for persistence

### Application Settings

Modify `app.py` for:

- UI themes and styling
- Page layouts and navigation
- Feature enablement/disablement

## 🔍 API Reference

### Core Modules

#### DataPreprocessor

```python
preprocessor = DataPreprocessor()
X_train, X_test, y_train, y_test, features = preprocessor.preprocess_pipeline(
    df=data,
    target_column='target',
    task_type='classification'
)
```

#### AutoMLEngine

```python
automl = AutoMLEngine(task_type='classification')
automl.setup_automl(X_train, y_train, 'target')
models = automl.compare_models(n_select=5)
```

#### ModelManager

```python
manager = ModelManager()
model_id = manager.save_model(model, 'model_name', 'classification', metrics)
model, metadata = manager.load_model(model_id)
```

## 🧪 Testing

### Unit Tests

```bash
python -m pytest tests/
```

### Integration Tests

```bash
python -m pytest tests/integration/
```

### Load Testing

```bash
# Test application performance
streamlit run app.py --server.port 8501 &
# Run load tests with your preferred tool
```

## 📊 Monitoring & Logging

### Health Checks

- Application health: `http://localhost:8501/_stcore/health`
- Container health checks included in Docker configuration

### Logging

- Application logs: `logs/automl.log`
- Container logs: `docker logs automl-container`

### Azure Monitoring

- Application Insights integration
- Log Analytics workspace
- Container monitoring

## 🔒 Security Considerations

### Production Deployment

- Use HTTPS with proper SSL certificates
- Implement authentication and authorization
- Secure sensitive environment variables
- Regular security updates

### Data Privacy

- Implement data retention policies
- Secure data storage and transmission
- Comply with relevant data protection regulations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation
- Use meaningful commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues

1. **Module Import Errors**: Ensure all dependencies are installed
2. **Docker Build Failures**: Check Docker daemon is running
3. **Azure Deployment Issues**: Verify Azure CLI authentication
4. **Memory Issues**: Increase container memory limits

### Getting Help

- Check the [Issues](../../issues) page for known problems
- Create a new issue for bugs or feature requests
- Review the documentation for detailed guides

## 🚧 Roadmap

### Upcoming Features

- [ ] Support for additional file formats (Excel, JSON)
- [ ] Integration with more AutoML frameworks (H2O, FLAML)
- [ ] Real-time model monitoring
- [ ] A/B testing framework
- [ ] REST API endpoints
- [ ] Multi-user support with authentication
- [ ] Advanced feature engineering
- [ ] Ensemble model support

### Version History

- **v1.0.0**: Initial release with core AutoML functionality
- **v1.1.0**: Added Azure deployment support
- **v1.2.0**: Enhanced model management and reporting

---

🎉 **Happy Machine Learning!** 🎉
