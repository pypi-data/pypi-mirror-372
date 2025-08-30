"""
Batch Processor - Handles batch processing of multiple models for bias analysis.
"""

import os
import time
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from .bias_probe import BiasProbe
from ..utils.model_manager import get_supported_models
from ..utils.weat_category import get_default_categories


class BatchProcessor:
    """
    Processes multiple models for bias analysis in batch mode.
    
    This class provides efficient batch processing capabilities for:
    - Multiple model analysis
    - Parallel processing where possible
    - Consolidated result reporting
    - Progress tracking
    """
    
    def __init__(
        self,
        models: List[str],
        cache_dir: str = "./cache",
        max_workers: int = 1,  # Keep at 1 for GPU memory management
        use_quantization: bool = True
    ):
        """
        Initialize the BatchProcessor.
        
        Args:
            models (List[str]): List of model identifiers to process
            cache_dir (str): Directory for caching
            max_workers (int): Number of parallel workers (keep at 1 for GPU)
            use_quantization (bool): Whether to use quantization
        """
        self.models = models
        self.cache_dir = cache_dir
        self.max_workers = max_workers
        self.use_quantization = use_quantization
        
        # Validate models
        self.supported_models = get_supported_models()
        self._validate_models()
        
        # Setup cache directory
        os.makedirs(cache_dir, exist_ok=True)
    
    def _validate_models(self):
        """Validate that all specified models are supported."""
        unsupported = [model for model in self.models if model not in self.supported_models]
        if unsupported:
            print(f"Warning: The following models are not in the officially supported list: {unsupported}")
            print("They will still be processed, but may have compatibility issues.")
    
    def run_bias_analysis(
        self,
        languages: List[str] = ["en"],
        weat_categories: Optional[List[str]] = None,
        output_dir: str = "./batch_results",
        comments: str = "batch_analysis",
        save_individual_results: bool = True,
        continue_on_error: bool = True
    ) -> Dict:
        """
        Run bias analysis on all models in batch.
        
        Args:
            languages (List[str]): Languages to analyze
            weat_categories (Optional[List[str]]): WEAT categories to test
            output_dir (str): Directory to save results
            comments (str): Comments for the analysis
            save_individual_results (bool): Whether to save results for each model
            continue_on_error (bool): Whether to continue if one model fails
            
        Returns:
            Dict: Batch processing results and metadata
        """
        if weat_categories is None:
            weat_categories = get_default_categories('basic')
        
        print(f"Starting batch bias analysis for {len(self.models)} models")
        print(f"Models: {self.models}")
        print(f"Languages: {languages}")
        print(f"WEAT Categories: {weat_categories}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Track results
        all_results = []
        model_results = {}
        failed_models = []
        
        # Process models sequentially (better for GPU memory management)
        for model_name in tqdm(self.models, desc="Processing Models"):
            try:
                print(f"\n{'='*60}")
                print(f"Processing Model: {model_name}")
                print(f"{'='*60}")
                
                start_time = time.time()
                
                # Initialize probe for this model
                probe = BiasProbe(
                    model_name=model_name,
                    cache_dir=self.cache_dir,
                    use_quantization=self.use_quantization
                )
                
                # Run analysis
                model_result = probe.analyze_bias(
                    languages=languages,
                    weat_categories=weat_categories,
                    output_dir=os.path.join(output_dir, "individual_models") if save_individual_results else output_dir,
                    comments=f"{comments}_{model_name.replace('/', '_')}"
                )
                
                # Clean up
                probe.unload_model()
                del probe
                
                processing_time = time.time() - start_time
                
                if "error" not in model_result:
                    # Add processing metadata
                    model_result.update({
                        "processing_time": processing_time,
                        "status": "success"
                    })
                    
                    # Store results
                    model_results[model_name] = model_result
                    if isinstance(model_result.get("results"), pd.DataFrame):
                        all_results.append(model_result["results"])
                    
                    print(f"✅ Completed {model_name} in {processing_time:.2f}s")
                else:
                    failed_models.append({
                        "model": model_name,
                        "error": model_result["error"],
                        "processing_time": processing_time
                    })
                    print(f"❌ Failed {model_name}: {model_result['error']}")
                
            except Exception as e:
                error_msg = str(e)
                failed_models.append({
                    "model": model_name,
                    "error": error_msg,
                    "processing_time": time.time() - start_time if 'start_time' in locals() else 0
                })
                print(f"❌ Exception processing {model_name}: {error_msg}")
                
                if not continue_on_error:
                    break
        
        # Consolidate results
        batch_results = self._consolidate_results(
            all_results, model_results, failed_models, 
            output_dir, languages, weat_categories, comments
        )
        
        print(f"\n{'='*60}")
        print("BATCH PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total Models: {len(self.models)}")
        print(f"Successful: {len(model_results)}")
        print(f"Failed: {len(failed_models)}")
        print(f"Results saved to: {output_dir}")
        
        return batch_results
    
    def compare_models(
        self,
        languages: List[str] = ["en"],
        weat_categories: Optional[List[str]] = None,
        output_dir: str = "./model_comparison",
        metric: str = "mean_absolute_bias"
    ) -> Dict:
        """
        Compare bias across multiple models.
        
        Args:
            languages (List[str]): Languages to compare
            weat_categories (Optional[List[str]]): WEAT categories to compare
            output_dir (str): Directory to save comparison results
            metric (str): Metric for comparison
            
        Returns:
            Dict: Model comparison results
        """
        # Run batch analysis
        batch_results = self.run_bias_analysis(
            languages=languages,
            weat_categories=weat_categories,
            output_dir=output_dir,
            comments="model_comparison"
        )
        
        if not batch_results.get("consolidated_results"):
            return {"error": "No results available for comparison"}
        
        # Load consolidated results
        df = batch_results["consolidated_results"]
        
        # Create comparison metrics
        comparison_data = []
        
        for model in df['model_id'].unique():
            model_data = df[df['model_id'] == model]
            
            for lang in languages:
                lang_data = model_data[model_data['language'] == lang]
                
                if len(lang_data) > 0:
                    metrics = {
                        'model': model,
                        'language': lang,
                        'mean_bias': lang_data['weat_score'].mean(),
                        'std_bias': lang_data['weat_score'].std(),
                        'max_bias': lang_data['weat_score'].abs().max(),
                        'mean_absolute_bias': lang_data['weat_score'].abs().mean(),
                        'num_categories': len(lang_data['weat_category_id'].unique()),
                        'num_layers': len(lang_data['layer_idx'].unique())
                    }
                    comparison_data.append(metrics)
        
        # Save comparison results
        comparison_df = pd.DataFrame(comparison_data)
        comparison_file = os.path.join(output_dir, "model_comparison_summary.csv")
        comparison_df.to_csv(comparison_file, index=False)
        
        # Create rankings
        rankings = {}
        for lang in languages:
            lang_comparison = comparison_df[comparison_df['language'] == lang]
            rankings[lang] = lang_comparison.sort_values(metric).to_dict('records')
        
        print(f"Model comparison saved to: {comparison_file}")
        
        return {
            "comparison_data": comparison_df,
            "rankings": rankings,
            "comparison_file": comparison_file,
            "metric_used": metric
        }
    
    def get_processing_summary(self) -> Dict:
        """Get summary of models to be processed."""
        return {
            "total_models": len(self.models),
            "models": self.models,
            "supported_models": [m for m in self.models if m in self.supported_models],
            "unsupported_models": [m for m in self.models if m not in self.supported_models],
            "cache_dir": self.cache_dir,
            "max_workers": self.max_workers,
            "use_quantization": self.use_quantization
        }
    
    def _consolidate_results(
        self,
        all_results: List[pd.DataFrame],
        model_results: Dict,
        failed_models: List[Dict],
        output_dir: str,
        languages: List[str],
        weat_categories: List[str],
        comments: str
    ) -> Dict:
        """Consolidate results from all models."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Combine all successful results
        consolidated_df = None
        if all_results:
            consolidated_df = pd.concat(all_results, ignore_index=True)
            
            # Save consolidated results
            consolidated_file = os.path.join(
                output_dir, 
                f"consolidated_bias_results_{comments}_{timestamp}.csv"
            )
            consolidated_df.to_csv(consolidated_file, index=False)
            print(f"Consolidated results saved to: {consolidated_file}")
        
        # Save batch summary
        summary = {
            "batch_info": {
                "timestamp": timestamp,
                "total_models": len(self.models),
                "successful_models": len(model_results),
                "failed_models": len(failed_models),
                "languages": languages,
                "weat_categories": weat_categories,
                "comments": comments
            },
            "successful_models": list(model_results.keys()),
            "failed_models": failed_models,
            "processing_times": {
                model: result.get("processing_time", 0) 
                for model, result in model_results.items()
            }
        }
        
        summary_file = os.path.join(output_dir, f"batch_summary_{timestamp}.json")
        import json
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        return {
            "consolidated_results": consolidated_df,
            "model_results": model_results,
            "failed_models": failed_models,
            "summary": summary,
            "summary_file": summary_file,
            "consolidated_file": consolidated_file if consolidated_df is not None else None
        }
