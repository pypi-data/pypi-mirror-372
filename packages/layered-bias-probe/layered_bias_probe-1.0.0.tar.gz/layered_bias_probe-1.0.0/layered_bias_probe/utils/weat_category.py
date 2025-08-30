"""
WEAT Category - Defines and manages Word Embedding Association Test categories.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class WEATCategory:
    """
    Represents a Word Embedding Association Test (WEAT) category.
    
    A WEAT test consists of:
    - Two target word sets (target1, target2) 
    - Two attribute word sets (attribute1, attribute2)
    - A language specification
    """
    name: str
    target1: List[str]
    target2: List[str] 
    attribute1: List[str]
    attribute2: List[str]
    language: str
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate the WEAT category after initialization."""
        self.validate()
    
    def validate(self) -> bool:
        """
        Validate that the WEAT category has all required components.
        
        Returns:
            bool: True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if not self.name:
            raise ValueError("WEAT category name cannot be empty")
            
        if not all([self.target1, self.target2, self.attribute1, self.attribute2]):
            raise ValueError("All word lists must be non-empty")
            
        if not self.language:
            raise ValueError("Language must be specified")
            
        # Check for minimum word count
        min_words = 3
        if any(len(word_list) < min_words for word_list in 
               [self.target1, self.target2, self.attribute1, self.attribute2]):
            raise ValueError(f"Each word list must contain at least {min_words} words")
            
        return True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            'name': self.name,
            'targ1': self.target1,
            'targ2': self.target2, 
            'attr1': self.attribute1,
            'attr2': self.attribute2,
            'language': self.language,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WEATCategory':
        """Create WEATCategory from dictionary."""
        return cls(
            name=data['name'],
            target1=data.get('targ1', data.get('target1', [])),
            target2=data.get('targ2', data.get('target2', [])),
            attribute1=data.get('attr1', data.get('attribute1', [])),
            attribute2=data.get('attr2', data.get('attribute2', [])),
            language=data['language'],
            description=data.get('description')
        )


# Predefined WEAT categories mapping
WEAT_CATEGORIES_INFO = {
    # Original WEAT tests
    'WEAT1': {
        'description': 'Flowers vs. Insects with Pleasant vs. Unpleasant',
        'targets': ['Flowers', 'Insects'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Valence',
        'split': 'original_weat'
    },
    'WEAT2': {
        'description': 'Instruments vs. Weapons with Pleasant vs. Unpleasant', 
        'targets': ['Instruments', 'Weapons'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Valence',
        'split': 'original_weat'
    },
    'WEAT6': {
        'description': 'Career vs. Family with Male vs. Female Names',
        'targets': ['Career', 'Family'],
        'attributes': ['Male Names', 'Female Names'], 
        'bias_type': 'Gender-Profession',
        'split': 'original_weat'
    },
    'WEAT7': {
        'description': 'Math vs. Arts with Male vs. Female Terms',
        'targets': ['Math', 'Arts'],
        'attributes': ['Male Terms', 'Female Terms'],
        'bias_type': 'Gender-Academic',
        'split': 'original_weat'
    },
    'WEAT8': {
        'description': 'Science vs. Arts with Male vs. Female Terms',
        'targets': ['Science', 'Arts'], 
        'attributes': ['Male Terms', 'Female Terms'],
        'bias_type': 'Gender-Academic',
        'split': 'original_weat'
    },
    'WEAT9': {
        'description': 'Mental vs. Physical Disease with Temporary vs. Permanent',
        'targets': ['Mental Disease', 'Physical Disease'],
        'attributes': ['Temporary', 'Permanent'],
        'bias_type': 'Health',
        'split': 'original_weat'
    },
    
    # New human biases
    'WEAT11': {
        'description': 'Young vs. Old Names with Pleasant vs. Unpleasant',
        'targets': ['Young Names', 'Old Names'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Age',
        'split': 'new_human_biases'
    },
    'WEAT12': {
        'description': 'Disability vs. No Disability with Pleasant vs. Unpleasant',
        'targets': ['Disability', 'No Disability'],
        'attributes': ['Pleasant', 'Unpleasant'], 
        'bias_type': 'Disability',
        'split': 'new_human_biases'
    },
    'WEAT12B': {
        'description': 'Disability vs. No Disability with Pleasant vs. Unpleasant (Version B)',
        'targets': ['Disability', 'No Disability'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Disability',
        'split': 'new_human_biases'
    },
    'WEAT13': {
        'description': 'Homosexual vs. Heterosexual with Pleasant vs. Unpleasant',
        'targets': ['Homosexual', 'Heterosexual'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Sexual Orientation',
        'split': 'new_human_biases'
    },
    'WEAT13B': {
        'description': 'Homosexual vs. Heterosexual with Pleasant vs. Unpleasant (Version B)',
        'targets': ['Homosexual', 'Heterosexual'], 
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Sexual Orientation',
        'split': 'new_human_biases'
    },
    'WEAT14': {
        'description': 'Black vs. White Names with Pleasant vs. Unpleasant',
        'targets': ['Black Names', 'White Names'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Race',
        'split': 'new_human_biases'
    },
    'WEAT15': {
        'description': 'Fat vs. Thin with Pleasant vs. Unpleasant',
        'targets': ['Fat', 'Thin'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Body Size',
        'split': 'new_human_biases'
    },
    
    # India-specific biases
    'WEAT16': {
        'description': 'Upper Caste vs. Lower Caste Names with Pleasant vs. Unpleasant',
        'targets': ['Upper Caste Names', 'Lower Caste Names'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Caste',
        'split': 'india_specific_biases'
    },
    'WEAT17': {
        'description': 'Hindu vs. Muslim Names with Pleasant vs. Unpleasant',
        'targets': ['Hindu Names', 'Muslim Names'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Religion',
        'split': 'india_specific_biases'
    },
    'WEAT18': {
        'description': 'North Indian vs. South Indian Names with Pleasant vs. Unpleasant',
        'targets': ['North Indian Names', 'South Indian Names'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Regional',
        'split': 'india_specific_biases'
    },
    'WEAT19': {
        'description': 'Urban vs. Rural Names with Pleasant vs. Unpleasant',
        'targets': ['Urban Names', 'Rural Names'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Geography',
        'split': 'india_specific_biases'
    },
    'WEAT20': {
        'description': 'Hindu vs. Sikh Names with Pleasant vs. Unpleasant',
        'targets': ['Hindu Names', 'Sikh Names'], 
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Religion',
        'split': 'india_specific_biases'
    },
    'WEAT21': {
        'description': 'Upper Caste vs. Muslim Names with Pleasant vs. Unpleasant',
        'targets': ['Upper Caste Names', 'Muslim Names'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Caste-Religion',
        'split': 'india_specific_biases'
    },
    'WEAT22': {
        'description': 'Hindu vs. Christian Names with Pleasant vs. Unpleasant',
        'targets': ['Hindu Names', 'Christian Names'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Religion',
        'split': 'india_specific_biases'
    },
    'WEAT23': {
        'description': 'Bengali vs. Punjabi Names with Pleasant vs. Unpleasant',
        'targets': ['Bengali Names', 'Punjabi Names'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Regional-Linguistic',
        'split': 'india_specific_biases'
    },
    'WEAT24': {
        'description': 'Marathi vs. Tamil Names with Pleasant vs. Unpleasant',
        'targets': ['Marathi Names', 'Tamil Names'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Regional-Linguistic', 
        'split': 'india_specific_biases'
    },
    'WEAT25': {
        'description': 'Upper Caste vs. Christian Names with Pleasant vs. Unpleasant',
        'targets': ['Upper Caste Names', 'Christian Names'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Caste-Religion',
        'split': 'india_specific_biases'
    },
    'WEAT26': {
        'description': 'Hindi vs. English Names with Pleasant vs. Unpleasant',
        'targets': ['Hindi Names', 'English Names'],
        'attributes': ['Pleasant', 'Unpleasant'],
        'bias_type': 'Linguistic',
        'split': 'india_specific_biases'
    }
}


def get_weat_categories_by_split(split_name: str) -> List[str]:
    """Get all WEAT categories for a given split."""
    return [cat for cat, info in WEAT_CATEGORIES_INFO.items() 
            if info['split'] == split_name]


def get_weat_categories_by_bias_type(bias_type: str) -> List[str]:
    """Get all WEAT categories for a given bias type."""
    return [cat for cat, info in WEAT_CATEGORIES_INFO.items() 
            if info['bias_type'] == bias_type]


def get_all_weat_categories() -> List[str]:
    """Get all available WEAT categories."""
    return list(WEAT_CATEGORIES_INFO.keys())


def get_weat_category_info(category: str) -> Optional[Dict]:
    """Get information about a specific WEAT category."""
    return WEAT_CATEGORIES_INFO.get(category)


def get_split_mapping() -> Dict[str, str]:
    """Get mapping of WEAT categories to their dataset splits."""
    return {cat: info['split'] for cat, info in WEAT_CATEGORIES_INFO.items()}


# Default WEAT categories for different use cases
DEFAULT_WEAT_CATEGORIES = {
    'basic': ['WEAT1', 'WEAT2', 'WEAT6'],
    'gender': ['WEAT6', 'WEAT7', 'WEAT8'],
    'comprehensive': ['WEAT1', 'WEAT2', 'WEAT6', 'WEAT7', 'WEAT8', 'WEAT9'],
    'india_specific': ['WEAT16', 'WEAT17', 'WEAT18', 'WEAT19', 'WEAT20'],
    'all_original': get_weat_categories_by_split('original_weat'),
    'all_new': get_weat_categories_by_split('new_human_biases'),
    'all_india': get_weat_categories_by_split('india_specific_biases'),
}


def get_default_categories(category_set: str = 'basic') -> List[str]:
    """Get a predefined set of WEAT categories."""
    return DEFAULT_WEAT_CATEGORIES.get(category_set, DEFAULT_WEAT_CATEGORIES['basic'])
