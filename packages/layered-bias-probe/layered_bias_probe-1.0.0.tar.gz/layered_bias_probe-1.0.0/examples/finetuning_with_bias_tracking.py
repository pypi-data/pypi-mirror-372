"""
Fine-tuning with Bias Tracking Example

This example demonstrates how to fine-tune a model while tracking bias evolution
during the training process.
"""

import os
from layered_bias_probe import FineTuner

def main():
    # Configure the fine-tuning
    model_name = "EleutherAI/pythia-70m"  # Small model for demonstration
    dataset_name = "iamshnoo/alpaca-cleaned-hindi"  # Hindi instruction dataset
    output_dir = "./fine_tuned_pythia_hindi"
    bias_results_dir = "./bias_tracking_results"
    cache_dir = "./model_cache"
    
    # Bias tracking configuration
    bias_languages = ["en", "hi"]  # Track bias in both English and Hindi
    weat_categories = ["WEAT1", "WEAT2", "WEAT6"]  # Basic bias categories
    
    print("🔧 Starting Fine-tuning with Bias Tracking Example")
    print(f"Model: {model_name}")
    print(f"Dataset: {dataset_name}")
    print(f"Bias tracking languages: {bias_languages}")
    print(f"WEAT Categories: {weat_categories}")
    print("-" * 60)
    
    # Initialize the fine-tuner
    tuner = FineTuner(
        model_name=model_name,
        dataset_name=dataset_name,
        cache_dir=cache_dir,
        track_bias=True,  # Enable bias tracking
        bias_languages=bias_languages,
        weat_categories=weat_categories,
        hf_username="your_username"  # Replace with your HuggingFace username
    )
    
    try:
        # Start fine-tuning with bias tracking
        print("Starting fine-tuning with bias tracking...")
        results = tuner.train(
            num_epochs=3,  # Reduced for demonstration
            batch_size=4,
            gradient_accumulation_steps=4,
            learning_rate=2e-5,
            output_dir=output_dir,
            results_dir=bias_results_dir,
            upload_to_hub=False  # Set to True if you want to upload
        )
        
        # Display results
        print("✅ Fine-tuning completed successfully!")
        print(f"📁 Model saved to: {results['output_dir']}")
        print(f"📉 Final training loss: {results['final_loss']:.4f}")
        
        if results['bias_tracking_enabled']:
            print(f"📊 Bias tracking results saved to: {results['bias_results_dir']}")
            print(f"🌐 Languages tracked: {results['bias_languages']}")
            print(f"📋 WEAT categories tracked: {results['weat_categories']}")
        
        # List generated bias tracking files
        if os.path.exists(bias_results_dir):
            bias_files = [f for f in os.listdir(bias_results_dir) if f.endswith('.csv')]
            print(f"\n📈 Generated {len(bias_files)} bias tracking files:")
            for file in bias_files[:5]:  # Show first 5 files
                print(f"  - {file}")
            if len(bias_files) > 5:
                print(f"  ... and {len(bias_files) - 5} more files")
        
    except Exception as e:
        print(f"❌ Error during fine-tuning: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
