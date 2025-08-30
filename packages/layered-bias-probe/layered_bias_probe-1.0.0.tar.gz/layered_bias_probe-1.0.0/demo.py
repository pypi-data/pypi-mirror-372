"""
Quick Demo Script for layered-bias-probe

This script provides a quick demonstration of the package's capabilities
using a small model and a subset of WEAT categories.
"""

import os
import sys
import time
from datetime import datetime

def main():
    print("🚀 layered-bias-probe Quick Demo")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Import the package
        print("📦 Importing layered-bias-probe...")
        from layered_bias_probe import BiasProbe
        from layered_bias_probe.utils.weat_category import get_default_categories, WEAT_CATEGORIES_INFO
        print("✅ Package imported successfully!")
        
        # Show available WEAT categories
        print("\n📊 Available WEAT Categories:")
        categories = list(WEAT_CATEGORIES_INFO.keys())
        for i, category in enumerate(categories[:5], 1):  # Show first 5
            info = WEAT_CATEGORIES_INFO[category]
            print(f"  {i}. {category}: {info['description']}")
        if len(categories) > 5:
            print(f"  ... and {len(categories) - 5} more categories")
        
        # Demo configuration
        demo_config = {
            "model_name": "facebook/opt-125m",  # Small model for quick demo
            "weat_categories": ["weat1", "weat6"],  # Just 2 categories for speed
            "language": "english",
            "max_layers": 8,  # Limit layers for speed
            "use_quantization": True,  # Use quantization to save memory
            "device": "cpu"  # Use CPU for compatibility
        }
        
        print(f"\n⚙️ Demo Configuration:")
        print(f"  Model: {demo_config['model_name']}")
        print(f"  WEAT Categories: {', '.join(demo_config['weat_categories'])}")
        print(f"  Language: {demo_config['language']}")
        print(f"  Max Layers: {demo_config['max_layers']}")
        print(f"  Device: {demo_config['device']}")
        
        # Create output directory
        output_dir = "demo_results"
        os.makedirs(output_dir, exist_ok=True)
        print(f"  Output Directory: {output_dir}")
        
        # Initialize bias probe
        print(f"\n🔧 Initializing BiasProbe...")
        probe = BiasProbe(
            model_name=demo_config["model_name"],
            use_quantization=demo_config["use_quantization"],
            torch_dtype="float16",
            device_map="auto"
        )
        print("✅ BiasProbe initialized!")
        
        # Run bias analysis
        print(f"\n🔍 Running bias analysis...")
        print("⚠️  This may take a few minutes for the first run (downloading model)...")
        
        start_time = time.time()
        
        # Run analysis using the correct API
        print(f"\n  📈 Analyzing categories: {', '.join(demo_config['weat_categories'])}")
        
        try:
            results = probe.analyze_bias(
                languages=[demo_config["language"]],
                weat_categories=demo_config["weat_categories"],
                output_dir=output_dir,
                comments="demo_analysis"
            )
            
            if "error" in results:
                print(f"    ❌ Error: {results['error']}")
                return False
                
            # Get the results DataFrame
            results_df = results.get("results_df")
            if results_df is not None and hasattr(results_df, 'empty') and not results_df.empty:
                print(f"    ✅ Completed! Found {len(results_df)} records")
                # Convert to list of dicts for compatibility with rest of script
                results_list = results_df.to_dict('records')
            else:
                print(f"    ❌ No results generated")
                return False
                
        except Exception as e:
            print(f"    ❌ Error during analysis: {e}")
            return False
        
        analysis_time = time.time() - start_time
        
        # Handle results - check what we got back from analyze_bias
        if isinstance(results, dict) and "results_df" in results:
            results_df = results["results_df"]
            output_file_path = results.get("output_file", "")
            
            print(f"\n💾 Results Summary:")
            print(f"  Analysis time: {analysis_time:.1f} seconds")
            
            # Check if output_file_path is a string and exists
            if isinstance(output_file_path, str) and output_file_path and os.path.exists(output_file_path):
                print(f"  Results saved to: {output_file_path}")
                
                # Try to read the CSV to show summary
                try:
                    import pandas as pd
                    df = pd.read_csv(output_file_path)
                    print(f"  Total records: {len(df)}")
                    
                    if 'weat_score' in df.columns:
                        print(f"  Average bias score: {df['weat_score'].abs().mean():.4f}")
                        print(f"  Score range: {df['weat_score'].min():.4f} to {df['weat_score'].max():.4f}")
                    
                    # Show sample results
                    print(f"\n📋 Sample Results (first 5 records):")
                    display_cols = [col for col in ['layer', 'weat_category_id', 'weat_score', 'p_value'] 
                                  if col in df.columns]
                    if display_cols:
                        print(df[display_cols].head().to_string(index=False))
                    else:
                        print(df.head().to_string(index=False))
                        
                except Exception as e:
                    print(f"  Could not read results file: {e}")
            else:
                print(f"  Results type: {type(results_df)}")
                print(f"  Output file: {output_file_path}")
                
        elif isinstance(results, dict) and "error" in results:
            print(f"\n❌ Analysis failed: {results['error']}")
            return False
        else:
            print(f"\n❌ Unexpected results format: {type(results)}")
            print(f"Results keys: {results.keys() if isinstance(results, dict) else 'Not a dict'}")
            return False
        
        # Demo CLI usage
        print(f"\n🖥️ CLI Demo:")
        print("You can also use the command-line interface:")
        print(f"python -m layered_bias_probe.cli analyze \\")
        print(f"  --model {demo_config['model_name']} \\")
        print(f"  --language {demo_config['language']} \\")
        print(f"  --categories {' '.join(demo_config['weat_categories'])} \\")
        print(f"  --output-dir {output_dir}")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"⏰ Total time: {time.time() - start_time:.1f} seconds")
        print(f"📁 Results available in: {output_dir}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        print("Please make sure the package is installed:")
        print("python -m pip install -e .")
        return False
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🚀 Ready to explore more? Check out the examples/ directory!")
        print("📖 Read the README.md for detailed documentation.")
    sys.exit(0 if success else 1)
