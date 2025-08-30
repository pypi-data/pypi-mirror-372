"""
Results Analysis and Visualization Example

This example demonstrates how to analyze and visualize bias analysis results
using the ResultsAnalyzer class.
"""

import os
import pandas as pd
from layered_bias_probe import ResultsAnalyzer

def main():
    # Configure the analysis
    results_dir = "./bias_results"  # Directory containing bias analysis results
    analysis_output_dir = "./analysis_outputs"
    
    print("📊 Starting Results Analysis and Visualization Example")
    print(f"Results directory: {results_dir}")
    print(f"Analysis output: {analysis_output_dir}")
    print("-" * 60)
    
    # Check if results directory exists
    if not os.path.exists(results_dir):
        print(f"❌ Results directory '{results_dir}' not found!")
        print("Please run a bias analysis first to generate results.")
        return
    
    # Initialize the results analyzer
    analyzer = ResultsAnalyzer(
        results_dir=results_dir,
        output_dir=analysis_output_dir
    )
    
    # Check if data was loaded
    if analyzer.results_data is None:
        print("❌ No bias analysis results found in the directory!")
        print("Please ensure the directory contains CSV files from bias analysis.")
        return
    
    try:
        # Get and display summary
        summary = analyzer.get_summary()
        print("📋 Data Summary:")
        print(f"  Total records: {summary['total_records']}")
        print(f"  Unique models: {summary['unique_models']}")
        print(f"  Models: {', '.join([m.split('/')[-1] for m in summary['models']])}")
        print(f"  Languages: {', '.join(summary['languages'])}")
        print(f"  WEAT categories: {', '.join(summary['categories'])}")
        print(f"  Layer range: {summary['layer_range'][0]} - {summary['layer_range'][1]}")
        print(f"  Bias score range: {summary['bias_score_range'][0]:.4f} - {summary['bias_score_range'][1]:.4f}")
        print(f"  Mean absolute bias: {summary['mean_absolute_bias']:.4f}")
        print("-" * 60)
        
        # Generate comprehensive summary report
        print("📄 Generating comprehensive summary report...")
        report = analyzer.generate_summary_report()
        print("✅ Summary report generated!")
        
        # Create visualizations for the first available model/language/category
        first_model = summary['models'][0]
        first_language = summary['languages'][0]
        first_category = summary['categories'][0]
        
        print(f"\n📈 Creating visualizations for:")
        print(f"  Model: {first_model}")
        print(f"  Language: {first_language}")
        print(f"  Category: {first_category}")
        
        # 1. Bias Evolution Plot
        print("\n1. Creating bias evolution plot...")
        analyzer.plot_bias_evolution(
            model_name=first_model,
            weat_category=first_category,
            language=first_language,
            save_plot=True,
            interactive=True
        )
        
        # 2. Bias Heatmap
        print("2. Creating bias heatmap...")
        analyzer.create_bias_heatmap(
            model_name=first_model,
            languages=[first_language],
            save_plot=True,
            interactive=True
        )
        
        # 3. Model Comparison (if multiple models available)
        if summary['unique_models'] > 1:
            print("3. Creating model comparison plot...")
            analyzer.compare_models(
                weat_category=first_category,
                language=first_language,
                save_plot=True,
                interactive=True
            )
        else:
            print("3. Skipping model comparison (only one model available)")
        
        # 4. Export filtered data example
        print("4. Exporting filtered data...")
        filtered_data = analyzer.export_filtered_data(
            languages=[first_language],
            weat_categories=[first_category],
            output_file="filtered_sample_data.csv"
        )
        print(f"   Exported {len(filtered_data)} records")
        
        # Display some insights
        print(f"\n🔍 Key Insights:")
        
        # Find model with highest bias
        model_bias = {}
        for model in summary['models']:
            model_data = analyzer.results_data[analyzer.results_data['model_id'] == model]
            model_bias[model] = model_data['weat_score'].abs().mean()
        
        highest_bias_model = max(model_bias.keys(), key=lambda x: model_bias[x])
        lowest_bias_model = min(model_bias.keys(), key=lambda x: model_bias[x])
        
        print(f"  📈 Highest average bias: {highest_bias_model.split('/')[-1]} ({model_bias[highest_bias_model]:.4f})")
        print(f"  📉 Lowest average bias: {lowest_bias_model.split('/')[-1]} ({model_bias[lowest_bias_model]:.4f})")
        
        # Find category with highest bias
        category_bias = {}
        for category in summary['categories']:
            cat_data = analyzer.results_data[analyzer.results_data['weat_category_id'] == category]
            category_bias[category] = cat_data['weat_score'].abs().mean()
        
        highest_bias_category = max(category_bias.keys(), key=lambda x: category_bias[x])
        print(f"  🎯 Most biased category: {highest_bias_category} ({category_bias[highest_bias_category]:.4f})")
        
        print(f"\n✅ Analysis completed! Results saved to: {analysis_output_dir}")
        
        # List generated files
        if os.path.exists(analysis_output_dir):
            output_files = os.listdir(analysis_output_dir)
            print(f"\n📁 Generated files ({len(output_files)}):")
            for file in output_files:
                print(f"  - {file}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
