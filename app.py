import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# Add src to path - This is no longer needed with the updated Dockerfile
# sys.path.append('src')

from src.data_preprocessing import DataPreprocessor
from src.automl_engine import AutoMLEngine
from src.model_manager import ModelManager
from src.report_generator import ReportGenerator
from src.financial_data import FinancialDataFetcher

# Page config
st.set_page_config(
    page_title="AutoML Web Application",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.subheader {
    font-size: 1.5rem;
    color: #ff7f0e;
    margin-bottom: 1rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.stAlert > div {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'preprocessor' not in st.session_state:
    st.session_state.preprocessor = DataPreprocessor()
if 'automl_engine' not in st.session_state:
    st.session_state.automl_engine = None
if 'model_manager' not in st.session_state:
    st.session_state.model_manager = ModelManager()
if 'trained_models' not in st.session_state:
    st.session_state.trained_models = {}
if 'feature_columns' not in st.session_state:
    st.session_state.feature_columns = []
if 'financial_fetcher' not in st.session_state:
    st.session_state.financial_fetcher = FinancialDataFetcher()

def main():
    # Main header
    st.markdown('<h1 class="main-header">🤖 AutoML Web Application</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📊 Data Upload & Analysis", "💹 Financial Data", "⚙️ Data Preprocessing", "🚀 AutoML Training", 
         "📈 Model Comparison", "🔮 Make Predictions", "💾 Model Management", "📄 Generate Report"]
    )
    
    if page == "📊 Data Upload & Analysis":
        data_upload_page()
    elif page == "💹 Financial Data":
        financial_data_page()
    elif page == "⚙️ Data Preprocessing":
        preprocessing_page()
    elif page == "🚀 AutoML Training":
        automl_training_page()
    elif page == "📈 Model Comparison":
        model_comparison_page()
    elif page == "🔮 Make Predictions":
        prediction_page()
    elif page == "💾 Model Management":
        model_management_page()
    elif page == "📄 Generate Report":
        report_generation_page()

def financial_data_page():
    st.markdown('<h2 class="subheader">💹 Financial Data from Yahoo Finance</h2>', unsafe_allow_html=True)
    
    # Data source selection
    st.subheader("📈 Select Financial Data Source")
    
    data_source = st.radio(
        "Choose data source:",
        ["Single Stock", "Multiple Stocks", "Popular Stocks", "Market Indices", "Cryptocurrency"],
        help="Select the type of financial data you want to fetch"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Time period selection
        period = st.selectbox(
            "Data Period:",
            ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
            index=5,  # Default to 1y
            help="Select the time period for historical data"
        )
    
    with col2:
        # Interval selection
        interval = st.selectbox(
            "Data Interval:",
            ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"],
            index=8,  # Default to 1d
            help="Select the data interval"
        )
    
    # Symbol input based on data source
    symbols = []
    
    if data_source == "Single Stock":
        st.subheader("🔍 Enter Stock Symbol")
        symbol = st.text_input(
            "Stock Symbol:",
            value="AAPL",
            help="Enter a stock ticker symbol (e.g., AAPL, GOOGL, TSLA)"
        ).upper()
        if symbol:
            symbols = [symbol]
            
    elif data_source == "Multiple Stocks":
        st.subheader("📋 Enter Multiple Stock Symbols")
        symbols_input = st.text_area(
            "Stock Symbols (comma-separated):",
            value="AAPL, GOOGL, MSFT, AMZN",
            help="Enter multiple stock symbols separated by commas"
        )
        symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
        
    elif data_source == "Popular Stocks":
        st.subheader("🌟 Select from Popular Stocks")
        popular_stocks = st.session_state.financial_fetcher.get_popular_stocks()
        
        category = st.selectbox("Category:", list(popular_stocks.keys()))
        selected_symbols = st.multiselect(
            f"Select {category} stocks:",
            popular_stocks[category],
            default=popular_stocks[category][:3]
        )
        symbols = selected_symbols
        
    elif data_source == "Market Indices":
        st.subheader("📊 Market Indices")
        indices = {
            "S&P 500": "^GSPC",
            "Dow Jones": "^DJI", 
            "NASDAQ": "^IXIC",
            "Russell 2000": "^RUT",
            "VIX": "^VIX"
        }
        
        selected_indices = st.multiselect(
            "Select market indices:",
            list(indices.keys()),
            default=["S&P 500"]
        )
        symbols = [indices[idx] for idx in selected_indices]
        
    elif data_source == "Cryptocurrency":
        st.subheader("₿ Cryptocurrency")
        crypto_symbols = ["BTC-USD", "ETH-USD", "ADA-USD", "DOT-USD", "XRP-USD", "LTC-USD"]
        selected_crypto = st.multiselect(
            "Select cryptocurrencies:",
            crypto_symbols,
            default=["BTC-USD"]
        )
        symbols = selected_crypto
    
    # ML Configuration
    st.subheader("🤖 Machine Learning Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        task_type = st.selectbox(
            "ML Task Type:",
            ["classification", "regression"],
            help="Choose the type of machine learning task"
        )
    
    with col2:
        include_indicators = st.checkbox(
            "Include Technical Indicators",
            value=True,
            help="Add technical indicators like RSI, MACD, Bollinger Bands"
        )
    
    with col3:
        prediction_periods = st.slider(
            "Prediction Periods:",
            min_value=1,
            max_value=30,
            value=1,
            help="Number of periods ahead to predict"
        )
    
    # Target variable configuration
    if task_type == "classification":
        target_method = st.selectbox(
            "Classification Target:",
            ["price_direction", "price_movement", "volatility_breakout"],
            help="Method for creating classification target"
        )
    else:
        target_method = st.selectbox(
            "Regression Target:",
            ["next_close", "return", "volatility"],
            help="Method for creating regression target"
        )
    
    # Fetch data button
    if st.button("📥 Fetch Financial Data", type="primary"):
        if not symbols:
            st.error("Please select at least one symbol!")
            return
            
        try:
            with st.spinner("Fetching financial data..."):
                if len(symbols) == 1:
                    # Single symbol
                    data = st.session_state.financial_fetcher.fetch_stock_data(
                        symbols[0], period=period, interval=interval
                    )
                else:
                    # Multiple symbols - for now, let's fetch the first one for ML
                    # In a more advanced version, you could create a combined dataset
                    st.info(f"Fetching data for {symbols[0]} (first symbol) for ML processing...")
                    data = st.session_state.financial_fetcher.fetch_stock_data(
                        symbols[0], period=period, interval=interval
                    )
                
                if data is not None and not data.empty:
                    # Prepare data for ML
                    ml_data = st.session_state.financial_fetcher.prepare_ml_dataset(
                        data=data,
                        task_type=task_type,
                        target_method=target_method,
                        periods=prediction_periods,
                        include_technical_indicators=include_indicators
                    )
                    
                    if not ml_data.empty:
                        st.session_state.data = ml_data
                        st.success(f"✅ Financial data fetched successfully! Shape: {ml_data.shape}")
                        
                        # Display data info
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Rows", ml_data.shape[0])
                        with col2:
                            st.metric("Features", ml_data.shape[1] - 1)  # Excluding target
                        with col3:
                            st.metric("Task Type", task_type.title())
                        with col4:
                            if task_type == "classification":
                                unique_targets = ml_data['Target'].nunique()
                                st.metric("Classes", unique_targets)
                            else:
                                target_range = f"{ml_data['Target'].min():.2f} - {ml_data['Target'].max():.2f}"
                                st.metric("Target Range", target_range)
                        
                        # Show ticker info if available
                        if st.session_state.financial_fetcher.ticker_info:
                            info = st.session_state.financial_fetcher.ticker_info
                            st.subheader(f"📊 {symbols[0]} - {info.get('longName', 'Unknown Company')}")
                            
                            info_col1, info_col2, info_col3 = st.columns(3)
                            with info_col1:
                                st.metric("Sector", info.get('sector', 'Unknown'))
                            with info_col2:
                                market_cap = info.get('marketCap', 0)
                                if market_cap:
                                    market_cap_b = market_cap / 1e9
                                    st.metric("Market Cap", f"${market_cap_b:.1f}B")
                                else:
                                    st.metric("Market Cap", "N/A")
                            with info_col3:
                                st.metric("Industry", info.get('industry', 'Unknown'))
                        
                        # Data preview
                        st.subheader("📋 ML Dataset Preview")
                        
                        # Show original price data
                        st.write("**Original Price Data:**")
                        price_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
                        available_price_cols = [col for col in price_columns if col in data.columns]
                        if available_price_cols:
                            st.dataframe(data[available_price_cols].tail(10), use_container_width=True)
                        
                        # Show ML dataset
                        st.write("**Prepared ML Dataset:**")
                        st.dataframe(ml_data.tail(10), use_container_width=True)
                        
                        # Plot price chart
                        if 'Close' in data.columns:
                            st.subheader("📈 Price Chart")
                            
                            import plotly.graph_objects as go
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=data['Date'] if 'Date' in data.columns else range(len(data)),
                                y=data['Close'],
                                mode='lines',
                                name='Close Price',
                                line=dict(color='blue')
                            ))
                            
                            if include_indicators and 'SMA_20' in ml_data.columns:
                                fig.add_trace(go.Scatter(
                                    x=data['Date'] if 'Date' in data.columns else range(len(data)),
                                    y=ml_data['SMA_20'],
                                    mode='lines',
                                    name='SMA 20',
                                    line=dict(color='orange', dash='dash')
                                ))
                            
                            fig.update_layout(
                                title=f"{symbols[0]} - Stock Price",
                                xaxis_title="Date",
                                yaxis_title="Price ($)",
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Save to CSV option
                        st.subheader("💾 Save Dataset")
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{symbols[0]}_{task_type}_{timestamp}.csv"
                        
                        csv_data = ml_data.to_csv(index=False)
                        st.download_button(
                            label="📥 Download ML Dataset",
                            data=csv_data,
                            file_name=filename,
                            mime="text/csv",
                            help="Download the prepared dataset for further analysis"
                        )
                    else:
                        st.error("Failed to prepare ML dataset!")
                else:
                    st.error("No data could be fetched!")
                    
        except Exception as e:
            st.error(f"Error fetching financial data: {str(e)}")
    
    # Market summary for multiple symbols
    if len(symbols) > 1 and st.button("📊 Show Market Summary"):
        try:
            with st.spinner("Fetching market summary..."):
                summary_df = st.session_state.financial_fetcher.get_market_data_summary(symbols[:10])  # Limit to 10
                
                if not summary_df.empty:
                    st.subheader("📈 Market Summary")
                    st.dataframe(summary_df, use_container_width=True)
                else:
                    st.warning("No market data available for the selected symbols.")
                    
        except Exception as e:
            st.error(f"Error fetching market summary: {str(e)}")

def data_upload_page():
    st.markdown('<h2 class="subheader">📊 Data Upload & Analysis</h2>', unsafe_allow_html=True)
    
    # Data source selection
    st.subheader("📁 Choose Data Source")
    
    data_source_option = st.radio(
        "Select data source:",
        ["Upload CSV File", "Use Sample Dataset", "Financial Data (Yahoo Finance)"],
        help="Choose how you want to provide your dataset"
    )
    
    if data_source_option == "Upload CSV File":
        # File upload
        uploaded_file = st.file_uploader(
            "Upload your dataset (CSV format)",
            type=['csv'],
            help="Upload a CSV file with your dataset for AutoML training"
        )
        
        if uploaded_file is not None:
            try:
                # Load data
                data = pd.read_csv(uploaded_file)
                st.session_state.data = data
                
                st.success(f"✅ Dataset loaded successfully! Shape: {data.shape}")
                
                # Display basic info
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Rows", data.shape[0])
                with col2:
                    st.metric("Columns", data.shape[1])
                with col3:
                    st.metric("Missing Values", data.isnull().sum().sum())
                with col4:
                    st.metric("Memory Usage", f"{data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
                
                # Data preview
                st.subheader("📋 Data Preview")
                st.dataframe(data.head(100), use_container_width=True)
                
                # Data analysis
                if st.button("🔍 Analyze Dataset"):
                    analyze_dataset(data)
                    
            except Exception as e:
                st.error(f"Error loading dataset: {str(e)}")
                
    elif data_source_option == "Use Sample Dataset":
        if st.button("📝 Generate Sample Dataset"):
            sample_data = create_sample_dataset()
            st.session_state.data = sample_data
            st.success("✅ Sample dataset loaded!")
            st.rerun()
            
    elif data_source_option == "Financial Data (Yahoo Finance)":
        st.info("👆 Please go to the 'Financial Data' page to fetch financial data from Yahoo Finance.")
        if st.button("🔗 Go to Financial Data Page"):
            st.session_state.page = "💹 Financial Data"
            st.rerun()
    
    # Show current dataset info if available
    if st.session_state.data is not None:
        st.subheader("📊 Current Dataset Information")
        data = st.session_state.data
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Dataset Shape", f"{data.shape[0]} × {data.shape[1]}")
        with col2:
            st.metric("Numeric Columns", len(data.select_dtypes(include=[np.number]).columns))
        with col3:
            st.metric("Categorical Columns", len(data.select_dtypes(include=['object']).columns))

def analyze_dataset(data):
    """Analyze dataset and display results."""
    with st.spinner("Analyzing dataset..."):
        analysis = st.session_state.preprocessor.analyze_data(data)
        
        # Display analysis results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Column Information")
            
            # Data types
            dtype_df = pd.DataFrame({
                'Column': data.columns,
                'Data Type': data.dtypes.values,
                'Non-Null Count': data.count().values,
                'Unique Values': [data[col].nunique() for col in data.columns]
            })
            st.dataframe(dtype_df, use_container_width=True)
        
        with col2:
            st.subheader("🔍 Missing Values Analysis")
            
            missing_df = pd.DataFrame({
                'Column': data.columns,
                'Missing Count': data.isnull().sum().values,
                'Missing %': (data.isnull().sum() / len(data) * 100).values
            })
            missing_df = missing_df[missing_df['Missing Count'] > 0]
            
            if len(missing_df) > 0:
                st.dataframe(missing_df, use_container_width=True)
                
                # Visualize missing values
                fig_missing = st.plotly_chart(
                    {
                        'data': [{
                            'x': missing_df['Column'],
                            'y': missing_df['Missing %'],
                            'type': 'bar',
                            'marker': {'color': '#ff7f0e'}
                        }],
                        'layout': {
                            'title': 'Missing Values by Column (%)',
                            'xaxis': {'title': 'Columns'},
                            'yaxis': {'title': 'Missing Percentage'}
                        }
                    },
                    use_container_width=True
                )
            else:
                st.info("✨ No missing values found in the dataset!")
        
        # Summary statistics
        st.subheader("📈 Summary Statistics")
        
        # Numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            st.write("**Numeric Columns:**")
            st.dataframe(data[numeric_cols].describe(), use_container_width=True)
        
        # Categorical columns
        categorical_cols = data.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            st.write("**Categorical Columns:**")
            cat_summary = pd.DataFrame({
                'Column': categorical_cols,
                'Unique Values': [data[col].nunique() for col in categorical_cols],
                'Most Frequent': [data[col].mode()[0] if len(data[col].mode()) > 0 else 'N/A' for col in categorical_cols],
                'Frequency': [data[col].value_counts().iloc[0] if len(data[col].value_counts()) > 0 else 0 for col in categorical_cols]
            })
            st.dataframe(cat_summary, use_container_width=True)

def preprocessing_page():
    st.markdown('<h2 class="subheader">⚙️ Data Preprocessing</h2>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload a dataset first!")
        return
    
    data = st.session_state.data
    
    # Target column selection
    st.subheader("🎯 Select Target Column")
    target_column = st.selectbox(
        "Choose the target column for prediction:",
        data.columns.tolist(),
        help="Select the column you want to predict"
    )
    
    # Task type detection/selection
    if target_column:
        if data[target_column].dtype == 'object' or data[target_column].nunique() < 10:
            default_task = 'classification'
        else:
            default_task = 'regression'
        
        task_type = st.selectbox(
            "Task Type:",
            ['classification', 'regression'],
            index=0 if default_task == 'classification' else 1,
            help="Choose whether this is a classification or regression problem"
        )
        
        # Display target column info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Unique Values", data[target_column].nunique())
        with col2:
            st.metric("Missing Values", data[target_column].isnull().sum())
        with col3:
            if task_type == 'classification':
                st.metric("Classes", data[target_column].nunique())
            else:
                st.metric("Range", f"{data[target_column].min():.2f} - {data[target_column].max():.2f}")
    
    # Preprocessing options
    st.subheader("🛠️ Preprocessing Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Missing values
        st.write("**Missing Values Strategy:**")
        missing_strategy = st.selectbox(
            "Strategy for handling missing values:",
            ['mean', 'median', 'mode', 'knn'],
            help="Choose how to handle missing values in the dataset"
        )
        
        # Encoding
        st.write("**Categorical Encoding:**")
        encoding_method = st.selectbox(
            "Method for encoding categorical variables:",
            ['label', 'onehot'],
            help="Choose how to encode categorical variables"
        )
    
    with col2:
        # Scaling
        st.write("**Feature Scaling:**")
        scaling_method = st.selectbox(
            "Method for scaling numerical features:",
            ['standard', 'minmax'],
            help="Choose how to scale numerical features"
        )
        
        # Feature selection
        st.write("**Feature Selection:**")
        enable_feature_selection = st.checkbox("Enable feature selection")
        
        if enable_feature_selection:
            max_features = min(20, data.shape[1] - 1)
            feature_selection_k = st.slider(
                "Number of features to select:",
                min_value=1,
                max_value=max_features,
                value=min(10, max_features),
                help="Select top K features based on statistical tests"
            )
        else:
            feature_selection_k = None
    
    # Train-test split
    st.write("**Train-Test Split:**")
    test_size = st.slider(
        "Test set size (%):",
        min_value=10,
        max_value=40,
        value=20,
        help="Percentage of data to use for testing"
    ) / 100
    
    # Preprocess button
    if st.button("🚀 Run Preprocessing", type="primary"):
        if not target_column:
            st.error("Please select a target column!")
            return
        
        try:
            with st.spinner("Preprocessing data..."):
                # Run preprocessing pipeline
                X_train, X_test, y_train, y_test, feature_columns = st.session_state.preprocessor.preprocess_pipeline(
                    df=data,
                    target_column=target_column,
                    test_size=test_size,
                    missing_strategy=missing_strategy,
                    encoding_method=encoding_method,
                    scaling_method=scaling_method,
                    feature_selection_k=feature_selection_k,
                    task_type=task_type
                )
                
                # Store in session state
                st.session_state.X_train = X_train
                st.session_state.X_test = X_test
                st.session_state.y_train = y_train
                st.session_state.y_test = y_test
                st.session_state.feature_columns = feature_columns
                st.session_state.target_column = target_column
                st.session_state.task_type = task_type
                st.session_state.preprocessing_params = {
                    'missing_strategy': missing_strategy,
                    'encoding_method': encoding_method,
                    'scaling_method': scaling_method,
                    'feature_selection_k': feature_selection_k,
                    'test_size': test_size,
                    'train_size': 1 - test_size
                }
                
                st.success("✅ Preprocessing completed successfully!")
                
                # Display results
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Training Samples", X_train.shape[0])
                with col2:
                    st.metric("Test Samples", X_test.shape[0])
                with col3:
                    st.metric("Features", X_train.shape[1])
                with col4:
                    st.metric("Target Type", task_type.title())
                
                # Preview processed data
                st.subheader("📋 Processed Data Preview")
                
                # Training data preview
                st.write("**Training Data (First 5 rows):**")
                train_preview = X_train.head()
                train_preview[target_column] = y_train[:5]
                st.dataframe(train_preview, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error during preprocessing: {str(e)}")

def automl_training_page():
    st.markdown('<h2 class="subheader">🚀 AutoML Training</h2>', unsafe_allow_html=True)
    
    # Check if preprocessing is done
    if not all(key in st.session_state for key in ['X_train', 'X_test', 'y_train', 'y_test']):
        st.warning("⚠️ Please complete data preprocessing first!")
        return
    
    # Initialize AutoML engine
    if st.session_state.automl_engine is None:
        st.session_state.automl_engine = AutoMLEngine(task_type=st.session_state.task_type)
    
    # AutoML configuration
    st.subheader("🎛️ AutoML Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Model selection
        available_models = st.session_state.automl_engine.get_available_models()
        
        selected_models = st.multiselect(
            "Select models to compare (leave empty for all):",
            options=list(available_models.keys()),
            format_func=lambda x: f"{x}: {available_models[x]}",
            help="Choose specific models to compare, or leave empty to compare all available models"
        )
        
        if not selected_models:
            selected_models = None
    
    with col2:
        # Number of models to select
        n_select = st.slider(
            "Number of top models to select:",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of best performing models to keep for comparison"
        )
    
    # Training button
    if st.button("🎯 Start AutoML Training", type="primary"):
        try:
            with st.spinner("Setting up AutoML environment..."):
                # Setup AutoML
                setup_success = st.session_state.automl_engine.setup_automl(
                    st.session_state.X_train,
                    st.session_state.y_train,
                    st.session_state.target_column
                )
                
                if not setup_success:
                    st.error("Failed to setup AutoML environment!")
                    return
                
                st.success("✅ AutoML environment setup completed!")
            
            # Compare models
            with st.spinner("Training and comparing models... This may take several minutes."):
                models = st.session_state.automl_engine.compare_models(
                    include_models=selected_models,
                    n_select=n_select
                )
                
                if models is not None:
                    # Get results DataFrame
                    results_df = st.session_state.automl_engine.get_model_results_df()
                    
                    if results_df is not None:
                        # Store results in session state
                        st.session_state.model_results = results_df
                        st.session_state.trained_models = models
                        
                        st.success("🎉 AutoML training completed successfully!")
                        
                        # Display results preview
                        st.subheader("📊 Model Comparison Results")
                        st.dataframe(results_df, use_container_width=True)
                        
                        # Create and display plots
                        plots = st.session_state.automl_engine.plot_model_comparison(results_df)
                        if plots:
                            if st.session_state.task_type == 'classification':
                                fig_acc, fig_f1 = plots
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.plotly_chart(fig_acc, use_container_width=True)
                                with col2:
                                    st.plotly_chart(fig_f1, use_container_width=True)
                            else:
                                fig_rmse, fig_r2 = plots
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.plotly_chart(fig_rmse, use_container_width=True)
                                with col2:
                                    st.plotly_chart(fig_r2, use_container_width=True)
                    else:
                        st.error("Failed to retrieve model comparison results!")
                else:
                    st.error("Model training failed!")
                    
        except Exception as e:
            st.error(f"Error during AutoML training: {str(e)}")

def model_comparison_page():
    st.markdown('<h2 class="subheader">📈 Model Comparison</h2>', unsafe_allow_html=True)
    
    if 'model_results' not in st.session_state or st.session_state.model_results is None:
        st.warning("⚠️ Please complete AutoML training first!")
        return
    
    results_df = st.session_state.model_results
    
    # Display detailed results
    st.subheader("📊 Detailed Model Results")
    st.dataframe(results_df, use_container_width=True)
    
    # Model selection for detailed analysis
    st.subheader("🔍 Select Model for Detailed Analysis")
    
    model_names = results_df.index.tolist()
    selected_model_idx = st.selectbox(
        "Choose a model to analyze:",
        range(len(model_names)),
        format_func=lambda x: model_names[x]
    )
    
    if selected_model_idx is not None:
        selected_model_name = model_names[selected_model_idx]
        selected_model = st.session_state.trained_models[selected_model_idx]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Selected Model: {selected_model_name}**")
            
            # Display metrics
            model_metrics = results_df.loc[selected_model_name]
            for metric, value in model_metrics.items():
                if isinstance(value, (int, float)):
                    st.metric(metric, f"{value:.4f}")
        
        with col2:
            # Model evaluation
            if st.button("📊 Evaluate Model"):
                try:
                    with st.spinner("Evaluating model..."):
                        st.session_state.automl_engine.evaluate_model(selected_model)
                        st.success("Model evaluation completed! Check the plots above.")
                except Exception as e:
                    st.error(f"Error evaluating model: {str(e)}")
        
        # Model finalization and saving
        st.subheader("💾 Save Model")
        
        col1, col2 = st.columns(2)
        
        with col1:
            model_name = st.text_input(
                "Model Name:",
                value=f"{selected_model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                help="Enter a name for saving this model"
            )
        
        with col2:
            if st.button("💾 Save Selected Model", type="primary"):
                try:
                    with st.spinner("Finalizing and saving model..."):
                        # Finalize model
                        final_model = st.session_state.automl_engine.finalize_model(selected_model)
                        
                        if final_model is not None:
                            # Prepare performance metrics
                            performance_metrics = {}
                            for metric, value in model_metrics.items():
                                if isinstance(value, (int, float)):
                                    performance_metrics[metric] = value
                            
                            # Save model
                            model_id = st.session_state.model_manager.save_model(
                                model=final_model,
                                model_name=model_name,
                                model_type=st.session_state.task_type,
                                performance_metrics=performance_metrics,
                                preprocessing_params=st.session_state.preprocessing_params,
                                feature_columns=st.session_state.feature_columns
                            )
                            
                            if model_id:
                                st.success(f"✅ Model saved successfully with ID: {model_id}")
                        else:
                            st.error("Failed to finalize model!")
                            
                except Exception as e:
                    st.error(f"Error saving model: {str(e)}")

def prediction_page():
    st.markdown('<h2 class="subheader">🔮 Make Predictions</h2>', unsafe_allow_html=True)
    
    # Model selection
    models_df = st.session_state.model_manager.list_models()
    
    if models_df.empty:
        st.warning("⚠️ No saved models found! Please train and save a model first.")
        return
    
    st.subheader("📋 Select Model")
    
    # Display available models
    st.dataframe(models_df, use_container_width=True)
    
    model_ids = models_df['Model ID'].tolist()
    selected_model_id = st.selectbox(
        "Choose a model for prediction:",
        model_ids,
        help="Select a saved model to use for predictions"
    )
    
    if selected_model_id:
        # Load model
        model, metadata = st.session_state.model_manager.load_model(selected_model_id)
        
        if model is None:
            st.error("Failed to load selected model!")
            return
        
        st.success(f"✅ Model loaded: {metadata['model_name']}")
        
        # Prediction options
        st.subheader("🎯 Make Predictions")
        
        prediction_type = st.radio(
            "Choose prediction type:",
            ["Single Prediction", "Batch Prediction"],
            help="Make a single prediction or upload a file for batch predictions"
        )
        
        if prediction_type == "Single Prediction":
            single_prediction(model, metadata)
        else:
            batch_prediction(model, metadata)

def single_prediction(model, metadata):
    """Handle single prediction input."""
    st.write("**Enter feature values for prediction:**")
    
    feature_columns = metadata.get('feature_columns', [])
    
    if not feature_columns:
        st.error("No feature information found for this model!")
        return
    
    # Create input fields for each feature
    input_data = {}
    
    # Arrange inputs in columns
    cols = st.columns(3)
    
    for i, feature in enumerate(feature_columns):
        with cols[i % 3]:
            # Try to infer input type based on feature name
            if any(keyword in feature.lower() for keyword in ['age', 'year', 'count', 'number', 'size']):
                input_data[feature] = st.number_input(f"{feature}:", value=0.0, key=f"input_{feature}")
            else:
                input_data[feature] = st.text_input(f"{feature}:", key=f"input_{feature}")
    
    if st.button("🎯 Make Prediction", type="primary"):
        try:
            # Create DataFrame from input
            input_df = pd.DataFrame([input_data])
            
            # Transform input data using saved preprocessor
            if hasattr(st.session_state, 'preprocessor'):
                processed_input = st.session_state.preprocessor.transform_new_data(
                    input_df, feature_columns
                )
            else:
                processed_input = input_df
            
            # Make prediction
            with st.spinner("Making prediction..."):
                prediction = st.session_state.automl_engine.make_predictions(model, processed_input)
                
                if prediction is not None:
                    # Extract prediction result
                    if hasattr(prediction, 'prediction_label'):
                        result = prediction['prediction_label'].iloc[0]
                    else:
                        result = prediction.iloc[0, -1]  # Last column usually contains predictions
                    
                    # Display result
                    st.success("🎉 Prediction completed!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Prediction", result)
                    
                    with col2:
                        if metadata['model_type'] == 'classification':
                            if hasattr(prediction, 'prediction_score'):
                                confidence = prediction['prediction_score'].iloc[0]
                                st.metric("Confidence", f"{confidence:.4f}")
                else:
                    st.error("Prediction failed!")
                    
        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")

def batch_prediction(model, metadata):
    """Handle batch prediction from uploaded file."""
    st.write("**Upload a CSV file for batch predictions:**")
    
    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=['csv'],
        help="Upload a CSV file with the same features as training data"
    )
    
    if uploaded_file is not None:
        try:
            # Load data
            batch_data = pd.read_csv(uploaded_file)
            
            st.write("**Data Preview:**")
            st.dataframe(batch_data.head(), use_container_width=True)
            
            feature_columns = metadata.get('feature_columns', [])
            
            # Check if all required features are present
            missing_features = set(feature_columns) - set(batch_data.columns)
            if missing_features:
                st.error(f"Missing required features: {', '.join(missing_features)}")
                return
            
            if st.button("🚀 Run Batch Prediction", type="primary"):
                with st.spinner("Processing batch predictions..."):
                    # Transform input data
                    if hasattr(st.session_state, 'preprocessor'):
                        processed_data = st.session_state.preprocessor.transform_new_data(
                            batch_data, feature_columns
                        )
                    else:
                        processed_data = batch_data[feature_columns]
                    
                    # Make predictions
                    predictions = st.session_state.automl_engine.make_predictions(model, processed_data)
                    
                    if predictions is not None:
                        st.success(f"✅ Batch prediction completed for {len(batch_data)} samples!")
                        
                        # Display results
                        if hasattr(predictions, 'prediction_label'):
                            batch_data['Prediction'] = predictions['prediction_label']
                            if hasattr(predictions, 'prediction_score'):
                                batch_data['Confidence'] = predictions['prediction_score']
                        else:
                            batch_data['Prediction'] = predictions.iloc[:, -1]
                        
                        st.write("**Results:**")
                        st.dataframe(batch_data, use_container_width=True)
                        
                        # Download results
                        csv_download = batch_data.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results",
                            data=csv_download,
                            file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error("Batch prediction failed!")
                        
        except Exception as e:
            st.error(f"Error processing batch prediction: {str(e)}")

def model_management_page():
    st.markdown('<h2 class="subheader">💾 Model Management</h2>', unsafe_allow_html=True)
    
    # Display saved models
    models_df = st.session_state.model_manager.list_models()
    
    if models_df.empty:
        st.info("📝 No saved models found.")
        return
    
    st.subheader("📋 Saved Models")
    st.dataframe(models_df, use_container_width=True)
    
    # Storage usage
    storage_info = st.session_state.model_manager.get_storage_usage()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Models", storage_info['model_count'])
    with col2:
        st.metric("Total Storage", f"{storage_info['total_size_mb']} MB")
    with col3:
        st.metric("Avg Model Size", f"{storage_info['avg_size_mb']} MB")
    
    # Model operations
    st.subheader("🛠️ Model Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Delete model
        st.write("**Delete Model:**")
        model_to_delete = st.selectbox(
            "Select model to delete:",
            [''] + models_df['Model ID'].tolist(),
            key="delete_model"
        )
        
        if model_to_delete and st.button("🗑️ Delete Model", type="secondary"):
            if st.session_state.model_manager.delete_model(model_to_delete):
                st.rerun()
    
    with col2:
        # Export models summary
        st.write("**Export Summary:**")
        if st.button("📥 Export Models Summary"):
            export_path = st.session_state.model_manager.export_model_summary()
            if export_path:
                st.success(f"✅ Summary exported to: {export_path}")
    
    # Cleanup old models
    st.subheader("🧹 Cleanup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        keep_latest = st.slider(
            "Keep latest N models:",
            min_value=1,
            max_value=20,
            value=5,
            help="Number of latest models to keep when cleaning up"
        )
    
    with col2:
        if st.button("🧹 Cleanup Old Models"):
            st.session_state.model_manager.cleanup_old_models(keep_latest)
            st.rerun()

def report_generation_page():
    st.markdown('<h2 class="subheader">📄 Generate Report</h2>', unsafe_allow_html=True)
    
    # Project information
    st.subheader("📝 Project Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input("Project Name:", value="AutoML Project")
        author_name = st.text_input("Author:", value="Data Scientist")
    
    with col2:
        dataset_name = st.text_input("Dataset Name:", value="Custom Dataset")
        task_type = st.session_state.get('task_type', 'classification')
        st.text_input("Task Type:", value=task_type.title(), disabled=True)
    
    # Report generation
    if st.button("📄 Generate Project Report", type="primary"):
        try:
            with st.spinner("Generating report..."):
                # Prepare data for report
                project_info = {
                    'name': project_name,
                    'author': author_name,
                    'dataset_name': dataset_name,
                    'task_type': task_type
                }
                
                # Get data analysis
                data_analysis = None
                if st.session_state.data is not None:
                    data_analysis = st.session_state.preprocessor.analyze_data(st.session_state.data)
                
                # Get model results
                model_results = st.session_state.get('model_results', None)
                
                # Get best model info
                best_model_info = None
                best_model_id, _ = st.session_state.model_manager.get_best_model(
                    metric='Accuracy' if task_type == 'classification' else 'RMSE',
                    task_type=task_type
                )
                if best_model_id:
                    best_model_info = st.session_state.model_manager.get_model_details(best_model_id)
                
                # Get preprocessing parameters
                preprocessing_params = st.session_state.get('preprocessing_params', None)
                
                # Generate report
                report_generator = ReportGenerator()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_path = f"reports/automl_report_{timestamp}.pdf"
                
                os.makedirs('reports', exist_ok=True)
                
                report_file = report_generator.create_project_report(
                    output_path=report_path,
                    project_info=project_info,
                    data_analysis=data_analysis,
                    model_results=model_results,
                    best_model_info=best_model_info,
                    preprocessing_params=preprocessing_params
                )
                
                st.success(f"✅ Report generated successfully: {report_file}")
                
                # Download button
                with open(report_file, "rb") as f:
                    st.download_button(
                        label="📥 Download Report",
                        data=f.read(),
                        file_name=f"automl_report_{timestamp}.pdf",
                        mime="application/pdf"
                    )
                    
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
    
    # Deployment guide
    st.subheader("🚀 Deployment Guide")
    
    if st.button("📚 Generate Deployment Guide"):
        try:
            with st.spinner("Generating deployment guide..."):
                report_generator = ReportGenerator()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                guide_path = f"reports/deployment_guide_{timestamp}.pdf"
                
                os.makedirs('reports', exist_ok=True)
                
                guide_file = report_generator.create_deployment_guide(guide_path)
                
                st.success(f"✅ Deployment guide generated: {guide_file}")
                
                # Download button
                with open(guide_file, "rb") as f:
                    st.download_button(
                        label="📥 Download Deployment Guide",
                        data=f.read(),
                        file_name=f"deployment_guide_{timestamp}.pdf",
                        mime="application/pdf"
                    )
                    
        except Exception as e:
            st.error(f"Error generating deployment guide: {str(e)}")

def create_sample_dataset():
    """Create a sample dataset for demonstration."""
    np.random.seed(42)
    
    n_samples = 1000
    
    # Generate sample data
    data = {
        'age': np.random.randint(18, 80, n_samples),
        'income': np.random.normal(50000, 20000, n_samples),
        'education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_samples),
        'experience': np.random.randint(0, 40, n_samples),
        'city': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'], n_samples),
        'score': np.random.normal(75, 15, n_samples)
    }
    
    # Create target variable
    # Classification target
    target_prob = (data['age'] / 80 + data['income'] / 100000 + data['experience'] / 40) / 3
    data['approved'] = np.random.binomial(1, target_prob, n_samples)
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    main() 