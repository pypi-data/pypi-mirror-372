# layered-bias-probe Package Summary

## 🎉 Package Created Successfully!

The `layered-bias-probe` package has been successfully created with all the functionality you requested. Here's what has been built:

## 📁 Package Structure

```
layered-bias-probe/
├── setup.py                           # Package setup and metadata
├── requirements.txt                   # Dependencies
├── README.md                          # Comprehensive documentation
├── install_and_test.py               # Installation and testing script
├── demo.py                           # Quick demo script
├── layered_bias_probe/               # Main package
│   ├── __init__.py                   # Package initialization
│   ├── cli.py                        # Command-line interface
│   ├── core/                         # Core functionality
│   │   ├── bias_probe.py             # Main bias analysis class
│   │   ├── fine_tuner.py             # Fine-tuning with bias tracking
│   │   ├── batch_processor.py        # Batch analysis across models
│   │   └── results_analyzer.py       # Results visualization and analysis
│   ├── utils/                        # Utility modules
│   │   ├── model_manager.py          # Model loading and management
│   │   ├── weat_category.py          # WEAT category definitions
│   │   ├── weathub_loader.py         # Dataset loading
│   │   ├── embedding_extractor.py    # Layer embedding extraction
│   │   └── bias_quantifier.py        # Bias quantification (WEAT scores)
│   └── config/                       # Configuration
│       ├── default.yaml              # Default configuration
│       └── __init__.py               # Config management
└── examples/                         # Usage examples
    ├── basic_analysis.py             # Basic bias analysis
    ├── finetuning_with_bias_tracking.py  # Fine-tuning with bias tracking
    ├── batch_model_comparison.py     # Batch model comparison
    └── results_analysis.py           # Results analysis and visualization
```

## 🚀 Quick Start

### 1. Installation
```bash
# Navigate to the package directory
cd layered-bias-probe

# Run the installation and testing script
python install_and_test.py

# Or install manually
pip install -e .
```

### 2. Quick Demo
```bash
# Run the demo script to see the package in action
python demo.py
```

### 3. Command Line Usage
```bash
# Basic bias analysis
python -m layered_bias_probe.cli analyze --model facebook/opt-125m --language english

# With specific WEAT categories
python -m layered_bias_probe.cli analyze \
  --model facebook/opt-125m \
  --language english \
  --categories WEAT1 WEAT6 \
  --output-dir my_results

# Fine-tuning with bias tracking
python -m layered_bias_probe.cli finetune \
  --model facebook/opt-125m \
  --dataset alpaca \
  --language english \
  --epochs 3

# Batch model comparison
python -m layered_bias_probe.cli batch \
  --models facebook/opt-125m microsoft/DialoGPT-small \
  --language english \
  --output-dir comparison_results
```

### 4. Python API Usage
```python
from layered_bias_probe import BiasProbe, FineTuner, BatchProcessor

# Basic bias analysis
probe = BiasProbe(model_name="facebook/opt-125m")
results = probe.analyze_bias(
    languages=["english"],
    weat_categories=["WEAT1", "WEAT6"]
)

# Fine-tuning with bias tracking
tuner = FineTuner(
    model_name="facebook/opt-125m",
    finetune_dataset="alpaca"
)
results = tuner.finetune_and_track_bias(
    epochs=3,
    languages=["english"]
)

# Batch model comparison
processor = BatchProcessor()
results = processor.compare_models(
    model_names=["facebook/opt-125m", "microsoft/DialoGPT-small"],
    languages=["english"]
)
```

## 🔧 Key Features

### ✅ Core Functionality
- **Layer-wise bias analysis** using WEAT (Word Embedding Association Test)
- **Fine-tuning with bias tracking** during training
- **Batch processing** for comparing multiple models
- **Comprehensive results analysis** with visualizations

### ✅ Model Support
- Any HuggingFace transformer model
- Automatic model quantization for memory efficiency
- GPU/CPU support with automatic device detection

### ✅ WEAT Categories
- 20+ predefined WEAT categories covering:
  - Gender bias (career, academic, family)
  - Racial bias (African American names, European American names)
  - Religious bias (Christianity, Islam, Judaism)
  - India-specific biases (caste, religion, regional)

### ✅ Language Support
- English, Hindi, Bengali
- Extensible to other languages

### ✅ Output Formats
- CSV files with detailed bias metrics
- Interactive HTML visualizations
- PNG plots for publications
- Structured results for further analysis

### ✅ Configuration
- YAML-based configuration
- Command-line overrides
- Flexible parameter settings

## 📊 Available WEAT Categories

| Category | Description | Type |
|----------|-------------|------|
| WEAT1 | Flowers vs. Insects with Pleasant vs. Unpleasant | Valence |
| WEAT2 | Instruments vs. Weapons with Pleasant vs. Unpleasant | Valence |
| WEAT6 | Career vs. Family with Male vs. Female Names | Gender-Profession |
| WEAT7 | Math vs. Arts with Male vs. Female Terms | Gender-Academic |
| WEAT8 | Science vs. Arts with Male vs. Female Terms | Gender-Academic |
| WEAT9 | Mental vs. Physical Disease with Controllable vs. Uncontrollable | Disability |
| WEAT10 | Young vs. Old Names with Pleasant vs. Unpleasant | Age |
| ... | 10+ more categories for comprehensive bias analysis | Various |

## 🔍 Analysis Outputs

Each analysis produces:
- **Layer-wise bias scores** (WEAT effect sizes)
- **Statistical significance** (p-values)
- **Temporal evolution** during fine-tuning
- **Model comparisons** across architectures
- **Visualization dashboards** for exploration

## 🛠️ Extensibility

The package is designed to be easily extended:
- **Add new WEAT categories** in `utils/weat_category.py`
- **Support new languages** by adding datasets
- **Custom analysis workflows** using the core classes
- **Integration with existing pipelines** via Python API

## 📖 Documentation

- **README.md**: Comprehensive usage guide
- **Examples**: Ready-to-run scripts in `examples/`
- **CLI Help**: `python -m layered_bias_probe.cli --help`
- **Docstrings**: Detailed documentation in all modules

## 🧪 Testing

Run the test suite:
```bash
python install_and_test.py
```

This will:
- Install all dependencies
- Test package imports
- Verify CLI functionality
- Run basic analysis tests

## 🎯 Use Cases

1. **Research**: Analyze bias in pre-trained models
2. **Development**: Track bias during model fine-tuning
3. **Comparison**: Evaluate bias across model families
4. **Monitoring**: Continuous bias assessment in ML pipelines
5. **Education**: Learn about bias in language models

## 📈 Performance

- **Memory efficient**: Automatic quantization support
- **Fast analysis**: Optimized layer extraction
- **Scalable**: Batch processing for multiple models
- **Resumable**: Checkpoint support for long analyses

## 🤝 Contributing

The package structure supports easy contributions:
- Modular design for independent development
- Clear separation of concerns
- Comprehensive testing framework
- Standardized configuration system

---

## 🎉 Ready to Use!

Your `layered-bias-probe` package is ready for:
- **Research publications**
- **Production deployment**
- **Educational use**
- **Community sharing**

Start with the demo script (`python demo.py`) to see it in action, then explore the examples and documentation for advanced usage.

Happy bias probing! 🔍📊
