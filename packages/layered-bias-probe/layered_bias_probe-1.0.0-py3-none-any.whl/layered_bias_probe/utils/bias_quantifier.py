"""
Bias Quantifier - Calculates bias scores using WEAT methodology.
"""

import numpy as np
from typing import List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity


class BiasQuantifier:
    """Calculates bias scores using Word Embedding Association Test (WEAT) methodology."""
    
    def __init__(self):
        """Initialize the bias quantifier."""
        pass
    
    def _s(self, w: np.ndarray, A: np.ndarray, B: np.ndarray) -> float:
        """
        Helper function for WEAT: computes the association of word w with attribute sets A and B.
        
        Args:
            w (np.ndarray): Word embedding
            A (np.ndarray): First attribute set embeddings 
            B (np.ndarray): Second attribute set embeddings
            
        Returns:
            float: Association score (mean cosine similarity with A minus mean with B)
        """
        mean_cos_A = np.mean([cosine_similarity([w], [a])[0][0] for a in A])
        mean_cos_B = np.mean([cosine_similarity([w], [b])[0][0] for b in B])
        return mean_cos_A - mean_cos_B
    
    def weat_effect_size(
        self, 
        T1_embeds: np.ndarray, 
        T2_embeds: np.ndarray, 
        A1_embeds: np.ndarray, 
        A2_embeds: np.ndarray
    ) -> float:
        """
        Calculate the Word Embedding Association Test (WEAT) effect size (d-score).
        
        The WEAT effect size measures the differential association between two target
        word sets and two attribute word sets, normalized by the standard deviation.
        
        Args:
            T1_embeds (np.ndarray): Target set 1 embeddings
            T2_embeds (np.ndarray): Target set 2 embeddings  
            A1_embeds (np.ndarray): Attribute set 1 embeddings
            A2_embeds (np.ndarray): Attribute set 2 embeddings
            
        Returns:
            float: WEAT effect size (d-score)
        """
        # Calculate mean association for each target set
        mean_T1 = np.mean([self._s(t, A1_embeds, A2_embeds) for t in T1_embeds])
        mean_T2 = np.mean([self._s(t, A1_embeds, A2_embeds) for t in T2_embeds])
        
        # Calculate standard deviation across all target words
        all_s = [self._s(t, A1_embeds, A2_embeds) for t in np.concatenate((T1_embeds, T2_embeds))]
        std_dev = np.std(all_s, ddof=1)
        
        # Return effect size (Cohen's d)
        return (mean_T1 - mean_T2) / std_dev if std_dev > 0 else 0.0
    
    def weat_p_value(
        self,
        T1_embeds: np.ndarray,
        T2_embeds: np.ndarray, 
        A1_embeds: np.ndarray,
        A2_embeds: np.ndarray,
        num_permutations: int = 1000
    ) -> float:
        """
        Calculate p-value for WEAT test using permutation testing.
        
        Args:
            T1_embeds (np.ndarray): Target set 1 embeddings
            T2_embeds (np.ndarray): Target set 2 embeddings
            A1_embeds (np.ndarray): Attribute set 1 embeddings  
            A2_embeds (np.ndarray): Attribute set 2 embeddings
            num_permutations (int): Number of permutations for statistical test
            
        Returns:
            float: p-value
        """
        # Calculate original test statistic
        original_stat = self._weat_test_statistic(T1_embeds, T2_embeds, A1_embeds, A2_embeds)
        
        # Combine target sets for permutation
        all_targets = np.concatenate((T1_embeds, T2_embeds))
        n_T1 = len(T1_embeds)
        
        # Count permutations with test statistic >= original
        extreme_count = 0
        
        for _ in range(num_permutations):
            # Randomly permute targets
            np.random.shuffle(all_targets)
            perm_T1 = all_targets[:n_T1]
            perm_T2 = all_targets[n_T1:]
            
            # Calculate test statistic for permutation
            perm_stat = self._weat_test_statistic(perm_T1, perm_T2, A1_embeds, A2_embeds)
            
            if perm_stat >= original_stat:
                extreme_count += 1
                
        return extreme_count / num_permutations
    
    def _weat_test_statistic(
        self,
        T1_embeds: np.ndarray,
        T2_embeds: np.ndarray,
        A1_embeds: np.ndarray, 
        A2_embeds: np.ndarray
    ) -> float:
        """
        Calculate the WEAT test statistic.
        
        Args:
            T1_embeds (np.ndarray): Target set 1 embeddings
            T2_embeds (np.ndarray): Target set 2 embeddings
            A1_embeds (np.ndarray): Attribute set 1 embeddings
            A2_embeds (np.ndarray): Attribute set 2 embeddings
            
        Returns:
            float: Test statistic
        """
        sum_T1 = sum(self._s(t, A1_embeds, A2_embeds) for t in T1_embeds)
        sum_T2 = sum(self._s(t, A1_embeds, A2_embeds) for t in T2_embeds)
        return sum_T1 - sum_T2
    
    def calculate_individual_associations(
        self,
        target_embeds: np.ndarray,
        A1_embeds: np.ndarray,
        A2_embeds: np.ndarray
    ) -> List[float]:
        """
        Calculate individual association scores for each target word.
        
        Args:
            target_embeds (np.ndarray): Target word embeddings
            A1_embeds (np.ndarray): Attribute set 1 embeddings
            A2_embeds (np.ndarray): Attribute set 2 embeddings
            
        Returns:
            List[float]: Individual association scores
        """
        return [self._s(t, A1_embeds, A2_embeds) for t in target_embeds]
    
    def calculate_cosine_similarities(
        self,
        embeddings1: np.ndarray, 
        embeddings2: np.ndarray
    ) -> np.ndarray:
        """
        Calculate pairwise cosine similarities between two sets of embeddings.
        
        Args:
            embeddings1 (np.ndarray): First set of embeddings
            embeddings2 (np.ndarray): Second set of embeddings
            
        Returns:
            np.ndarray: Cosine similarity matrix
        """
        return cosine_similarity(embeddings1, embeddings2)
    
    def analyze_bias_direction(
        self,
        T1_embeds: np.ndarray,
        T2_embeds: np.ndarray, 
        A1_embeds: np.ndarray,
        A2_embeds: np.ndarray
    ) -> dict:
        """
        Analyze the direction and magnitude of bias.
        
        Args:
            T1_embeds (np.ndarray): Target set 1 embeddings
            T2_embeds (np.ndarray): Target set 2 embeddings
            A1_embeds (np.ndarray): Attribute set 1 embeddings
            A2_embeds (np.ndarray): Attribute set 2 embeddings
            
        Returns:
            dict: Analysis results including effect size, direction, and individual scores
        """
        effect_size = self.weat_effect_size(T1_embeds, T2_embeds, A1_embeds, A2_embeds)
        
        # Calculate individual association scores
        T1_associations = self.calculate_individual_associations(T1_embeds, A1_embeds, A2_embeds)
        T2_associations = self.calculate_individual_associations(T2_embeds, A1_embeds, A2_embeds)
        
        return {
            'effect_size': effect_size,
            'bias_direction': 'T1->A1' if effect_size > 0 else 'T1->A2',
            'T1_mean_association': np.mean(T1_associations),
            'T2_mean_association': np.mean(T2_associations),
            'T1_associations': T1_associations,
            'T2_associations': T2_associations,
            'magnitude': abs(effect_size),
            'strength': self._classify_effect_size(abs(effect_size))
        }
    
    def _classify_effect_size(self, abs_effect_size: float) -> str:
        """
        Classify the strength of the effect size according to Cohen's conventions.
        
        Args:
            abs_effect_size (float): Absolute value of effect size
            
        Returns:
            str: Classification of effect strength
        """
        if abs_effect_size < 0.2:
            return 'negligible'
        elif abs_effect_size < 0.5:
            return 'small'
        elif abs_effect_size < 0.8:
            return 'medium'
        else:
            return 'large'
    
    def validate_embeddings(
        self,
        T1_embeds: np.ndarray,
        T2_embeds: np.ndarray,
        A1_embeds: np.ndarray, 
        A2_embeds: np.ndarray
    ) -> Tuple[bool, str]:
        """
        Validate that embeddings are suitable for WEAT analysis.
        
        Args:
            T1_embeds (np.ndarray): Target set 1 embeddings
            T2_embeds (np.ndarray): Target set 2 embeddings
            A1_embeds (np.ndarray): Attribute set 1 embeddings
            A2_embeds (np.ndarray): Attribute set 2 embeddings
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        embeddings = [T1_embeds, T2_embeds, A1_embeds, A2_embeds]
        names = ['T1', 'T2', 'A1', 'A2']
        
        # Check for empty arrays
        for emb, name in zip(embeddings, names):
            if len(emb) == 0:
                return False, f"{name} embeddings are empty"
                
        # Check dimensions match
        dims = [emb.shape[1] for emb in embeddings]
        if len(set(dims)) > 1:
            return False, f"Embedding dimensions don't match: {dims}"
            
        # Check for NaN or infinite values
        for emb, name in zip(embeddings, names):
            if np.any(np.isnan(emb)) or np.any(np.isinf(emb)):
                return False, f"{name} embeddings contain NaN or infinite values"
                
        return True, "Valid"
