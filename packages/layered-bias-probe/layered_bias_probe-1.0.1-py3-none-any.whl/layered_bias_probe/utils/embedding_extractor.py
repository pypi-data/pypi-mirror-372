"""
Layer Embedding Extractor - Extracts hidden states from transformer layers.
"""

import torch
import numpy as np
from typing import List, Union
from transformers import AutoModelForCausalLM, AutoTokenizer


class LayerEmbeddingExtractor:
    """Extracts hidden states from specific layers of transformer models."""
    
    def __init__(self, model: AutoModelForCausalLM, tokenizer: AutoTokenizer):
        """
        Initialize the embedding extractor.
        
        Args:
            model: The transformer model
            tokenizer: The corresponding tokenizer
        """
        self.model = model
        self.tokenizer = tokenizer
        self.device = model.device
        
    @torch.no_grad()
    def get_embeddings(self, words: List[str], layer_idx: int) -> np.ndarray:
        """
        Get embeddings for a list of words at a specific layer.
        
        Args:
            words (List[str]): List of words to extract embeddings for
            layer_idx (int): Layer index to extract embeddings from
            
        Returns:
            np.ndarray: Array of embeddings with shape (num_words, hidden_size)
        """
        all_embeddings = []
        
        for word in words:
            # Tokenize the word without special tokens to get clean embeddings
            inputs = self.tokenizer(
                word, 
                return_tensors="pt", 
                add_special_tokens=False
            ).to(self.device)
            
            # Get model outputs with hidden states
            outputs = self.model(**inputs, output_hidden_states=True)
            
            # Extract embedding from the specified layer
            # Average across token dimension if word is tokenized into multiple tokens
            word_embedding = outputs.hidden_states[layer_idx][0].mean(dim=0).float().cpu().numpy()
            all_embeddings.append(word_embedding)
            
        return np.array(all_embeddings)
    
    @torch.no_grad()
    def get_embeddings_batch(self, words: List[str], layer_idx: int, batch_size: int = 8) -> np.ndarray:
        """
        Get embeddings for words in batches for efficiency.
        
        Args:
            words (List[str]): List of words to extract embeddings for
            layer_idx (int): Layer index to extract embeddings from
            batch_size (int): Number of words to process at once
            
        Returns:
            np.ndarray: Array of embeddings with shape (num_words, hidden_size)
        """
        all_embeddings = []
        
        for i in range(0, len(words), batch_size):
            batch_words = words[i:i + batch_size]
            
            # Tokenize batch
            inputs = self.tokenizer(
                batch_words,
                return_tensors="pt",
                padding=True,
                truncation=True,
                add_special_tokens=False
            ).to(self.device)
            
            # Get model outputs
            outputs = self.model(**inputs, output_hidden_states=True)
            
            # Extract embeddings from specified layer
            layer_embeddings = outputs.hidden_states[layer_idx]
            
            # Average across sequence length for each word
            # Handle padding by using attention mask
            attention_mask = inputs.get('attention_mask', None)
            if attention_mask is not None:
                # Expand attention mask to match hidden states
                expanded_mask = attention_mask.unsqueeze(-1).expand(layer_embeddings.size()).float()
                # Zero out padded positions
                masked_embeddings = layer_embeddings * expanded_mask
                # Sum and divide by actual length
                summed = masked_embeddings.sum(dim=1)
                lengths = expanded_mask.sum(dim=1)
                batch_embeddings = (summed / lengths).float().cpu().numpy()
            else:
                # No padding, just average
                batch_embeddings = layer_embeddings.mean(dim=1).float().cpu().numpy()
                
            all_embeddings.append(batch_embeddings)
            
        return np.vstack(all_embeddings)
    
    def get_layer_count(self) -> int:
        """Get the number of layers in the model."""
        return self.model.config.num_hidden_layers
    
    def get_hidden_size(self) -> int:
        """Get the hidden size of the model."""
        return self.model.config.hidden_size
    
    @torch.no_grad()
    def get_all_layer_embeddings(self, words: List[str]) -> np.ndarray:
        """
        Get embeddings for words from all layers.
        
        Args:
            words (List[str]): List of words to extract embeddings for
            
        Returns:
            np.ndarray: Array with shape (num_layers, num_words, hidden_size)
        """
        all_layer_embeddings = []
        
        for layer_idx in range(self.get_layer_count()):
            layer_embeddings = self.get_embeddings(words, layer_idx)
            all_layer_embeddings.append(layer_embeddings)
            
        return np.array(all_layer_embeddings)
    
    def validate_layer_index(self, layer_idx: int) -> bool:
        """
        Validate that a layer index is valid for the model.
        
        Args:
            layer_idx (int): Layer index to validate
            
        Returns:
            bool: True if valid
        """
        return 0 <= layer_idx < self.get_layer_count()
    
    def get_embedding_info(self) -> dict:
        """
        Get information about the embedding extraction setup.
        
        Returns:
            dict: Information about the model and embedding dimensions
        """
        return {
            "model_type": self.model.config.model_type,
            "num_layers": self.get_layer_count(),
            "hidden_size": self.get_hidden_size(),
            "device": str(self.device),
            "vocab_size": self.model.config.vocab_size
        }
