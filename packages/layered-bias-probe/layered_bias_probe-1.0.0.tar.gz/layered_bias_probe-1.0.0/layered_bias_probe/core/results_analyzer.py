"""
Results Analyzer - Provides analysis and visualization of bias analysis results.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional, Union, Tuple
from datetime import datetime


class ResultsAnalyzer:
    """
    Analyzes and visualizes bias analysis results.
    
    This class provides comprehensive analysis capabilities for:
    - Loading and processing bias analysis results
    - Statistical analysis and summaries
    - Interactive and static visualizations
    - Comparative analysis across models, languages, and categories
    """
    
    def __init__(self, results_dir: str, output_dir: Optional[str] = None):
        """
        Initialize the ResultsAnalyzer.
        
        Args:
            results_dir (str): Directory containing bias analysis results
            output_dir (Optional[str]): Directory to save analysis outputs
        """
        self.results_dir = results_dir
        self.output_dir = output_dir or os.path.join(results_dir, "analysis")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Data storage
        self.results_data = None
        self.summary_stats = None
        
        # Load data if available
        self._discover_and_load_data()
    
    def _discover_and_load_data(self):
        """Discover and load bias analysis results from the directory."""
        csv_files = [f for f in os.listdir(self.results_dir) if f.endswith('.csv')]
        
        if not csv_files:
            print(f"No CSV files found in {self.results_dir}")
            return
        
        print(f"Found {len(csv_files)} result files")
        
        # Try to load consolidated results first
        consolidated_files = [f for f in csv_files if 'consolidated' in f.lower()]
        if consolidated_files:
            self._load_csv_file(os.path.join(self.results_dir, consolidated_files[0]))
        else:
            # Load and combine individual files
            self._load_multiple_files(csv_files)
    
    def _load_csv_file(self, filepath: str):
        """Load a single CSV file."""
        try:
            self.results_data = pd.read_csv(filepath)
            print(f"Loaded data from {filepath}: {len(self.results_data)} records")
            self._compute_summary_stats()
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    
    def _load_multiple_files(self, csv_files: List[str]):
        """Load and combine multiple CSV files."""
        dataframes = []
        
        for filename in csv_files:
            try:
                filepath = os.path.join(self.results_dir, filename)
                df = pd.read_csv(filepath)
                dataframes.append(df)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                continue
        
        if dataframes:
            self.results_data = pd.concat(dataframes, ignore_index=True)
            print(f"Combined {len(dataframes)} files: {len(self.results_data)} total records")
            self._compute_summary_stats()
    
    def _compute_summary_stats(self):
        """Compute summary statistics for the loaded data."""
        if self.results_data is None:
            return
        
        self.summary_stats = {
            'total_records': len(self.results_data),
            'unique_models': self.results_data['model_id'].nunique(),
            'unique_languages': self.results_data['language'].nunique(),
            'unique_categories': self.results_data['weat_category_id'].nunique(),
            'models': sorted(self.results_data['model_id'].unique()),
            'languages': sorted(self.results_data['language'].unique()),
            'categories': sorted(self.results_data['weat_category_id'].unique()),
            'layer_range': (
                self.results_data['layer_idx'].min(),
                self.results_data['layer_idx'].max()
            ),
            'bias_score_range': (
                self.results_data['weat_score'].min(),
                self.results_data['weat_score'].max()
            ),
            'mean_absolute_bias': self.results_data['weat_score'].abs().mean()
        }
    
    def load_data(self, filepath: str):
        """Load data from a specific file."""
        self._load_csv_file(filepath)
    
    def get_summary(self) -> Dict:
        """Get summary statistics of the loaded data."""
        return self.summary_stats
    
    def plot_bias_evolution(
        self,
        model_name: str,
        weat_category: str,
        language: str,
        save_plot: bool = True,
        interactive: bool = True
    ):
        """
        Plot bias evolution across layers for a specific model/category/language.
        
        Args:
            model_name (str): Model identifier
            weat_category (str): WEAT category
            language (str): Language code
            save_plot (bool): Whether to save the plot
            interactive (bool): Whether to create an interactive plot
        """
        if self.results_data is None:
            print("No data loaded")
            return
        
        # Filter data
        data = self.results_data[
            (self.results_data['model_id'] == model_name) &
            (self.results_data['weat_category_id'] == weat_category) &
            (self.results_data['language'] == language)
        ]
        
        if data.empty:
            print(f"No data found for {model_name}/{weat_category}/{language}")
            return
        
        # Sort by layer index
        data = data.sort_values('layer_idx')
        
        if interactive:
            # Create interactive plot with Plotly
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=data['layer_idx'],
                y=data['weat_score'],
                mode='lines+markers',
                name=f'{weat_category} Bias',
                line=dict(width=3),
                marker=dict(size=8)
            ))
            
            fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                         annotation_text="No Bias")
            
            fig.update_layout(
                title=f'Layer-wise Bias Evolution<br>{model_name} - {weat_category} ({language.upper()})',
                xaxis_title='Layer Index',
                yaxis_title='WEAT Bias Score',
                template='plotly_white',
                width=800,
                height=500
            )
            
            if save_plot:
                filename = f"bias_evolution_{model_name.replace('/', '_')}_{weat_category}_{language}.html"
                filepath = os.path.join(self.output_dir, filename)
                fig.write_html(filepath)
                print(f"Interactive plot saved to: {filepath}")
            
            fig.show()
            
        else:
            # Create static plot with Matplotlib
            plt.figure(figsize=(10, 6))
            plt.plot(data['layer_idx'], data['weat_score'], 'o-', linewidth=2, markersize=6)
            plt.axhline(y=0, color='gray', linestyle='--', alpha=0.7, label='No Bias')
            
            plt.xlabel('Layer Index')
            plt.ylabel('WEAT Bias Score')
            plt.title(f'Layer-wise Bias Evolution\n{model_name} - {weat_category} ({language.upper()})')
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            if save_plot:
                filename = f"bias_evolution_{model_name.replace('/', '_')}_{weat_category}_{language}.png"
                filepath = os.path.join(self.output_dir, filename)
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                print(f"Plot saved to: {filepath}")
            
            plt.show()
    
    def create_bias_heatmap(
        self,
        model_name: str,
        languages: Optional[List[str]] = None,
        save_plot: bool = True,
        interactive: bool = True
    ):
        """
        Create a heatmap of bias scores across layers and WEAT categories.
        
        Args:
            model_name (str): Model identifier
            languages (Optional[List[str]]): Languages to include (None for all)
            save_plot (bool): Whether to save the plot
            interactive (bool): Whether to create an interactive plot
        """
        if self.results_data is None:
            print("No data loaded")
            return
        
        # Filter data for the model
        data = self.results_data[self.results_data['model_id'] == model_name]
        
        if languages:
            data = data[data['language'].isin(languages)]
        
        if data.empty:
            print(f"No data found for {model_name}")
            return
        
        for lang in data['language'].unique():
            lang_data = data[data['language'] == lang]
            
            # Create pivot table for heatmap
            pivot_table = lang_data.pivot_table(
                index='layer_idx',
                columns='weat_category_id',
                values='weat_score',
                aggfunc='mean'
            )
            
            if interactive:
                # Create interactive heatmap with Plotly
                fig = go.Figure(data=go.Heatmap(
                    z=pivot_table.values,
                    x=pivot_table.columns,
                    y=pivot_table.index,
                    colorscale='RdBu',
                    zmid=0,
                    text=np.round(pivot_table.values, 3),
                    texttemplate="%{text}",
                    textfont={"size": 10},
                    hoverongaps=False
                ))
                
                fig.update_layout(
                    title=f'Bias Heatmap: {model_name} ({lang.upper()})',
                    xaxis_title='WEAT Category',
                    yaxis_title='Layer Index',
                    template='plotly_white',
                    width=800,
                    height=600
                )
                
                if save_plot:
                    filename = f"bias_heatmap_{model_name.replace('/', '_')}_{lang}.html"
                    filepath = os.path.join(self.output_dir, filename)
                    fig.write_html(filepath)
                    print(f"Interactive heatmap saved to: {filepath}")
                
                fig.show()
                
            else:
                # Create static heatmap with Seaborn
                plt.figure(figsize=(12, 8))
                sns.heatmap(
                    pivot_table,
                    cmap="RdBu_r",
                    center=0,
                    annot=True,
                    fmt='.3f',
                    cbar_kws={'label': 'WEAT Bias Score'}
                )
                
                plt.title(f'Bias Heatmap: {model_name} ({lang.upper()})')
                plt.xlabel('WEAT Category')
                plt.ylabel('Layer Index')
                plt.xticks(rotation=45, ha='right')
                
                if save_plot:
                    filename = f"bias_heatmap_{model_name.replace('/', '_')}_{lang}.png"
                    filepath = os.path.join(self.output_dir, filename)
                    plt.savefig(filepath, dpi=300, bbox_inches='tight')
                    print(f"Heatmap saved to: {filepath}")
                
                plt.show()
    
    def compare_models(
        self,
        weat_category: str,
        language: str,
        models: Optional[List[str]] = None,
        save_plot: bool = True,
        interactive: bool = True
    ):
        """
        Compare bias evolution across multiple models.
        
        Args:
            weat_category (str): WEAT category to compare
            language (str): Language code
            models (Optional[List[str]]): Models to compare (None for all)
            save_plot (bool): Whether to save the plot
            interactive (bool): Whether to create an interactive plot
        """
        if self.results_data is None:
            print("No data loaded")
            return
        
        # Filter data
        data = self.results_data[
            (self.results_data['weat_category_id'] == weat_category) &
            (self.results_data['language'] == language)
        ]
        
        if models:
            data = data[data['model_id'].isin(models)]
        
        if data.empty:
            print(f"No data found for {weat_category}/{language}")
            return
        
        if interactive:
            # Create interactive comparison with Plotly
            fig = go.Figure()
            
            for model in data['model_id'].unique():
                model_data = data[data['model_id'] == model].sort_values('layer_idx')
                
                fig.add_trace(go.Scatter(
                    x=model_data['layer_idx'],
                    y=model_data['weat_score'],
                    mode='lines+markers',
                    name=model.split('/')[-1],  # Use model name without organization
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
            
            fig.add_hline(y=0, line_dash="dash", line_color="gray",
                         annotation_text="No Bias")
            
            fig.update_layout(
                title=f'Model Comparison: {weat_category} ({language.upper()})',
                xaxis_title='Layer Index',
                yaxis_title='WEAT Bias Score',
                template='plotly_white',
                width=900,
                height=600,
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02
                )
            )
            
            if save_plot:
                filename = f"model_comparison_{weat_category}_{language}.html"
                filepath = os.path.join(self.output_dir, filename)
                fig.write_html(filepath)
                print(f"Interactive comparison saved to: {filepath}")
            
            fig.show()
            
        else:
            # Create static comparison with Matplotlib
            plt.figure(figsize=(12, 8))
            
            for model in data['model_id'].unique():
                model_data = data[data['model_id'] == model].sort_values('layer_idx')
                plt.plot(
                    model_data['layer_idx'],
                    model_data['weat_score'],
                    'o-',
                    label=model.split('/')[-1],
                    linewidth=2,
                    markersize=5
                )
            
            plt.axhline(y=0, color='gray', linestyle='--', alpha=0.7, label='No Bias')
            plt.xlabel('Layer Index')
            plt.ylabel('WEAT Bias Score')
            plt.title(f'Model Comparison: {weat_category} ({language.upper()})')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True, alpha=0.3)
            
            if save_plot:
                filename = f"model_comparison_{weat_category}_{language}.png"
                filepath = os.path.join(self.output_dir, filename)
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                print(f"Comparison plot saved to: {filepath}")
            
            plt.show()
    
    def generate_summary_report(self, save_report: bool = True) -> Dict:
        """
        Generate a comprehensive summary report.
        
        Args:
            save_report (bool): Whether to save the report to a file
            
        Returns:
            Dict: Summary report data
        """
        if self.results_data is None:
            return {"error": "No data loaded"}
        
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "data_source": self.results_dir,
                "total_records": len(self.results_data)
            },
            "summary_statistics": self.summary_stats,
            "model_analysis": {},
            "language_analysis": {},
            "category_analysis": {}
        }
        
        # Analyze each model
        for model in self.results_data['model_id'].unique():
            model_data = self.results_data[self.results_data['model_id'] == model]
            
            report["model_analysis"][model] = {
                "total_records": len(model_data),
                "languages": sorted(model_data['language'].unique()),
                "categories": sorted(model_data['weat_category_id'].unique()),
                "layer_count": model_data['layer_idx'].nunique(),
                "mean_bias": model_data['weat_score'].mean(),
                "std_bias": model_data['weat_score'].std(),
                "max_absolute_bias": model_data['weat_score'].abs().max(),
                "mean_absolute_bias": model_data['weat_score'].abs().mean()
            }
        
        # Analyze each language
        for lang in self.results_data['language'].unique():
            lang_data = self.results_data[self.results_data['language'] == lang]
            
            report["language_analysis"][lang] = {
                "total_records": len(lang_data),
                "models": sorted(lang_data['model_id'].unique()),
                "categories": sorted(lang_data['weat_category_id'].unique()),
                "mean_bias": lang_data['weat_score'].mean(),
                "std_bias": lang_data['weat_score'].std(),
                "max_absolute_bias": lang_data['weat_score'].abs().max(),
                "mean_absolute_bias": lang_data['weat_score'].abs().mean()
            }
        
        # Analyze each category
        for cat in self.results_data['weat_category_id'].unique():
            cat_data = self.results_data[self.results_data['weat_category_id'] == cat]
            
            report["category_analysis"][cat] = {
                "total_records": len(cat_data),
                "models": sorted(cat_data['model_id'].unique()),
                "languages": sorted(cat_data['language'].unique()),
                "mean_bias": cat_data['weat_score'].mean(),
                "std_bias": cat_data['weat_score'].std(),
                "max_absolute_bias": cat_data['weat_score'].abs().max(),
                "mean_absolute_bias": cat_data['weat_score'].abs().mean()
            }
        
        if save_report:
            import json
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_report_{timestamp}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"Summary report saved to: {filepath}")
        
        return report
    
    def export_filtered_data(
        self,
        model_ids: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        weat_categories: Optional[List[str]] = None,
        output_file: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Export filtered subset of the data.
        
        Args:
            model_ids (Optional[List[str]]): Models to include
            languages (Optional[List[str]]): Languages to include
            weat_categories (Optional[List[str]]): Categories to include
            output_file (Optional[str]): File to save filtered data
            
        Returns:
            pd.DataFrame: Filtered data
        """
        if self.results_data is None:
            print("No data loaded")
            return pd.DataFrame()
        
        filtered_data = self.results_data.copy()
        
        if model_ids:
            filtered_data = filtered_data[filtered_data['model_id'].isin(model_ids)]
        
        if languages:
            filtered_data = filtered_data[filtered_data['language'].isin(languages)]
        
        if weat_categories:
            filtered_data = filtered_data[filtered_data['weat_category_id'].isin(weat_categories)]
        
        if output_file:
            if not output_file.endswith('.csv'):
                output_file += '.csv'
            
            filepath = os.path.join(self.output_dir, output_file)
            filtered_data.to_csv(filepath, index=False)
            print(f"Filtered data saved to: {filepath}")
        
        return filtered_data
