"""
Basic Bias Analysis Example

This example demonstrates how to perform basic bias analysis on a language model
using the layered-bias-probe package.
"""

import os
from layered_bias_probe import BiasProbe

def main():
    # Configure the analysis
    model_name = "EleutherAI/pythia-70m"  # Small model for demonstration
    languages = ["en"]  # English analysis
    weat_categories = ["WEAT1", "WEAT2", "WEAT6"]  # Basic bias categories
    output_dir = "./bias_results"
    cache_dir = "./model_cache"
    
    print("🔍 Starting Basic Bias Analysis Example")
    print(f"Model: {model_name}")
    print(f"Languages: {languages}")
    print(f"WEAT Categories: {weat_categories}")
    print("-" * 50)
    
    # Initialize the bias probe
    probe = BiasProbe(
        model_name=model_name,
        cache_dir=cache_dir,
        use_quantization=True  # Use quantization to save memory
    )
    
    try:
        # Get model information
        model_info = probe.get_model_info()
        print(f"Model Type: {model_info.get('model_type', 'Unknown')}")
        print(f"Number of Layers: {model_info.get('num_layers', 'Unknown')}")
        print(f"Hidden Size: {model_info.get('hidden_size', 'Unknown')}")
        print("-" * 50)
        
        # Run bias analysis
        print("Running bias analysis...")
        results = probe.analyze_bias(
            languages=languages,
            weat_categories=weat_categories,
            output_dir=output_dir,
            comments="basic_example"
        )
        
        # Check for errors
        if "error" in results:
            print(f"❌ Error during analysis: {results['error']}")
            return
        
        # Display results
        print("✅ Analysis completed successfully!")
        print(f"📊 Total records generated: {results['num_results']}")
        print(f"💾 Results saved to: {results['output_path']}")
        
        # Display some sample results
        if "results" in results:
            df = results["results"]
            print("\n📈 Sample Results:")
            print(df.head(10).to_string(index=False))
            
            # Show summary statistics
            print(f"\n📊 Summary Statistics:")
            print(f"Mean bias score: {df['weat_score'].mean():.4f}")
            print(f"Std bias score: {df['weat_score'].std():.4f}")
            print(f"Max absolute bias: {df['weat_score'].abs().max():.4f}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        
    finally:
        # Clean up
        probe.unload_model()
        print("\n🧹 Model unloaded and memory cleaned up")

if __name__ == "__main__":
    main()
