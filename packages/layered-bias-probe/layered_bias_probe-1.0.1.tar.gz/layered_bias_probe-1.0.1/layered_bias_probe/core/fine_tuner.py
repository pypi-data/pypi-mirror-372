"""
Fine Tuner - Handles fine-tuning with bias tracking capabilities.
"""

import os
import gc
import torch
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Union, Callable
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    TrainerCallback,
    DataCollatorForLanguageModeling,
)
from datasets import load_dataset

from ..utils.model_manager import ModelManager
from ..utils.weathub_loader import WEATHubLoader
from ..utils.embedding_extractor import LayerEmbeddingExtractor
from ..utils.bias_quantifier import BiasQuantifier
from ..utils.weat_category import get_default_categories


class BiasTrackingCallback(TrainerCallback):
    """Custom callback to track bias evolution during fine-tuning."""
    
    def __init__(
        self,
        tokenizer,
        weathub_loader: WEATHubLoader,
        bias_quantifier: BiasQuantifier,
        results_dir: str,
        model_name: str,
        languages: List[str],
        weat_categories: List[str],
        track_frequency: str = "epoch"  # "epoch" or "step"
    ):
        """
        Initialize the bias tracking callback.
        
        Args:
            tokenizer: Model tokenizer
            weathub_loader: WEATHub dataset loader
            bias_quantifier: Bias calculation utility
            results_dir: Directory to save bias tracking results
            model_name: Name of the model being fine-tuned
            languages: Languages to track bias for
            weat_categories: WEAT categories to analyze
            track_frequency: When to track bias ("epoch" or "step")
        """
        self.tokenizer = tokenizer
        self.weathub_loader = weathub_loader
        self.bias_quantifier = bias_quantifier
        self.results_dir = results_dir
        self.model_name = model_name
        self.languages = languages
        self.weat_categories = weat_categories
        self.track_frequency = track_frequency
        
        # Create results directory
        os.makedirs(results_dir, exist_ok=True)
        
        # Track bias history
        self.bias_history = []
    
    def on_epoch_end(self, args, state, control, **kwargs):
        """Run bias analysis at the end of each epoch."""
        if self.track_frequency == "epoch":
            self._run_bias_analysis(state.epoch, "epoch", kwargs.get('model'))
    
    def on_step_end(self, args, state, control, **kwargs):
        """Run bias analysis at specified step intervals."""
        if self.track_frequency == "step" and state.global_step % 100 == 0:
            self._run_bias_analysis(state.global_step, "step", kwargs.get('model'))
    
    def on_train_begin(self, args, state, control, **kwargs):
        """Run initial bias analysis before training starts."""
        print("\n--- Running Initial Bias Analysis (Before Fine-tuning) ---")
        self._run_bias_analysis(0, "initial", kwargs.get('model'))
    
    def on_train_end(self, args, state, control, **kwargs):
        """Run final bias analysis after training completes."""
        print("\n--- Running Final Bias Analysis (After Fine-tuning) ---")
        self._run_bias_analysis("final", "final", kwargs.get('model'))
        self._save_bias_history()
    
    def _run_bias_analysis(self, iteration: Union[int, str], stage: str, model):
        """Run bias analysis and save results."""
        if model is None:
            print("Warning: Model not available for bias analysis")
            return
        
        print(f"\n--- Running Bias Analysis at {stage} {iteration} ---")
        
        try:
            # Create embedding extractor for current model state
            embedding_extractor = LayerEmbeddingExtractor(model, self.tokenizer)
            num_layers = embedding_extractor.get_layer_count()
            
            all_results = []
            
            for lang in self.languages:
                for weat_cat in self.weat_categories:
                    print(f"Processing: Lang='{lang}', Category='{weat_cat}'")
                    
                    # Get word lists
                    word_lists = self.weathub_loader.get_word_lists(lang, weat_cat)
                    if not word_lists:
                        continue
                    
                    # Analyze across layers
                    for layer_idx in range(num_layers):
                        try:
                            # Extract embeddings
                            t1_embeds = embedding_extractor.get_embeddings(word_lists['targ1'], layer_idx)
                            t2_embeds = embedding_extractor.get_embeddings(word_lists['targ2'], layer_idx)
                            a1_embeds = embedding_extractor.get_embeddings(word_lists['attr1'], layer_idx)
                            a2_embeds = embedding_extractor.get_embeddings(word_lists['attr2'], layer_idx)
                            
                            # Calculate WEAT score
                            weat_score = self.bias_quantifier.weat_effect_size(
                                t1_embeds, t2_embeds, a1_embeds, a2_embeds
                            )
                            
                            # Store result
                            result = {
                                'model_id': self.model_name,
                                'language': lang,
                                'weat_category_id': weat_cat,
                                'layer_idx': layer_idx,
                                'weat_score': weat_score,
                                'iteration': iteration,
                                'stage': stage,
                                'timestamp': datetime.now().isoformat()
                            }
                            all_results.append(result)
                            
                        except Exception as e:
                            print(f"Error at layer {layer_idx}: {e}")
                            continue
            
            # Save results
            if all_results:
                self._save_iteration_results(all_results, iteration, stage)
                self.bias_history.extend(all_results)
            
            # Cleanup
            del embedding_extractor
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
        except Exception as e:
            print(f"Error in bias analysis: {e}")
        
        print(f"--- Bias Analysis at {stage} {iteration} Completed ---")
    
    def _save_iteration_results(self, results: List[Dict], iteration: Union[int, str], stage: str):
        """Save results for a specific iteration."""
        df = pd.DataFrame(results)
        filename = f"bias_results_{self.model_name.replace('/', '_')}_{stage}_{iteration}.csv"
        filepath = os.path.join(self.results_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Bias results saved to: {filepath}")
    
    def _save_bias_history(self):
        """Save complete bias tracking history."""
        if self.bias_history:
            df = pd.DataFrame(self.bias_history)
            filename = f"bias_evolution_{self.model_name.replace('/', '_')}_complete.csv"
            filepath = os.path.join(self.results_dir, filename)
            df.to_csv(filepath, index=False)
            print(f"Complete bias evolution saved to: {filepath}")


class FineTuner:
    """
    Fine-tuning class with integrated bias tracking capabilities.
    """
    
    def __init__(
        self,
        model_name: str,
        dataset_name: str,
        cache_dir: str = "./cache",
        track_bias: bool = True,
        bias_languages: List[str] = ["en"],
        weat_categories: Optional[List[str]] = None,
        hf_username: Optional[str] = None
    ):
        """
        Initialize the FineTuner.
        
        Args:
            model_name (str): HuggingFace model identifier
            dataset_name (str): HuggingFace dataset identifier for fine-tuning
            cache_dir (str): Directory for caching
            track_bias (bool): Whether to track bias during training
            bias_languages (List[str]): Languages to track bias for
            weat_categories (Optional[List[str]]): WEAT categories to analyze
            hf_username (Optional[str]): HuggingFace username for model upload
        """
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.cache_dir = cache_dir
        self.track_bias = track_bias
        self.bias_languages = bias_languages
        self.weat_categories = weat_categories or get_default_categories('basic')
        self.hf_username = hf_username
        
        # Initialize components
        self.model_manager = ModelManager(cache_dir=cache_dir)
        if track_bias:
            self.weathub_loader = WEATHubLoader(cache_dir=os.path.join(cache_dir, "datasets"))
            self.bias_quantifier = BiasQuantifier()
        
        # Setup cache directory
        os.makedirs(cache_dir, exist_ok=True)
    
    def prepare_dataset(
        self,
        max_length: int = 512,
        test_size: float = 0.1,
        prompt_template: Optional[str] = None
    ) -> tuple:
        """
        Prepare the dataset for fine-tuning.
        
        Args:
            max_length (int): Maximum sequence length
            test_size (float): Proportion of data to use for validation
            prompt_template (Optional[str]): Template for formatting prompts
            
        Returns:
            tuple: (train_dataset, eval_dataset, tokenizer)
        """
        print(f"Loading dataset: {self.dataset_name}")
        
        # Load dataset
        dataset = load_dataset(self.dataset_name, split="train", cache_dir=self.cache_dir)
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(self.model_name, cache_dir=self.cache_dir)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Apply prompt template if provided
        if prompt_template:
            dataset = dataset.map(lambda example: {"text": self._format_prompt(example, prompt_template)})
        elif "text" not in dataset.column_names:
            # Default formatting for instruction datasets
            dataset = dataset.map(lambda example: {"text": self._create_instruction_prompt(example)})
        
        # Tokenize dataset
        tokenized_dataset = dataset.map(
            lambda examples: tokenizer(
                examples["text"],
                truncation=True,
                max_length=max_length,
                padding=False
            ),
            batched=True,
            remove_columns=dataset.column_names
        )
        
        # Split into train and validation
        if test_size > 0:
            split_dataset = tokenized_dataset.train_test_split(test_size=test_size, seed=42)
            train_dataset = split_dataset['train']
            eval_dataset = split_dataset['test']
        else:
            train_dataset = tokenized_dataset
            eval_dataset = None
        
        print(f"Dataset prepared. Train: {len(train_dataset)}, Eval: {len(eval_dataset) if eval_dataset else 0}")
        
        return train_dataset, eval_dataset, tokenizer
    
    def train(
        self,
        num_epochs: int = 3,
        batch_size: int = 4,
        gradient_accumulation_steps: int = 4,
        learning_rate: float = 2e-5,
        warmup_steps: int = 100,
        save_strategy: str = "epoch",
        evaluation_strategy: str = "epoch",
        output_dir: str = "./fine_tuned_model",
        results_dir: str = "./bias_tracking_results",
        use_quantization: bool = False,
        max_length: int = 512,
        test_size: float = 0.1,
        prompt_template: Optional[str] = None,
        upload_to_hub: bool = False,
        **training_kwargs
    ) -> Dict:
        """
        Fine-tune the model with optional bias tracking.
        
        Args:
            num_epochs (int): Number of training epochs
            batch_size (int): Training batch size
            gradient_accumulation_steps (int): Gradient accumulation steps
            learning_rate (float): Learning rate
            warmup_steps (int): Number of warmup steps
            save_strategy (str): When to save checkpoints
            evaluation_strategy (str): When to run evaluation
            output_dir (str): Directory to save the fine-tuned model
            results_dir (str): Directory to save bias tracking results
            use_quantization (bool): Whether to use quantization during training
            max_length (int): Maximum sequence length
            test_size (float): Validation set proportion
            prompt_template (Optional[str]): Template for prompt formatting
            upload_to_hub (bool): Whether to upload to HuggingFace Hub
            **training_kwargs: Additional training arguments
            
        Returns:
            Dict: Training results and metadata
        """
        print(f"Starting fine-tuning of {self.model_name}")
        
        # Prepare dataset
        train_dataset, eval_dataset, tokenizer = self.prepare_dataset(
            max_length=max_length,
            test_size=test_size,
            prompt_template=prompt_template
        )
        
        # Load model for training (without quantization for training)
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            cache_dir=self.cache_dir
        )
        
        # Setup training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            learning_rate=learning_rate,
            warmup_steps=warmup_steps,
            save_strategy=save_strategy,
            evaluation_strategy=evaluation_strategy if eval_dataset else "no",
            logging_steps=10,
            bf16=True,
            report_to="none",
            remove_unused_columns=False,
            **training_kwargs
        )
        
        # Setup data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False
        )
        
        # Setup callbacks
        callbacks = []
        if self.track_bias:
            bias_callback = BiasTrackingCallback(
                tokenizer=tokenizer,
                weathub_loader=self.weathub_loader,
                bias_quantifier=self.bias_quantifier,
                results_dir=results_dir,
                model_name=self.model_name,
                languages=self.bias_languages,
                weat_categories=self.weat_categories
            )
            callbacks.append(bias_callback)
        
        # Initialize trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            processing_class=tokenizer,
            data_collator=data_collator,
            callbacks=callbacks
        )
        
        # Start training
        print("--- Starting Fine-tuning ---")
        training_result = trainer.train()
        
        # Save final model
        trainer.save_model(output_dir)
        print(f"Fine-tuned model saved to: {output_dir}")
        
        # Upload to HuggingFace Hub if requested
        if upload_to_hub and self.hf_username:
            repo_name = f"{self.hf_username}/{self._generate_repo_name()}"
            self._upload_to_hub(output_dir, repo_name)
        
        # Prepare results
        results = {
            "model_name": self.model_name,
            "dataset_name": self.dataset_name,
            "training_result": training_result,
            "output_dir": output_dir,
            "num_epochs": num_epochs,
            "final_loss": training_result.training_loss,
            "bias_tracking_enabled": self.track_bias
        }
        
        if self.track_bias:
            results.update({
                "bias_results_dir": results_dir,
                "bias_languages": self.bias_languages,
                "weat_categories": self.weat_categories
            })
        
        print("--- Fine-tuning Completed ---")
        return results
    
    def _create_instruction_prompt(self, example: Dict) -> str:
        """Create a formatted instruction prompt from a dataset example."""
        template = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:
{output}"""
        
        instruction = example.get("instruction", example.get("input", ""))
        output = example.get("output", example.get("response", example.get("target", "")))
        
        return template.format(instruction=instruction, output=output + "</s>")
    
    def _format_prompt(self, example: Dict, template: str) -> str:
        """Format a prompt using a custom template."""
        return template.format(**example)
    
    def _generate_repo_name(self) -> str:
        """Generate a repository name for HuggingFace Hub."""
        model_base = self.model_name.split('/')[-1]
        dataset_base = self.dataset_name.split('/')[-1]
        return f"{model_base}-finetuned-{dataset_base}"
    
    def _upload_to_hub(self, model_path: str, repo_name: str):
        """Upload model to HuggingFace Hub."""
        try:
            from huggingface_hub import HfApi
            
            api = HfApi()
            
            # Create repository
            api.create_repo(repo_id=repo_name, repo_type="model", exist_ok=True)
            
            # Upload folder
            api.upload_folder(
                folder_path=model_path,
                repo_id=repo_name,
                repo_type="model",
                commit_message=f"Upload fine-tuned {self.model_name}"
            )
            
            print(f"✅ Model uploaded to: https://huggingface.co/{repo_name}")
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")


def create_prompt_template(template_type: str = "alpaca") -> str:
    """
    Create a prompt template for common dataset formats.
    
    Args:
        template_type (str): Type of template ('alpaca', 'chat', 'qa', 'simple')
        
    Returns:
        str: Prompt template
    """
    templates = {
        "alpaca": """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:
{output}""",
        
        "chat": """<|user|>
{instruction}
<|assistant|>
{output}""",
        
        "qa": """Question: {instruction}
Answer: {output}""",
        
        "simple": "{instruction}\n\n{output}"
    }
    
    return templates.get(template_type, templates["alpaca"])
