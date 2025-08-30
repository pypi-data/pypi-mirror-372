"""
Installation and Testing Script for layered-bias-probe

This script helps users install dependencies and test the package functionality.
"""

import subprocess
import sys
import os
import importlib

def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def check_package_import(package_name):
    """Check if a package can be imported."""
    try:
        importlib.import_module(package_name)
        print(f"✅ {package_name} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {package_name}: {e}")
        return False

def main():
    print("🚀 layered-bias-probe Installation and Testing Script")
    print("=" * 60)
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(script_dir)
    
    print(f"📁 Package directory: {package_dir}")
    print(f"🐍 Python version: {sys.version}")
    
    # Check if we're in the right directory
    setup_py_path = os.path.join(package_dir, "setup.py")
    if not os.path.exists(setup_py_path):
        print(f"❌ setup.py not found at {setup_py_path}")
        print("Please run this script from the package directory.")
        return False
    
    # Change to package directory
    os.chdir(package_dir)
    print(f"📂 Changed to directory: {os.getcwd()}")
    
    # Step 1: Install package in development mode
    print("\n" + "="*60)
    print("STEP 1: Installing package in development mode")
    print("="*60)
    
    install_success = run_command(
        f"{sys.executable} -m pip install -e .",
        "Installing package in development mode"
    )
    
    if not install_success:
        print("❌ Package installation failed. Please check the error above.")
        return False
    
    # Step 2: Install additional dependencies
    print("\n" + "="*60)
    print("STEP 2: Installing additional dependencies")
    print("="*60)
    
    additional_deps = [
        "jupyter",
        "ipywidgets",
        "ipykernel"
    ]
    
    for dep in additional_deps:
        run_command(
            f"{sys.executable} -m pip install {dep}",
            f"Installing {dep}"
        )
    
    # Step 3: Test imports
    print("\n" + "="*60)
    print("STEP 3: Testing package imports")
    print("="*60)
    
    packages_to_test = [
        "layered_bias_probe",
        "layered_bias_probe.core.bias_probe",
        "layered_bias_probe.core.fine_tuner",
        "layered_bias_probe.core.batch_processor",
        "layered_bias_probe.core.results_analyzer",
        "layered_bias_probe.utils.model_manager",
        "layered_bias_probe.utils.weat_category",
        "layered_bias_probe.utils.weathub_loader",
        "layered_bias_probe.utils.embedding_extractor",
        "layered_bias_probe.utils.bias_quantifier",
        "layered_bias_probe.config",
        "layered_bias_probe.cli"
    ]
    
    import_success = True
    for package in packages_to_test:
        if not check_package_import(package):
            import_success = False
    
    # Step 4: Test CLI
    print("\n" + "="*60)
    print("STEP 4: Testing CLI functionality")
    print("="*60)
    
    cli_success = run_command(
        f"{sys.executable} -m layered_bias_probe.cli --help",
        "Testing CLI help command"
    )
    
    # Step 5: Test basic functionality
    print("\n" + "="*60)
    print("STEP 5: Testing basic functionality")
    print("="*60)
    
    test_script = '''
import sys
sys.path.insert(0, ".")

try:
    from layered_bias_probe import BiasProbe, WEATCategory, ModelManager
    
    # Test WEATCategory
    categories = WEATCategory.get_all_categories()
    print(f"✅ Found {len(categories)} WEAT categories")
    
    # Test ModelManager
    manager = ModelManager()
    print("✅ ModelManager initialized successfully")
    
    # Test BiasProbe initialization
    probe = BiasProbe(
        model_name="facebook/opt-125m",
        use_quantization=False,
        device="cpu"
    )
    print("✅ BiasProbe initialized successfully")
    
    print("✅ All basic functionality tests passed!")
    
except Exception as e:
    print(f"❌ Basic functionality test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    
    with open("temp_test.py", "w") as f:
        f.write(test_script)
    
    try:
        basic_test_success = run_command(
            f"{sys.executable} temp_test.py",
            "Testing basic functionality"
        )
    finally:
        # Clean up
        if os.path.exists("temp_test.py"):
            os.remove("temp_test.py")
    
    # Final report
    print("\n" + "="*60)
    print("INSTALLATION AND TESTING SUMMARY")
    print("="*60)
    
    all_success = (install_success and import_success and 
                  cli_success and basic_test_success)
    
    if all_success:
        print("🎉 ALL TESTS PASSED! Package is ready to use.")
        print("\nNext steps:")
        print("1. Try running the examples in the 'examples/' directory")
        print("2. Check the CLI with: python -m layered_bias_probe.cli --help")
        print("3. Read the README.md for detailed usage instructions")
        
        print("\nQuick start commands:")
        print("# Basic bias analysis")
        print("python -m layered_bias_probe.cli analyze --model facebook/opt-125m --language english")
        print("\n# Run an example")
        print("python examples/basic_analysis.py")
        
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure you have Python 3.8+ installed")
        print("2. Try updating pip: python -m pip install --upgrade pip")
        print("3. Install PyTorch manually if GPU support is needed")
        print("4. Check the requirements.txt for dependency versions")
    
    return all_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
