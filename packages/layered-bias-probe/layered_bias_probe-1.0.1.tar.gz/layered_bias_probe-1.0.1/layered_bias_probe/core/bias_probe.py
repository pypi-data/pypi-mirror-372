"""
Main Bias Probe - Core class for performing layer-wise bias analysis.
"""

import os
import gc
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Union, Tuple
from tqdm import tqdm

from ..utils.model_manager import ModelManager
from ..utils.weathub_loader import WEATHubLoader
from ..utils.embedding_extractor import LayerEmbeddingExtractor
from ..utils.bias_quantifier import BiasQuantifier
from ..utils.weat_category import get_default_categories, get_all_weat_categories


class BiasProbe:
    """
    Main class for performing layer-wise bias analysis on language models.
    
    This class provides a high-level interface for:
    - Loading models and datasets
    - Running bias analysis across multiple layers
    - Saving results in structured format
    """
    
    def __init__(
        self,
        model_name: str,
        cache_dir: str = "./cache",
        use_quantization: bool = True,
        torch_dtype: str = "float16",
        device_map: str = "auto"
    ):
        """
        Initialize the BiasProbe.
        
        Args:
            model_name (str): HuggingFace model identifier
            cache_dir (str): Directory for caching models and datasets
            use_quantization (bool): Whether to use 4-bit quantization
            torch_dtype (str): Torch data type for model
            device_map (str): Device mapping strategy
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.use_quantization = use_quantization
        self.torch_dtype = torch_dtype
        self.device_map = device_map
        
        # Initialize components
        self.model_manager = ModelManager(cache_dir=cache_dir)
        self.weathub_loader = WEATHubLoader(cache_dir=os.path.join(cache_dir, "datasets"))
        self.bias_quantifier = BiasQuantifier()
        
        # State variables
        self.current_model = None
        self.current_tokenizer = None
        self.embedding_extractor = None
        
        # Setup cache directory
        os.makedirs(cache_dir, exist_ok=True)
    
    def load_model(self) -> bool:
        """
        Load the specified model and tokenizer.
        
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"Loading model: {self.model_name}")
        
        model, tokenizer = self.model_manager.load_model(
            model_id=self.model_name,
            use_quantization=self.use_quantization,
            torch_dtype=self.torch_dtype,
            device_map=self.device_map
        )
        
        if model is None or tokenizer is None:
            print(f"Failed to load model: {self.model_name}")
            return False
            
        self.current_model = model
        self.current_tokenizer = tokenizer
        self.embedding_extractor = LayerEmbeddingExtractor(model, tokenizer)
        
        print(f"Model loaded successfully. Layers: {self.embedding_extractor.get_layer_count()}")
        return True
    
    def unload_model(self):
        """Unload the current model to free memory."""
        if self.current_model is not None:
            self.model_manager.unload_model()
            self.current_model = None
            self.current_tokenizer = None
            self.embedding_extractor = None
    
    def analyze_bias(
        self,
        languages: List[str] = ["en"],
        weat_categories: Optional[List[str]] = None,
        output_dir: str = "./results",
        comments: str = "bias_analysis",
        save_individual_layers: bool = False
    ) -> Dict[str, Union[str, pd.DataFrame]]:
        """
        Perform comprehensive bias analysis across specified languages and WEAT categories.
        
        Args:
            languages (List[str]): Language codes to analyze
            weat_categories (Optional[List[str]]): WEAT categories to test (None for default)
            output_dir (str): Directory to save results
            comments (str): Comments to include in results
            save_individual_layers (bool): Whether to save results for each layer separately
            
        Returns:
            Dict[str, Union[str, pd.DataFrame]]: Analysis results and metadata
        """
        if not self._ensure_model_loaded():
            return {"error": "Failed to load model"}
        
        if weat_categories is None:
            weat_categories = get_default_categories('basic')
        
        print(f"Starting bias analysis for {self.model_name}")
        print(f"Languages: {languages}")
        print(f"WEAT Categories: {weat_categories}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Run analysis
        all_results = []
        num_layers = self.embedding_extractor.get_layer_count()
        
        for lang in languages:
            for weat_cat in weat_categories:
                print(f"\nProcessing: Lang='{lang}', Category='{weat_cat}'")
                
                # Get word lists from WEATHub
                word_lists = self.weathub_loader.get_word_lists(lang, weat_cat)
                if not word_lists:
                    print(f"Skipping {weat_cat} for {lang} - no data available")
                    continue
                
                # Validate word lists
                if not self._validate_word_lists(word_lists):
                    print(f"Skipping {weat_cat} for {lang} - invalid word lists")
                    continue
                
                # Analyze across all layers
                layer_results = self._analyze_category_across_layers(
                    word_lists, weat_cat, lang, comments, num_layers
                )
                all_results.extend(layer_results)
        
        if not all_results:
            return {"error": "No valid results generated"}
        
        # Create results DataFrame
        results_df = pd.DataFrame(all_results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bias_results_{self.model_name.replace('/', '_')}_{comments}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        results_df.to_csv(filepath, index=False)
        
        print(f"Results saved to: {filepath}")
        
        # Save individual layer results if requested
        if save_individual_layers:
            self._save_layer_results(results_df, output_dir, timestamp)
        
        return {
            "results": results_df,
            "output_path": filepath,
            "num_results": len(all_results),
            "languages": languages,
            "weat_categories": weat_categories,
            "model_name": self.model_name
        }
    
    def analyze_single_category(
        self,
        language: str,
        weat_category: str,
        output_dir: Optional[str] = None,
        return_layer_details: bool = False
    ) -> Dict:
        """
        Analyze bias for a single language-category pair.
        
        Args:
            language (str): Language code
            weat_category (str): WEAT category
            output_dir (Optional[str]): Directory to save results
            return_layer_details (bool): Whether to return detailed layer-by-layer results
            
        Returns:
            Dict: Analysis results
        """
        if not self._ensure_model_loaded():
            return {"error": "Failed to load model"}
        
        print(f"Analyzing {weat_category} for {language}")
        
        # Get word lists
        word_lists = self.weathub_loader.get_word_lists(language, weat_category)
        if not word_lists:
            return {"error": f"No data available for {weat_category} in {language}"}
        
        if not self._validate_word_lists(word_lists):
            return {"error": "Invalid word lists"}
        
        # Analyze across layers
        num_layers = self.embedding_extractor.get_layer_count()
        layer_results = self._analyze_category_across_layers(
            word_lists, weat_category, language, "single_analysis", num_layers
        )
        
        # Prepare results
        results = {
            "model_name": self.model_name,
            "language": language,
            "weat_category": weat_category,
            "num_layers": num_layers,
            "layer_scores": [r['weat_score'] for r in layer_results],
            "mean_score": np.mean([r['weat_score'] for r in layer_results]),
            "std_score": np.std([r['weat_score'] for r in layer_results]),
            "max_score": max([r['weat_score'] for r in layer_results]),
            "min_score": min([r['weat_score'] for r in layer_results])
        }
        
        if return_layer_details:
            results["layer_details"] = layer_results
        
        # Save if output directory specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            df = pd.DataFrame(layer_results)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"single_analysis_{self.model_name.replace('/', '_')}_{language}_{weat_category}_{timestamp}.csv"
            filepath = os.path.join(output_dir, filename)
            df.to_csv(filepath, index=False)
            results["output_path"] = filepath
        
        return results
    
    def get_model_info(self) -> Dict:
        """Get information about the current model."""
        info = self.model_manager.get_model_info(self.model_name)
        
        if self.embedding_extractor:
            info.update(self.embedding_extractor.get_embedding_info())
        
        return info
    
    def get_available_categories(self, language: str) -> List[str]:
        """Get available WEAT categories for a language."""
        return self.weathub_loader.get_available_categories(language)
    
    def get_available_languages(self, weat_category: str) -> List[str]:
        """Get available languages for a WEAT category."""
        return self.weathub_loader.get_available_languages(weat_category)
    
    def validate_language_category_pair(self, language: str, weat_category: str) -> bool:
        """Check if a language-category pair is available."""
        return self.weathub_loader.validate_language_category_pair(language, weat_category)
    
    def _ensure_model_loaded(self) -> bool:
        """Ensure that a model is loaded."""
        if self.current_model is None:
            return self.load_model()
        return True
    
    def _validate_word_lists(self, word_lists: Dict[str, List[str]]) -> bool:
        """Validate that word lists are suitable for analysis."""
        required_keys = ['targ1', 'targ2', 'attr1', 'attr2']
        
        if not all(key in word_lists for key in required_keys):
            return False
        
        # Check that all lists have words
        for key in required_keys:
            if not word_lists[key] or len(word_lists[key]) == 0:
                return False
        
        return True
    
    def _analyze_category_across_layers(
        self,
        word_lists: Dict[str, List[str]],
        weat_category: str,
        language: str,
        comments: str,
        num_layers: int
    ) -> List[Dict]:
        """Analyze a single category across all model layers."""
        layer_results = []
        
        for layer_idx in tqdm(range(num_layers), desc=f"Layer Analysis ({language}/{weat_category})"):
            try:
                # Extract embeddings for each word set
                t1_embeds = self.embedding_extractor.get_embeddings(word_lists['targ1'], layer_idx)
                t2_embeds = self.embedding_extractor.get_embeddings(word_lists['targ2'], layer_idx)
                a1_embeds = self.embedding_extractor.get_embeddings(word_lists['attr1'], layer_idx)
                a2_embeds = self.embedding_extractor.get_embeddings(word_lists['attr2'], layer_idx)
                
                # Validate embeddings
                is_valid, error_msg = self.bias_quantifier.validate_embeddings(
                    t1_embeds, t2_embeds, a1_embeds, a2_embeds
                )
                
                if not is_valid:
                    print(f"Warning: Invalid embeddings at layer {layer_idx}: {error_msg}")
                    weat_score = np.nan
                else:
                    # Calculate WEAT score
                    weat_score = self.bias_quantifier.weat_effect_size(
                        t1_embeds, t2_embeds, a1_embeds, a2_embeds
                    )
                
                # Store result
                layer_results.append({
                    'model_id': self.model_name,
                    'language': language,
                    'weat_category_id': weat_category,
                    'layer_idx': layer_idx,
                    'weat_score': weat_score,
                    'comments': comments,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"Error processing layer {layer_idx}: {e}")
                layer_results.append({
                    'model_id': self.model_name,
                    'language': language,
                    'weat_category_id': weat_category,
                    'layer_idx': layer_idx,
                    'weat_score': np.nan,
                    'comments': f"{comments}_error",
                    'timestamp': datetime.now().isoformat()
                })
        
        return layer_results
    
    def _save_layer_results(self, results_df: pd.DataFrame, output_dir: str, timestamp: str):
        """Save individual layer results as separate files."""
        layer_dir = os.path.join(output_dir, "layer_results", timestamp)
        os.makedirs(layer_dir, exist_ok=True)
        
        for layer_idx in results_df['layer_idx'].unique():
            layer_data = results_df[results_df['layer_idx'] == layer_idx]
            filename = f"layer_{layer_idx}_results.csv"
            filepath = os.path.join(layer_dir, filename)
            layer_data.to_csv(filepath, index=False)
        
        print(f"Individual layer results saved to: {layer_dir}")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.unload_model()
