"""
Command Line Interface for layered-bias-probe package.
"""

import click
import json
from typing import List, Optional
from .core.bias_probe import BiasProbe
from .core.fine_tuner import FineTuner
from .core.batch_processor import BatchProcessor
from .core.results_analyzer import ResultsAnalyzer
from .utils.model_manager import get_supported_models, is_model_supported
from .utils.weat_category import (
    get_all_weat_categories, 
    get_default_categories,
    WEAT_CATEGORIES_INFO
)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Layered Bias Probe - A toolkit for layer-wise bias analysis in language models."""
    pass


@cli.command()
@click.option('--model', '-m', required=True, help='Model identifier (e.g., EleutherAI/pythia-70m)')
@click.option('--languages', '-l', default='en', help='Comma-separated language codes (default: en)')
@click.option('--categories', '-c', help='Comma-separated WEAT categories (default: basic set)')
@click.option('--output', '-o', default='./results', help='Output directory (default: ./results)')
@click.option('--cache-dir', default='./cache', help='Cache directory (default: ./cache)')
@click.option('--comments', default='cli_analysis', help='Comments for the analysis')
@click.option('--quantization/--no-quantization', default=True, help='Use quantization (default: True)')
def analyze(model, languages, categories, output, cache_dir, comments, quantization):
    """Run bias analysis on a single model."""
    # Parse languages
    lang_list = [lang.strip() for lang in languages.split(',')]
    
    # Parse categories
    if categories:
        cat_list = [cat.strip() for cat in categories.split(',')]
    else:
        cat_list = get_default_categories('basic')
    
    click.echo(f"Starting bias analysis for {model}")
    click.echo(f"Languages: {lang_list}")
    click.echo(f"Categories: {cat_list}")
    
    # Check if model is supported
    if not is_model_supported(model):
        click.echo(f"Warning: {model} is not in the officially supported model list")
    
    # Initialize probe
    probe = BiasProbe(
        model_name=model,
        cache_dir=cache_dir,
        use_quantization=quantization
    )
    
    try:
        # Run analysis
        results = probe.analyze_bias(
            languages=lang_list,
            weat_categories=cat_list,
            output_dir=output,
            comments=comments
        )
        
        if "error" in results:
            click.echo(f"Error: {results['error']}", err=True)
            return
        
        click.echo(f"✅ Analysis completed successfully!")
        click.echo(f"Results saved to: {results['output_path']}")
        click.echo(f"Total records: {results['num_results']}")
        
    except Exception as e:
        click.echo(f"Error during analysis: {e}", err=True)
    finally:
        probe.unload_model()


@cli.command()
@click.option('--model', '-m', required=True, help='Model identifier')
@click.option('--dataset', '-d', required=True, help='Dataset identifier for fine-tuning')
@click.option('--epochs', '-e', default=3, help='Number of training epochs (default: 3)')
@click.option('--batch-size', '-b', default=4, help='Training batch size (default: 4)')
@click.option('--learning-rate', '-lr', default=2e-5, help='Learning rate (default: 2e-5)')
@click.option('--output', '-o', default='./fine_tuned_model', help='Output directory')
@click.option('--cache-dir', default='./cache', help='Cache directory')
@click.option('--track-bias/--no-track-bias', default=True, help='Track bias during training')
@click.option('--bias-languages', default='en', help='Languages for bias tracking')
@click.option('--bias-categories', help='WEAT categories for bias tracking')
@click.option('--upload/--no-upload', default=False, help='Upload to HuggingFace Hub')
@click.option('--hf-username', help='HuggingFace username for upload')
def finetune(model, dataset, epochs, batch_size, learning_rate, output, cache_dir, 
             track_bias, bias_languages, bias_categories, upload, hf_username):
    """Fine-tune a model with bias tracking."""
    # Parse bias languages
    bias_lang_list = [lang.strip() for lang in bias_languages.split(',')]
    
    # Parse bias categories
    if bias_categories:
        bias_cat_list = [cat.strip() for cat in bias_categories.split(',')]
    else:
        bias_cat_list = get_default_categories('basic')
    
    click.echo(f"Starting fine-tuning of {model} on {dataset}")
    
    # Initialize fine-tuner
    tuner = FineTuner(
        model_name=model,
        dataset_name=dataset,
        cache_dir=cache_dir,
        track_bias=track_bias,
        bias_languages=bias_lang_list,
        weat_categories=bias_cat_list,
        hf_username=hf_username
    )
    
    try:
        # Start training
        results = tuner.train(
            num_epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            output_dir=output,
            upload_to_hub=upload
        )
        
        click.echo(f"✅ Fine-tuning completed successfully!")
        click.echo(f"Model saved to: {results['output_dir']}")
        click.echo(f"Final loss: {results['final_loss']:.4f}")
        
        if track_bias:
            click.echo(f"Bias tracking results: {results['bias_results_dir']}")
        
    except Exception as e:
        click.echo(f"Error during fine-tuning: {e}", err=True)


@cli.command()
@click.option('--models', '-m', required=True, help='Comma-separated model identifiers')
@click.option('--languages', '-l', default='en', help='Comma-separated language codes')
@click.option('--categories', '-c', help='Comma-separated WEAT categories')
@click.option('--output', '-o', default='./batch_results', help='Output directory')
@click.option('--cache-dir', default='./cache', help='Cache directory')
@click.option('--compare/--no-compare', default=True, help='Generate model comparison')
def batch(models, languages, categories, output, cache_dir, compare):
    """Run batch analysis on multiple models."""
    # Parse models
    model_list = [model.strip() for model in models.split(',')]
    
    # Parse languages
    lang_list = [lang.strip() for lang in languages.split(',')]
    
    # Parse categories
    if categories:
        cat_list = [cat.strip() for cat in categories.split(',')]
    else:
        cat_list = get_default_categories('basic')
    
    click.echo(f"Starting batch analysis for {len(model_list)} models")
    click.echo(f"Models: {model_list}")
    
    # Initialize batch processor
    processor = BatchProcessor(
        models=model_list,
        cache_dir=cache_dir
    )
    
    try:
        # Run batch analysis
        results = processor.run_bias_analysis(
            languages=lang_list,
            weat_categories=cat_list,
            output_dir=output
        )
        
        click.echo(f"✅ Batch analysis completed!")
        click.echo(f"Successful models: {len(results['model_results'])}")
        click.echo(f"Failed models: {len(results['failed_models'])}")
        
        if results['consolidated_file']:
            click.echo(f"Consolidated results: {results['consolidated_file']}")
        
        # Generate comparison if requested
        if compare and len(results['model_results']) > 1:
            comparison_results = processor.compare_models(
                languages=lang_list,
                weat_categories=cat_list,
                output_dir=output
            )
            click.echo(f"Model comparison: {comparison_results['comparison_file']}")
        
    except Exception as e:
        click.echo(f"Error during batch processing: {e}", err=True)


@cli.command()
@click.option('--results-dir', '-r', required=True, help='Directory containing bias analysis results')
@click.option('--output', '-o', help='Output directory for analysis (default: results-dir/analysis)')
@click.option('--model', help='Model to analyze (analyze all if not specified)')
@click.option('--language', help='Language to analyze (analyze all if not specified)')
@click.option('--category', help='WEAT category to analyze (analyze all if not specified)')
@click.option('--interactive/--static', default=True, help='Generate interactive plots')
def analyze_results(results_dir, output, model, language, category, interactive):
    """Analyze and visualize bias analysis results."""
    click.echo(f"Analyzing results from {results_dir}")
    
    # Initialize analyzer
    analyzer = ResultsAnalyzer(
        results_dir=results_dir,
        output_dir=output
    )
    
    if analyzer.results_data is None:
        click.echo("No data found in the specified directory", err=True)
        return
    
    # Get summary
    summary = analyzer.get_summary()
    click.echo(f"Loaded data: {summary['total_records']} records")
    click.echo(f"Models: {summary['unique_models']}")
    click.echo(f"Languages: {summary['unique_languages']}")
    click.echo(f"Categories: {summary['unique_categories']}")
    
    try:
        # Generate summary report
        report = analyzer.generate_summary_report()
        click.echo("Generated summary report")
        
        # Generate visualizations based on parameters
        if model and language and category:
            # Single specific analysis
            analyzer.plot_bias_evolution(
                model_name=model,
                weat_category=category,
                language=language,
                interactive=interactive
            )
        elif model:
            # Heatmap for specific model
            analyzer.create_bias_heatmap(
                model_name=model,
                interactive=interactive
            )
        elif category and language:
            # Compare all models for specific category/language
            analyzer.compare_models(
                weat_category=category,
                language=language,
                interactive=interactive
            )
        else:
            # Generate default visualizations
            click.echo("Generating default visualizations...")
            
            # Pick first available model/language/category for demonstration
            first_model = summary['models'][0]
            first_lang = summary['languages'][0]
            first_cat = summary['categories'][0]
            
            analyzer.plot_bias_evolution(
                model_name=first_model,
                weat_category=first_cat,
                language=first_lang,
                interactive=interactive
            )
            
            analyzer.create_bias_heatmap(
                model_name=first_model,
                interactive=interactive
            )
        
        click.echo(f"✅ Analysis completed! Results saved to: {analyzer.output_dir}")
        
    except Exception as e:
        click.echo(f"Error during analysis: {e}", err=True)


@cli.command()
def list_weat():
    """List all available WEAT categories."""
    click.echo("Available WEAT Categories:")
    click.echo("=" * 50)
    
    for category, info in WEAT_CATEGORIES_INFO.items():
        click.echo(f"{category}: {info['description']}")
        click.echo(f"  Type: {info['bias_type']}")
        click.echo(f"  Split: {info['split']}")
        click.echo()


@cli.command()
def list_models():
    """List all officially supported models."""
    supported = get_supported_models()
    
    click.echo("Officially Supported Models:")
    click.echo("=" * 50)
    
    for model_id, info in supported.items():
        click.echo(f"{model_id}")
        click.echo(f"  Name: {info['name']}")
        click.echo(f"  Size: {info['size']}")
        click.echo(f"  Organization: {info['organization']}")
        click.echo()


@cli.command()
@click.option('--model', '-m', required=True, help='Model identifier')
@click.option('--cache-dir', default='./cache', help='Cache directory')
def model_info(model, cache_dir):
    """Get information about a specific model."""
    from .utils.model_manager import ModelManager
    
    manager = ModelManager(cache_dir=cache_dir)
    info = manager.get_model_info(model)
    
    if "error" in info:
        click.echo(f"Error getting model info: {info['error']}", err=True)
        return
    
    click.echo(f"Model Information: {model}")
    click.echo("=" * 50)
    
    for key, value in info.items():
        click.echo(f"{key}: {value}")


@cli.command()
@click.option('--category', '-c', required=True, help='WEAT category')
@click.option('--language', '-l', help='Language code (optional)')
def category_info(category, language):
    """Get information about a WEAT category."""
    from .utils.weathub_loader import WEATHubLoader
    
    info = WEAT_CATEGORIES_INFO.get(category)
    if not info:
        click.echo(f"Category '{category}' not found", err=True)
        return
    
    click.echo(f"WEAT Category: {category}")
    click.echo("=" * 50)
    click.echo(f"Description: {info['description']}")
    click.echo(f"Bias Type: {info['bias_type']}")
    click.echo(f"Dataset Split: {info['split']}")
    click.echo(f"Targets: {info['targets']}")
    click.echo(f"Attributes: {info['attributes']}")
    
    if language:
        # Check availability for specific language
        loader = WEATHubLoader()
        available = loader.validate_language_category_pair(language, category)
        click.echo(f"Available for {language}: {'Yes' if available else 'No'}")


def main():
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
