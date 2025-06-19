from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import pandas as pd
import os


class ReportGenerator:
    """Generate PDF reports for AutoML projects."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.darkblue,
            spaceAfter=15
        )
    
    def create_project_report(self, output_path, project_info, data_analysis, 
                            model_results, best_model_info, preprocessing_params=None):
        """Create a comprehensive project report."""
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Title Page
        story.append(Paragraph("AutoML Project Report", self.title_style))
        story.append(Spacer(1, 20))
        
        # Project Information
        story.append(Paragraph("Project Information", self.heading_style))
        project_table_data = [
            ["Project Name", project_info.get('name', 'AutoML Project')],
            ["Date Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Task Type", project_info.get('task_type', 'Classification')],
            ["Dataset Name", project_info.get('dataset_name', 'Unknown')],
            ["Author", project_info.get('author', 'AutoML System')]
        ]
        
        project_table = Table(project_table_data, colWidths=[2*inch, 3*inch])
        project_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(project_table)
        story.append(Spacer(1, 20))
        
        # Data Analysis Section
        story.append(Paragraph("Data Analysis", self.heading_style))
        
        if data_analysis:
            data_info = [
                ["Dataset Shape", f"{data_analysis['shape'][0]} rows × {data_analysis['shape'][1]} columns"],
                ["Numeric Columns", str(len(data_analysis['numeric_columns']))],
                ["Categorical Columns", str(len(data_analysis['categorical_columns']))],
                ["Missing Values", str(sum(data_analysis['missing_values'].values()))],
                ["Total Features", str(len(data_analysis['columns']) - 1)]  # Excluding target
            ]
            
            data_table = Table(data_info, colWidths=[2*inch, 3*inch])
            data_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(data_table)
            story.append(Spacer(1, 20))
        
        # Preprocessing Parameters
        if preprocessing_params:
            story.append(Paragraph("Preprocessing Configuration", self.heading_style))
            
            preprocessing_info = [
                ["Missing Value Strategy", preprocessing_params.get('missing_strategy', 'Default')],
                ["Encoding Method", preprocessing_params.get('encoding_method', 'Label Encoding')],
                ["Scaling Method", preprocessing_params.get('scaling_method', 'Standard Scaling')],
                ["Feature Selection", preprocessing_params.get('feature_selection', 'None')],
                ["Train-Test Split", f"{preprocessing_params.get('train_size', 0.8)*100:.0f}% - {preprocessing_params.get('test_size', 0.2)*100:.0f}%"]
            ]
            
            preprocessing_table = Table(preprocessing_info, colWidths=[2*inch, 3*inch])
            preprocessing_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkgreen),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(preprocessing_table)
            story.append(Spacer(1, 20))
        
        # Model Results Section
        story.append(Paragraph("Model Comparison Results", self.heading_style))
        
        if model_results is not None and not model_results.empty:
            # Convert DataFrame to table data
            model_data = [model_results.columns.tolist()]  # Header
            for idx, row in model_results.head(10).iterrows():  # Top 10 models
                model_data.append([str(idx)] + [f"{val:.4f}" if isinstance(val, (int, float)) else str(val) 
                                              for val in row.tolist()])
            
            model_table = Table(model_data)
            model_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))
            
            story.append(model_table)
            story.append(Spacer(1, 20))
        
        # Best Model Section
        if best_model_info:
            story.append(Paragraph("Best Model Details", self.heading_style))
            
            best_model_data = [
                ["Model Name", best_model_info.get('model_name', 'Unknown')],
                ["Model Type", best_model_info.get('model_type', 'Unknown')],
                ["Training Date", best_model_info.get('datetime', 'Unknown')],
                ["File Size", f"{best_model_info.get('file_size_mb', 0)} MB"]
            ]
            
            # Add performance metrics
            metrics = best_model_info.get('performance_metrics', {})
            for metric, value in metrics.items():
                if isinstance(value, (int, float)):
                    best_model_data.append([metric, f"{value:.4f}"])
                else:
                    best_model_data.append([metric, str(value)])
            
            best_model_table = Table(best_model_data, colWidths=[2*inch, 3*inch])
            best_model_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.gold),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkred),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(best_model_table)
            story.append(Spacer(1, 20))
        
        # Recommendations Section
        story.append(Paragraph("Recommendations", self.heading_style))
        
        recommendations = [
            "• Monitor model performance regularly and retrain when necessary",
            "• Consider ensemble methods for improved performance",
            "• Validate model predictions on new, unseen data",
            "• Document any data drift or concept drift observations",
            "• Set up automated monitoring for production deployment",
            "• Consider A/B testing for model comparison in production",
            "• Maintain version control for models and datasets",
            "• Ensure data privacy and security compliance"
        ]
        
        for recommendation in recommendations:
            story.append(Paragraph(recommendation, self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph("Generated by AutoML Web Application", 
                             ParagraphStyle('Footer', 
                                          parent=self.styles['Normal'],
                                          fontSize=10,
                                          textColor=colors.grey,
                                          alignment=1)))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def create_deployment_guide(self, output_path):
        """Create a deployment guide PDF."""
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Title
        story.append(Paragraph("AutoML Application Deployment Guide", self.title_style))
        story.append(Spacer(1, 20))
        
        # Docker Deployment
        story.append(Paragraph("Docker Deployment", self.heading_style))
        
        docker_steps = [
            "1. Build the Docker image:",
            "   docker build -t automl-app .",
            "",
            "2. Run the container:",
            "   docker run -p 8501:8501 automl-app",
            "",
            "3. Access the application at http://localhost:8501"
        ]
        
        for step in docker_steps:
            story.append(Paragraph(step, self.styles['Code'] if step.strip().startswith('docker') else self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Azure Deployment
        story.append(Paragraph("Azure Container Instances Deployment", self.heading_style))
        
        azure_steps = [
            "1. Login to Azure CLI:",
            "   az login",
            "",
            "2. Create a resource group:",
            "   az group create --name automl-rg --location eastus",
            "",
            "3. Create container registry:",
            "   az acr create --resource-group automl-rg --name automlregistry --sku Basic",
            "",
            "4. Push image to registry:",
            "   docker tag automl-app automlregistry.azurecr.io/automl-app:latest",
            "   docker push automlregistry.azurecr.io/automl-app:latest",
            "",
            "5. Deploy to Container Instances:",
            "   az container create --resource-group automl-rg --name automl-app",
            "   --image automlregistry.azurecr.io/automl-app:latest --ports 8501"
        ]
        
        for step in azure_steps:
            if step.strip().startswith('az ') or step.strip().startswith('docker '):
                story.append(Paragraph(step, self.styles['Code']))
            else:
                story.append(Paragraph(step, self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Configuration
        story.append(Paragraph("Configuration", self.heading_style))
        
        config_info = [
            "• Environment variables can be set in .env file",
            "• Azure storage credentials for model persistence",
            "• SSL certificates for HTTPS deployment",
            "• Custom domain configuration",
            "• Monitoring and logging setup"
        ]
        
        for info in config_info:
            story.append(Paragraph(info, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return output_path 