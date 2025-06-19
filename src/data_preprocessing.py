import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.model_selection import train_test_split
import streamlit as st


class DataPreprocessor:
    """Comprehensive data preprocessing class for AutoML pipeline."""
    
    def __init__(self):
        self.label_encoders = {}
        self.scaler = None
        self.imputer = None
        self.feature_selector = None
        self.target_encoder = None
        
    def analyze_data(self, df):
        """Analyze dataset and provide insights."""
        analysis = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
            'unique_values': {col: df[col].nunique() for col in df.columns}
        }
        return analysis
    
    def handle_missing_values(self, df, strategy='mean', columns=None):
        """Handle missing values using various strategies."""
        df_copy = df.copy()
        
        if columns is None:
            columns = df.columns
            
        for col in columns:
            if df[col].isnull().sum() > 0:
                if df[col].dtype in ['int64', 'float64']:
                    if strategy == 'mean':
                        df_copy[col].fillna(df[col].mean(), inplace=True)
                    elif strategy == 'median':
                        df_copy[col].fillna(df[col].median(), inplace=True)
                    elif strategy == 'mode':
                        df_copy[col].fillna(df[col].mode()[0], inplace=True)
                    elif strategy == 'knn':
                        imputer = KNNImputer(n_neighbors=5)
                        df_copy[col] = imputer.fit_transform(df_copy[[col]])
                else:
                    # Categorical columns
                    if strategy == 'mode':
                        df_copy[col].fillna(df[col].mode()[0], inplace=True)
                    else:
                        df_copy[col].fillna('Unknown', inplace=True)
        
        return df_copy
    
    def encode_categorical_variables(self, df, columns=None, method='label'):
        """Encode categorical variables."""
        df_copy = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=['object']).columns
            
        for col in columns:
            if method == 'label':
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df_copy[col] = self.label_encoders[col].fit_transform(df_copy[col].astype(str))
                else:
                    df_copy[col] = self.label_encoders[col].transform(df_copy[col].astype(str))
            elif method == 'onehot':
                dummies = pd.get_dummies(df_copy[col], prefix=col)
                df_copy = pd.concat([df_copy.drop(col, axis=1), dummies], axis=1)
                
        return df_copy
    
    def scale_features(self, df, columns=None, method='standard'):
        """Scale numerical features."""
        df_copy = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns
            
        if method == 'standard':
            if self.scaler is None:
                self.scaler = StandardScaler()
                df_copy[columns] = self.scaler.fit_transform(df_copy[columns])
            else:
                df_copy[columns] = self.scaler.transform(df_copy[columns])
        elif method == 'minmax':
            if self.scaler is None:
                self.scaler = MinMaxScaler()
                df_copy[columns] = self.scaler.fit_transform(df_copy[columns])
            else:
                df_copy[columns] = self.scaler.transform(df_copy[columns])
                
        return df_copy
    
    def select_features(self, X, y, k=10, task_type='classification'):
        """Select top k features based on statistical tests."""
        if task_type == 'classification':
            score_func = f_classif
        else:
            score_func = f_regression
            
        if self.feature_selector is None:
            self.feature_selector = SelectKBest(score_func=score_func, k=k)
            X_selected = self.feature_selector.fit_transform(X, y)
        else:
            X_selected = self.feature_selector.transform(X)
            
        selected_features = X.columns[self.feature_selector.get_support()]
        return pd.DataFrame(X_selected, columns=selected_features), selected_features
    
    def preprocess_pipeline(self, df, target_column, test_size=0.2, 
                          missing_strategy='mean', encoding_method='label',
                          scaling_method='standard', feature_selection_k=None,
                          task_type='classification'):
        """Complete preprocessing pipeline."""
        
        # Separate features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Handle missing values
        X = self.handle_missing_values(X, strategy=missing_strategy)
        
        # Encode categorical variables
        categorical_cols = X.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            X = self.encode_categorical_variables(X, categorical_cols, method=encoding_method)
        
        # Encode target variable for classification
        if task_type == 'classification' and y.dtype == 'object':
            if self.target_encoder is None:
                self.target_encoder = LabelEncoder()
                y = self.target_encoder.fit_transform(y)
            else:
                y = self.target_encoder.transform(y)
        
        # Scale features
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            X = self.scale_features(X, numeric_cols, method=scaling_method)
        
        # Feature selection
        if feature_selection_k and feature_selection_k < X.shape[1]:
            X, selected_features = self.select_features(X, y, k=feature_selection_k, task_type=task_type)
            st.info(f"Selected features: {', '.join(selected_features)}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y if task_type == 'classification' else None
        )
        
        return X_train, X_test, y_train, y_test, X.columns.tolist()
    
    def transform_new_data(self, df, feature_columns):
        """Transform new data using fitted preprocessors."""
        df_copy = df.copy()
        
        # Handle missing values
        df_copy = self.handle_missing_values(df_copy)
        
        # Encode categorical variables
        categorical_cols = df_copy.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            df_copy = self.encode_categorical_variables(df_copy, categorical_cols)
        
        # Scale features
        numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0 and self.scaler is not None:
            df_copy = self.scale_features(df_copy, numeric_cols)
        
        # Select features
        if self.feature_selector is not None:
            df_copy = pd.DataFrame(
                self.feature_selector.transform(df_copy),
                columns=feature_columns
            )
        
        # Ensure columns match training data
        df_copy = df_copy.reindex(columns=feature_columns, fill_value=0)
        
        return df_copy 