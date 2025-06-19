import pandas as pd
import numpy as np
from pycaret.classification import *
from pycaret.regression import *
import streamlit as st
import joblib
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go


class AutoMLEngine:
    """AutoML engine using PyCaret for automated machine learning."""
    
    def __init__(self, task_type='classification'):
        self.task_type = task_type
        self.setup_done = False
        self.models = {}
        self.best_model = None
        self.model_results = None
        
    def setup_automl(self, X_train, y_train, target_column):
        """Setup AutoML environment."""
        try:
            # Combine features and target for PyCaret
            train_data = X_train.copy()
            train_data[target_column] = y_train
            
            if self.task_type == 'classification':
                self.ml_setup = setup(
                    data=train_data,
                    target=target_column,
                    train_size=0.8,
                    session_id=123,
                    verbose=False
                )
            else:
                self.ml_setup = setup(
                    data=train_data,
                    target=target_column,
                    train_size=0.8,
                    session_id=123,
                    verbose=False
                )
            
            self.setup_done = True
            return True
            
        except Exception as e:
            st.error(f"Error setting up AutoML: {str(e)}")
            return False
    
    def compare_models(self, include_models=None, n_select=5):
        """Compare multiple models and return results."""
        if not self.setup_done:
            st.error("AutoML setup not completed. Please run setup first.")
            return None
            
        try:
            with st.spinner("Comparing models... This may take a few minutes."):
                if self.task_type == 'classification':
                    self.model_results = compare_models(
                        include=include_models,
                        sort='Accuracy',
                        n_select=n_select,
                        verbose=False
                    )
                else:
                    self.model_results = compare_models(
                        include=include_models,
                        sort='RMSE',
                        n_select=n_select,
                        verbose=False
                    )
                
                return self.model_results
                
        except Exception as e:
            st.error(f"Error comparing models: {str(e)}")
            return None
    
    def get_model_results_df(self):
        """Get model comparison results as DataFrame."""
        if self.model_results is None:
            return None
            
        try:
            if self.task_type == 'classification':
                results_df = pull()
            else:
                results_df = pull()
            
            return results_df
            
        except Exception as e:
            st.error(f"Error retrieving model results: {str(e)}")
            return None
    
    def create_model(self, model_name, **kwargs):
        """Create and train a specific model."""
        if not self.setup_done:
            st.error("AutoML setup not completed. Please run setup first.")
            return None
            
        try:
            model = create_model(model_name, **kwargs)
            return model
            
        except Exception as e:
            st.error(f"Error creating model {model_name}: {str(e)}")
            return None
    
    def tune_model(self, model, **kwargs):
        """Tune hyperparameters of a model."""
        try:
            tuned_model = tune_model(model, **kwargs)
            return tuned_model
            
        except Exception as e:
            st.error(f"Error tuning model: {str(e)}")
            return None
    
    def evaluate_model(self, model):
        """Evaluate model performance."""
        try:
            evaluation = evaluate_model(model)
            return evaluation
            
        except Exception as e:
            st.error(f"Error evaluating model: {str(e)}")
            return None
    
    def finalize_model(self, model):
        """Finalize model (train on entire dataset)."""
        try:
            final_model = finalize_model(model)
            self.best_model = final_model
            return final_model
            
        except Exception as e:
            st.error(f"Error finalizing model: {str(e)}")
            return None
    
    def make_predictions(self, model, X_test):
        """Make predictions on test data."""
        try:
            predictions = predict_model(model, data=X_test)
            return predictions
            
        except Exception as e:
            st.error(f"Error making predictions: {str(e)}")
            return None
    
    def save_model(self, model, model_name):
        """Save trained model."""
        try:
            os.makedirs('models', exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"models/{model_name}_{timestamp}"
            
            save_model(model, filename)
            
            return f"{filename}.pkl"
            
        except Exception as e:
            st.error(f"Error saving model: {str(e)}")
            return None
    
    def load_model(self, model_path):
        """Load saved model."""
        try:
            model = load_model(model_path.replace('.pkl', ''))
            return model
            
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
            return None
    
    def get_available_models(self):
        """Get list of available models for the task type."""
        if self.task_type == 'classification':
            models = {
                'lr': 'Logistic Regression',
                'knn': 'K Neighbors Classifier',
                'nb': 'Naive Bayes',
                'dt': 'Decision Tree Classifier',
                'svm': 'SVM - Linear Kernel',
                'rbfsvm': 'SVM - Radial Kernel',
                'gpc': 'Gaussian Process Classifier',
                'mlp': 'MLP Classifier',
                'ridge': 'Ridge Classifier',
                'rf': 'Random Forest Classifier',
                'qda': 'Quadratic Discriminant Analysis',
                'ada': 'Ada Boost Classifier',
                'gbc': 'Gradient Boosting Classifier',
                'lda': 'Linear Discriminant Analysis',
                'et': 'Extra Trees Classifier',
                'xgboost': 'Extreme Gradient Boosting',
                'lightgbm': 'Light Gradient Boosting Machine',
                'catboost': 'CatBoost Classifier'
            }
        else:
            models = {
                'lr': 'Linear Regression',
                'lasso': 'Lasso Regression',
                'ridge': 'Ridge Regression',
                'en': 'Elastic Net',
                'lar': 'Least Angle Regression',
                'llar': 'Lasso Least Angle Regression',
                'omp': 'Orthogonal Matching Pursuit',
                'br': 'Bayesian Ridge',
                'ard': 'Automatic Relevance Determination',
                'par': 'Passive Aggressive Regressor',
                'ransac': 'Random Sample Consensus',
                'tr': 'TheilSen Regressor',
                'huber': 'Huber Regressor',
                'kr': 'Kernel Ridge',
                'svm': 'Support Vector Regression',
                'knn': 'K Neighbors Regressor',
                'dt': 'Decision Tree Regressor',
                'rf': 'Random Forest Regressor',
                'et': 'Extra Trees Regressor',
                'ada': 'AdaBoost Regressor',
                'gbr': 'Gradient Boosting Regressor',
                'mlp': 'MLP Regressor',
                'xgboost': 'Extreme Gradient Boosting',
                'lightgbm': 'Light Gradient Boosting Machine',
                'catboost': 'CatBoost Regressor'
            }
        
        return models
    
    def plot_model_comparison(self, results_df):
        """Create interactive plots for model comparison."""
        if results_df is None or results_df.empty:
            return None
            
        try:
            # Get model names
            model_names = results_df.index.tolist()
            
            if self.task_type == 'classification':
                # Accuracy plot
                fig_acc = px.bar(
                    x=model_names,
                    y=results_df['Accuracy'].values,
                    title='Model Accuracy Comparison',
                    labels={'x': 'Models', 'y': 'Accuracy'},
                    color=results_df['Accuracy'].values,
                    color_continuous_scale='viridis'
                )
                
                # F1 Score plot
                fig_f1 = px.bar(
                    x=model_names,
                    y=results_df['F1'].values,
                    title='Model F1 Score Comparison',
                    labels={'x': 'Models', 'y': 'F1 Score'},
                    color=results_df['F1'].values,
                    color_continuous_scale='plasma'
                )
                
                return fig_acc, fig_f1
                
            else:
                # RMSE plot
                fig_rmse = px.bar(
                    x=model_names,
                    y=results_df['RMSE'].values,
                    title='Model RMSE Comparison (Lower is Better)',
                    labels={'x': 'Models', 'y': 'RMSE'},
                    color=results_df['RMSE'].values,
                    color_continuous_scale='viridis_r'
                )
                
                # R2 plot
                fig_r2 = px.bar(
                    x=model_names,
                    y=results_df['R2'].values,
                    title='Model R² Score Comparison',
                    labels={'x': 'Models', 'y': 'R² Score'},
                    color=results_df['R2'].values,
                    color_continuous_scale='plasma'
                )
                
                return fig_rmse, fig_r2
                
        except Exception as e:
            st.error(f"Error creating plots: {str(e)}")
            return None 