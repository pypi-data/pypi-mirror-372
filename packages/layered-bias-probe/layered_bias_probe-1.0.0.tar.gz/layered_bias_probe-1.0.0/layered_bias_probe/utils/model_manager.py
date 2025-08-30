"""
Model Manager - Handles loading and management of language models for bias analysis.
"""

import os
import gc
import torch
from typing import Optional, Tuple, Union
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)


class ModelManager:
    """Manages the lifecycle of language models to optimize memory usage."""
    
    def __init__(self, cache_dir: str = "./cache"):
        """
        Initialize the ModelManager.
        
        Args:
            cache_dir (str): Directory to cache downloaded models
        """
        self.cache_dir = cache_dir
        self.model = None
        self.tokenizer = None
        self.current_model_id = None
        self._setup_cache_dir()
        
    def _setup_cache_dir(self):
        """Create cache directory if it doesn't exist."""
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def load_model(
        self, 
        model_id: str, 
        model_repo: str = 'hf',
        use_quantization: bool = True,
        torch_dtype: str = "float16",
        device_map: str = "auto"
    ) -> Tuple[Optional[AutoModelForCausalLM], Optional[AutoTokenizer]]:
        """
        Load model and tokenizer from either Hugging Face or a local path.
        
        Args:
            model_id (str): Model identifier or name
            model_repo (str): 'hf' for Hugging Face or local path
            use_quantization (bool): Whether to use 4-bit quantization
            torch_dtype (str): Torch data type to use
            device_map (str): Device mapping strategy
            
        Returns:
            Tuple[Optional[AutoModelForCausalLM], Optional[AutoTokenizer]]: 
                Loaded model and tokenizer, or (None, None) if failed
        """
        if self.current_model_id == model_id and self.model is not None:
            print(f"Model '{model_id}' already loaded.")
            return self.model, self.tokenizer

        print(f"Loading model: {model_id} from {model_repo}")
        load_path = model_id if model_repo == 'hf' else model_repo

        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                load_path, 
                cache_dir=self.cache_dir
            )
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Setup quantization config if requested
            quantization_config = None
            if use_quantization:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=getattr(torch, torch_dtype)
                )

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                load_path,
                torch_dtype=getattr(torch, torch_dtype),
                device_map=device_map,
                quantization_config=quantization_config,
                cache_dir=self.cache_dir
            )
            
            self.current_model_id = model_id
            print(f"Model '{model_id}' loaded successfully.")
            return self.model, self.tokenizer

        except Exception as e:
            print(f"ERROR: Failed to load model '{model_id}'. Exception: {e}")
            return None, None

    def unload_model(self):
        """Unloads the current model and clears GPU cache."""
        if self.model:
            print(f"Unloading model: {self.current_model_id}...")
            del self.model
            del self.tokenizer
            self.model, self.tokenizer, self.current_model_id = None, None, None
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print("Model unloaded and memory cleared.")
            
    def get_model_info(self, model_id: str) -> dict:
        """
        Get information about a model without loading it.
        
        Args:
            model_id (str): Model identifier
            
        Returns:
            dict: Model information
        """
        try:
            from transformers import AutoConfig
            config = AutoConfig.from_pretrained(model_id, cache_dir=self.cache_dir)
            
            return {
                "model_id": model_id,
                "model_type": config.model_type,
                "num_layers": getattr(config, 'num_hidden_layers', 'Unknown'),
                "hidden_size": getattr(config, 'hidden_size', 'Unknown'),
                "vocab_size": getattr(config, 'vocab_size', 'Unknown'),
                "max_position_embeddings": getattr(config, 'max_position_embeddings', 'Unknown'),
            }
        except Exception as e:
            return {"model_id": model_id, "error": str(e)}
    
    def is_model_loaded(self) -> bool:
        """Check if a model is currently loaded."""
        return self.model is not None
    
    def get_current_model_id(self) -> Optional[str]:
        """Get the ID of the currently loaded model."""
        return self.current_model_id
    
    def __del__(self):
        """Cleanup when the object is destroyed."""
        self.unload_model()


# Supported model configurations
SUPPORTED_MODELS = {
    "apple/OpenELM-270M": {
        "name": "OpenELM-270M",
        "size": "270M",
        "organization": "Apple"
    },
    "facebook/MobileLLM-125M": {
        "name": "MobileLLM-125M", 
        "size": "125M",
        "organization": "Facebook"
    },
    "cerebras/Cerebras-GPT-111M": {
        "name": "Cerebras-GPT-111M",
        "size": "111M", 
        "organization": "Cerebras"
    },
    "EleutherAI/pythia-70m": {
        "name": "Pythia-70M",
        "size": "70M",
        "organization": "EleutherAI"
    },
    "meta-llama/Llama-3.2-1B": {
        "name": "Llama-3.2-1B",
        "size": "1B",
        "organization": "Meta"
    },
    "Qwen/Qwen2.5-1.5B": {
        "name": "Qwen2.5-1.5B",
        "size": "1.5B", 
        "organization": "Alibaba"
    },
    "google/gemma-2-2b": {
        "name": "Gemma-2-2B",
        "size": "2B",
        "organization": "Google"
    },
    "ibm-granite/granite-3.3-2b-base": {
        "name": "Granite-3.3-2B",
        "size": "2B",
        "organization": "IBM"
    },
    "HuggingFaceTB/SmolLM2-135M": {
        "name": "SmolLM2-135M",
        "size": "135M",
        "organization": "HuggingFace"
    }
}


def get_supported_models() -> dict:
    """Get the dictionary of supported models."""
    return SUPPORTED_MODELS


def is_model_supported(model_id: str) -> bool:
    """Check if a model is officially supported."""
    return model_id in SUPPORTED_MODELS
