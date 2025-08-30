"""
Batch Model Comparison Example

This example demonstrates how to analyze and compare bias across multiple models
using the batch processing capabilities.
"""

import os
from layered_bias_probe import BatchProcessor

def main():
    # Configure the batch analysis
    models = [
        "EleutherAI/pythia-70m",
        "facebook/MobileLLM-125M",
        "HuggingFaceTB/SmolLM2-135M"
    ]
    
    languages = ["en"]  # Focus on English for comparison
    weat_categories = ["WEAT1", "WEAT2", "WEAT6"]
    output_dir = "./batch_comparison_results"
    cache_dir = "./model_cache"
    
    print("🔄 Starting Batch Model Comparison Example")
    print(f"Models to compare: {len(models)}")
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model}")
    print(f"Languages: {languages}")
    print(f"WEAT Categories: {weat_categories}")
    print("-" * 60)
    
    # Initialize the batch processor
    processor = BatchProcessor(
        models=models,
        cache_dir=cache_dir,
        use_quantization=True  # Use quantization to save memory
    )
    
    try:
        # Get processing summary
        summary = processor.get_processing_summary()
        print(f"📋 Processing Summary:")
        print(f"  Total models: {summary['total_models']}")
        print(f"  Supported models: {len(summary['supported_models'])}")
        print(f"  Cache directory: {summary['cache_dir']}")
        print("-" * 60)
        
        # Run batch bias analysis
        print("Running batch bias analysis...")
        results = processor.run_bias_analysis(
            languages=languages,
            weat_categories=weat_categories,
            output_dir=output_dir,
            comments="model_comparison",
            save_individual_results=True,
            continue_on_error=True
        )
        
        # Display batch results
        print("✅ Batch analysis completed!")
        print(f"✅ Successful models: {len(results['model_results'])}")
        print(f"❌ Failed models: {len(results['failed_models'])}")
        
        if results['failed_models']:
            print("\n❌ Failed Models:")
            for failed in results['failed_models']:
                print(f"  - {failed['model']}: {failed['error']}")
        
        if results['consolidated_file']:
            print(f"\n📊 Consolidated results: {results['consolidated_file']}")
        
        # Run model comparison
        if len(results['model_results']) > 1:
            print("\n🔍 Running model comparison analysis...")
            comparison_results = processor.compare_models(
                languages=languages,
                weat_categories=weat_categories,
                output_dir=output_dir,
                metric="mean_absolute_bias"
            )
            
            print(f"📈 Comparison results: {comparison_results['comparison_file']}")
            
            # Display rankings
            print(f"\n🏆 Model Rankings (by {comparison_results['metric_used']}):")
            for lang in languages:
                if lang in comparison_results['rankings']:
                    print(f"\n  {lang.upper()} Language:")
                    for i, model_stats in enumerate(comparison_results['rankings'][lang], 1):
                        model_name = model_stats['model'].split('/')[-1]
                        metric_value = model_stats[comparison_results['metric_used']]
                        print(f"    {i}. {model_name}: {metric_value:.4f}")
        
        # Show summary statistics
        if results['model_results']:
            print(f"\n⏱️ Processing Times:")
            processing_times = results['summary']['processing_times']
            for model, time_taken in processing_times.items():
                model_short = model.split('/')[-1]
                print(f"  {model_short}: {time_taken:.2f}s")
        
    except Exception as e:
        print(f"❌ Error during batch processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
