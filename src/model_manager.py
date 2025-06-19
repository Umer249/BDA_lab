import os
import json
import joblib
import pandas as pd
from datetime import datetime
import streamlit as st
from pathlib import Path


class ModelManager:
    """Manage trained models with metadata tracking."""
    
    def __init__(self, models_dir='models'):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.metadata_file = self.models_dir / 'model_metadata.json'
        self.load_metadata()
    
    def load_metadata(self):
        """Load model metadata from JSON file."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
    def save_metadata(self):
        """Save model metadata to JSON file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
    
    def save_model(self, model, model_name, model_type, performance_metrics, 
                   preprocessing_params=None, feature_columns=None):
        """Save model with comprehensive metadata."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_id = f"{model_name}_{timestamp}"
            model_path = self.models_dir / f"{model_id}.pkl"
            
            # Save the model
            joblib.dump(model, model_path)
            
            # Save metadata
            self.metadata[model_id] = {
                'model_name': model_name,
                'model_type': model_type,
                'timestamp': timestamp,
                'datetime': datetime.now().isoformat(),
                'model_path': str(model_path),
                'performance_metrics': performance_metrics,
                'preprocessing_params': preprocessing_params,
                'feature_columns': feature_columns,
                'file_size_mb': round(model_path.stat().st_size / (1024 * 1024), 2)
            }
            
            self.save_metadata()
            
            st.success(f"Model saved successfully as {model_id}")
            return model_id
            
        except Exception as e:
            st.error(f"Error saving model: {str(e)}")
            return None
    
    def load_model(self, model_id):
        """Load model by ID."""
        try:
            if model_id not in self.metadata:
                st.error(f"Model {model_id} not found in metadata.")
                return None, None
            
            model_path = Path(self.metadata[model_id]['model_path'])
            
            if not model_path.exists():
                st.error(f"Model file {model_path} not found.")
                return None, None
            
            model = joblib.load(model_path)
            metadata = self.metadata[model_id]
            
            return model, metadata
            
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
            return None, None
    
    def list_models(self):
        """List all saved models with their metadata."""
        if not self.metadata:
            return pd.DataFrame()
        
        models_data = []
        for model_id, metadata in self.metadata.items():
            model_info = {
                'Model ID': model_id,
                'Model Name': metadata.get('model_name', 'Unknown'),
                'Type': metadata.get('model_type', 'Unknown'),
                'DateTime': metadata.get('datetime', 'Unknown'),
                'File Size (MB)': metadata.get('file_size_mb', 0),
            }
            
            # Add performance metrics
            metrics = metadata.get('performance_metrics', {})
            for metric, value in metrics.items():
                if isinstance(value, (int, float)):
                    model_info[metric] = round(value, 4)
                else:
                    model_info[metric] = value
            
            models_data.append(model_info)
        
        return pd.DataFrame(models_data)
    
    def delete_model(self, model_id):
        """Delete a model and its metadata."""
        try:
            if model_id not in self.metadata:
                st.error(f"Model {model_id} not found.")
                return False
            
            # Delete model file
            model_path = Path(self.metadata[model_id]['model_path'])
            if model_path.exists():
                model_path.unlink()
            
            # Remove from metadata
            del self.metadata[model_id]
            self.save_metadata()
            
            st.success(f"Model {model_id} deleted successfully.")
            return True
            
        except Exception as e:
            st.error(f"Error deleting model: {str(e)}")
            return False
    
    def get_model_details(self, model_id):
        """Get detailed information about a specific model."""
        if model_id not in self.metadata:
            return None
        
        return self.metadata[model_id]
    
    def export_model_summary(self):
        """Export a summary of all models to CSV."""
        try:
            models_df = self.list_models()
            if models_df.empty:
                st.warning("No models to export.")
                return None
            
            export_path = self.models_dir / f"model_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            models_df.to_csv(export_path, index=False)
            
            return export_path
            
        except Exception as e:
            st.error(f"Error exporting model summary: {str(e)}")
            return None
    
    def get_best_model(self, metric='Accuracy', task_type='classification'):
        """Get the best model based on a specific metric."""
        if not self.metadata:
            return None, None
        
        best_model_id = None
        best_score = None
        
        for model_id, metadata in self.metadata.items():
            if metadata.get('model_type') != task_type:
                continue
                
            metrics = metadata.get('performance_metrics', {})
            if metric in metrics:
                score = metrics[metric]
                
                if best_score is None:
                    best_score = score
                    best_model_id = model_id
                else:
                    # For RMSE and similar metrics, lower is better
                    if metric.upper() in ['RMSE', 'MAE', 'MSE']:
                        if score < best_score:
                            best_score = score
                            best_model_id = model_id
                    else:
                        # For accuracy, F1, R2, etc., higher is better
                        if score > best_score:
                            best_score = score
                            best_model_id = model_id
        
        if best_model_id:
            return best_model_id, best_score
        
        return None, None
    
    def cleanup_old_models(self, keep_latest=5):
        """Keep only the latest N models and delete older ones."""
        if len(self.metadata) <= keep_latest:
            return
        
        # Sort models by datetime
        sorted_models = sorted(
            self.metadata.items(),
            key=lambda x: x[1].get('datetime', ''),
            reverse=True
        )
        
        # Keep only the latest models
        models_to_keep = sorted_models[:keep_latest]
        models_to_delete = sorted_models[keep_latest:]
        
        for model_id, _ in models_to_delete:
            self.delete_model(model_id)
        
        st.info(f"Cleaned up old models. Kept {len(models_to_keep)} latest models.")
    
    def get_storage_usage(self):
        """Get total storage usage of saved models."""
        total_size = 0
        model_count = 0
        
        for model_id, metadata in self.metadata.items():
            model_path = Path(metadata['model_path'])
            if model_path.exists():
                total_size += model_path.stat().st_size
                model_count += 1
        
        return {
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'model_count': model_count,
            'avg_size_mb': round(total_size / (1024 * 1024) / max(model_count, 1), 2)
        } 