# Layered Bias Probe

A comprehensive Python package for performing layer-wise bias analysis in language models, with support for fine-tuning and bias evolution tracking.

## Features

- **Layer-wise Bias Analysis**: Probe bias at each transformer layer using WEAT (Word Embedding Association Test) methodology
- **Multiple WEAT Categories**: Support for all WEAT categories including original, new human biases, and India-specific biases
- **Fine-tuning Integration**: Track bias evolution during model fine-tuning
- **Multi-language Support**: Analyze bias across different languages (English, Hindi, Bengali, etc.)
- **Flexible Model Support**: Works with 9+ popular language models
- **Export Results**: Save analysis results in CSV format with proper naming conventions

## Supported Models

- apple/OpenELM-270M
- facebook/MobileLLM-125M
- cerebras/Cerebras-GPT-111M 
- EleutherAI/pythia-70m
- meta-llama/Llama-3.2-1B
- Qwen/Qwen2.5-1.5B
- google/gemma-2-2b
- ibm-granite/granite-3.3-2b-base
- HuggingFaceTB/SmolLM2-135M

## Installation

```bash
pip install layered-bias-probe
```

Or install from source:

```bash
git clone https://github.com/yourusername/layered-bias-probe.git
cd layered-bias-probe
pip install -e .
```

## Quick Start

### Basic Bias Analysis

```python
from layered_bias_probe import BiasProbe

# Initialize the probe
probe = BiasProbe(
    model_name="EleutherAI/pythia-70m",
    cache_dir="./cache"
)

# Run bias analysis
results = probe.analyze_bias(
    languages=["en", "hi"],
    weat_categories=["WEAT1", "WEAT2", "WEAT6"],
    output_dir="./results"
)

print(f"Analysis complete! Results saved to: {results['output_path']}")
```

### Fine-tuning with Bias Tracking

```python
from layered_bias_probe import FineTuner

# Initialize fine-tuner with bias tracking
tuner = FineTuner(
    model_name="EleutherAI/pythia-70m",
    dataset_name="iamshnoo/alpaca-cleaned-hindi",
    track_bias=True,
    bias_languages=["en", "hi"],
    weat_categories=["WEAT1", "WEAT2", "WEAT6"]
)

# Fine-tune model and track bias evolution
results = tuner.train(
    num_epochs=5,
    batch_size=4,
    learning_rate=2e-5,
    output_dir="./fine_tuned_model"
)
```

### Command Line Interface

```bash
# Basic bias analysis
layered-bias-probe analyze --model "EleutherAI/pythia-70m" --languages en hi --output ./results

# Fine-tuning with bias tracking
layered-bias-probe finetune --model "EleutherAI/pythia-70m" --dataset "iamshnoo/alpaca-cleaned-hindi" --track-bias --output ./results

# List available WEAT categories
layered-bias-probe list-weat

# Get model info
layered-bias-probe model-info --model "EleutherAI/pythia-70m"
```

## WEAT Categories

The package supports multiple WEAT (Word Embedding Association Test) categories:

### Original WEAT Tests
- **WEAT1**: Flowers vs. Insects with Pleasant vs. Unpleasant
- **WEAT2**: Instruments vs. Weapons with Pleasant vs. Unpleasant  
- **WEAT6**: Career vs. Family with Male vs. Female Names
- **WEAT7**: Math vs. Arts with Male vs. Female Terms
- **WEAT8**: Science vs. Arts with Male vs. Female Terms
- **WEAT9**: Mental vs. Physical Disease with Temporary vs. Permanent

### New Human Biases (WEAT11-15)
- **WEAT11-15**: Various social and cultural bias categories

### India-Specific Biases (WEAT16-26)  
- **WEAT16-26**: Caste, religion, and regional bias categories specific to Indian context

## Configuration

Create a `config.yaml` file to customize default settings:

```yaml
# Default model settings
model:
  cache_dir: "./cache"
  device_map: "auto"
  torch_dtype: "float16"
  quantization: true

# Bias analysis settings
bias_analysis:
  default_languages: ["en"]
  default_weat_categories: ["WEAT1", "WEAT2", "WEAT6"]
  batch_size: 1
  
# Fine-tuning settings
fine_tuning:
  default_epochs: 5
  default_batch_size: 4
  default_learning_rate: 2e-5
  save_strategy: "epoch"
  
# Output settings
output:
  results_format: "csv"
  include_timestamp: true
  compression: false
```

## Advanced Usage

### Custom WEAT Categories

```python
from layered_bias_probe import BiasProbe, WEATCategory

# Define custom WEAT category
custom_weat = WEATCategory(
    name="CUSTOM1",
    target1=["word1", "word2"],
    target2=["word3", "word4"], 
    attribute1=["attr1", "attr2"],
    attribute2=["attr3", "attr4"],
    language="en"
)

probe = BiasProbe("EleutherAI/pythia-70m")
results = probe.analyze_custom_bias(custom_weat, output_dir="./results")
```

### Batch Processing Multiple Models

```python
from layered_bias_probe import BatchProcessor

models = [
    "EleutherAI/pythia-70m",
    "facebook/MobileLLM-125M", 
    "cerebras/Cerebras-GPT-111M"
]

processor = BatchProcessor(models)
results = processor.run_bias_analysis(
    languages=["en", "hi"],
    weat_categories=["WEAT1", "WEAT2", "WEAT6"],
    output_dir="./batch_results"
)
```

### Results Analysis and Visualization

```python
from layered_bias_probe import ResultsAnalyzer

# Load and analyze results
analyzer = ResultsAnalyzer("./results")

# Generate bias evolution plots
analyzer.plot_bias_evolution(
    model_name="EleutherAI/pythia-70m",
    weat_category="WEAT1",
    language="en"
)

# Create heatmaps
analyzer.create_bias_heatmap(
    model_name="EleutherAI/pythia-70m",
    languages=["en", "hi"]
)

# Export summary statistics
summary = analyzer.generate_summary_report()
```

## Output Format

Results are saved in CSV format with the following structure:

```csv
model_id,language,weat_category_id,layer_idx,weat_score,comments,timestamp
EleutherAI/pythia-70m,en,WEAT1,0,-0.234,Before_finetuning,2024-01-01T12:00:00
EleutherAI/pythia-70m,en,WEAT1,1,-0.187,Before_finetuning,2024-01-01T12:00:00
...
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this package in your research, please cite:

```bibtex
@software{layered_bias_probe,
  title={Layered Bias Probe: A Toolkit for Layer-wise Bias Analysis in Language Models},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/layered-bias-probe}
}
```

## Acknowledgments

This package builds upon the WEAT methodology and WEATHub dataset. Special thanks to the research community for their contributions to bias detection in NLP.
