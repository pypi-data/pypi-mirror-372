"""
WEATHub Loader - Loads the WEATHub dataset and provides word lists for bias analysis.
"""

import os
from typing import Dict, List, Optional
from datasets import load_dataset


class WEATHubLoader:
    """Loads the WEATHub dataset and provides word lists for WEAT analysis."""
    
    def __init__(self, dataset_id: str = "iamshnoo/WEATHub", cache_dir: Optional[str] = None):
        """
        Initialize the WEATHub loader.
        
        Args:
            dataset_id (str): HuggingFace dataset identifier
            cache_dir (Optional[str]): Cache directory for dataset
        """
        self.dataset_id = dataset_id
        self.cache_dir = cache_dir
        self.dataset = None
        self.split_mapping = {
            # Original WEAT tests
            'WEAT1': 'original_weat',
            'WEAT2': 'original_weat', 
            'WEAT6': 'original_weat',
            'WEAT7': 'original_weat',
            'WEAT8': 'original_weat',
            'WEAT9': 'original_weat',
            
            # New human biases
            'WEAT11': 'new_human_biases',
            'WEAT12': 'new_human_biases',
            'WEAT12B': 'new_human_biases',
            'WEAT13': 'new_human_biases',
            'WEAT13B': 'new_human_biases',
            'WEAT14': 'new_human_biases',
            'WEAT15': 'new_human_biases',
            
            # India-specific biases
            'WEAT16': 'india_specific_biases',
            'WEAT17': 'india_specific_biases',
            'WEAT18': 'india_specific_biases',
            'WEAT19': 'india_specific_biases',
            'WEAT20': 'india_specific_biases',
            'WEAT21': 'india_specific_biases',
            'WEAT22': 'india_specific_biases',
            'WEAT23': 'india_specific_biases',
            'WEAT24': 'india_specific_biases',
            'WEAT25': 'india_specific_biases',
            'WEAT26': 'india_specific_biases'
        }
        
        self._load_dataset()
    
    def _load_dataset(self):
        """Load the WEATHub dataset."""
        print(f"Loading WEATHub dataset from '{self.dataset_id}'...")
        try:
            self.dataset = load_dataset(
                self.dataset_id, 
                cache_dir=self.cache_dir,
                trust_remote_code=True
            )
            print("WEATHub dataset loaded successfully.")
            print(f"Available splits: {list(self.dataset.keys())}")
        except Exception as e:
            print(f"ERROR: Failed to load WEATHub dataset. Exception: {e}")
            self.dataset = None
    
    def get_word_lists(self, language_code: str, weat_category_id: str) -> Optional[Dict[str, List[str]]]:
        """
        Retrieve target and attribute word lists for a given language and WEAT category.
        
        Args:
            language_code (str): Language code (e.g., 'en', 'hi', 'bn')
            weat_category_id (str): WEAT category identifier (e.g., 'WEAT1')
            
        Returns:
            Optional[Dict[str, List[str]]]: Dictionary with keys 'targ1', 'targ2', 'attr1', 'attr2'
        """
        if not self.dataset:
            print("Dataset not loaded. Please check initialization.")
            return None
            
        split_name = self.split_mapping.get(weat_category_id)
        if not split_name:
            print(f"Warning: Category '{weat_category_id}' not found in mapping.")
            return None
            
        try:
            # Filter dataset for the specific language and WEAT category
            filtered = self.dataset[split_name].filter(
                lambda x: x['language'] == language_code and x['weat'] == weat_category_id
            )
            
            if len(filtered) > 0:
                example = filtered[0]
                return {
                    'targ1': example['targ1.examples'],
                    'targ2': example['targ2.examples'], 
                    'attr1': example['attr1.examples'],
                    'attr2': example['attr2.examples']
                }
            else:
                print(f"Warning: No data found for language '{language_code}' and category '{weat_category_id}'.")
                return None
                
        except Exception as e:
            print(f"Error filtering data for '{weat_category_id}' in language '{language_code}': {e}")
            return None
    
    def get_available_languages(self, weat_category_id: str) -> List[str]:
        """
        Get available languages for a given WEAT category.
        
        Args:
            weat_category_id (str): WEAT category identifier
            
        Returns:
            List[str]: List of available language codes
        """
        if not self.dataset:
            return []
            
        split_name = self.split_mapping.get(weat_category_id)
        if not split_name:
            return []
            
        try:
            split_data = self.dataset[split_name]
            filtered = split_data.filter(lambda x: x['weat'] == weat_category_id)
            languages = list(set(example['language'] for example in filtered))
            return sorted(languages)
        except Exception as e:
            print(f"Error getting languages for '{weat_category_id}': {e}")
            return []
    
    def get_available_categories(self, language_code: str) -> List[str]:
        """
        Get available WEAT categories for a given language.
        
        Args:
            language_code (str): Language code
            
        Returns:
            List[str]: List of available WEAT categories
        """
        if not self.dataset:
            return []
            
        categories = []
        
        for split_name in self.dataset.keys():
            try:
                split_data = self.dataset[split_name]
                filtered = split_data.filter(lambda x: x['language'] == language_code)
                split_categories = list(set(example['weat'] for example in filtered))
                categories.extend(split_categories)
            except Exception as e:
                print(f"Error processing split '{split_name}': {e}")
                continue
                
        return sorted(list(set(categories)))
    
    def validate_language_category_pair(self, language_code: str, weat_category_id: str) -> bool:
        """
        Check if a language-category pair is available in the dataset.
        
        Args:
            language_code (str): Language code
            weat_category_id (str): WEAT category identifier
            
        Returns:
            bool: True if the pair is available
        """
        word_lists = self.get_word_lists(language_code, weat_category_id)
        return word_lists is not None and all(
            isinstance(word_list, list) and len(word_list) > 0 
            for word_list in word_lists.values()
        )
    
    def get_dataset_info(self) -> Dict:
        """
        Get information about the loaded dataset.
        
        Returns:
            Dict: Dataset information
        """
        if not self.dataset:
            return {"status": "not_loaded"}
            
        info = {
            "dataset_id": self.dataset_id,
            "splits": list(self.dataset.keys()),
            "total_examples": sum(len(split) for split in self.dataset.values()),
            "split_mapping": self.split_mapping
        }
        
        # Add split-specific information
        for split_name in self.dataset.keys():
            try:
                split_data = self.dataset[split_name]
                languages = list(set(example['language'] for example in split_data))
                categories = list(set(example['weat'] for example in split_data))
                
                info[f"{split_name}_info"] = {
                    "num_examples": len(split_data),
                    "languages": sorted(languages),
                    "categories": sorted(categories)
                }
            except Exception as e:
                info[f"{split_name}_info"] = {"error": str(e)}
                
        return info
    
    def reload_dataset(self):
        """Reload the dataset (useful if there were loading issues)."""
        self._load_dataset()
