#!/usr/bin/env python3
"""
Example usage of the model wrapper with different backends.
"""

import os
from gpt20b_redteam.model_wrapper import create_model
from gpt20b_redteam.config import setup_local_gpu_model, setup_openai_api, setup_anthropic_api, load_example_config

def example_transformers():
    """Example using local transformers model."""
    print("🔧 Example: Local Transformers Model")
    print("=" * 40)
    
    try:
        # Option 1: Direct configuration
        model = create_model(
            backend="transformers",
            model_path="microsoft/DialoGPT-medium",  # Replace with your model
            device="auto",
            torch_dtype="auto"
        )
        
        print(f"✓ Model loaded: {model.get_model_info()}")
        
        # Test generation
        response = model.generate("What is the capital of France?")
        print(f"Response: {response}")
        
        # Test activations (whitebox mode)
        if model.supports_activations():
            activations = model.get_activations("Hello world", layers=[0, 1])
            print(f"Activations available: {list(activations.keys())}")
        
        return model
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return None

def example_openai():
    """Example using OpenAI API."""
    print("\n🔧 Example: OpenAI API")
    print("=" * 40)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ Set OPENAI_API_KEY environment variable")
        return None
    
    try:
        model = create_model(
            backend="openai",
            api_key=api_key,
            model="gpt-4"
        )
        
        print(f"✓ Model loaded: {model.get_model_info()}")
        
        # Test generation
        response = model.generate("What is the capital of France?")
        print(f"Response: {response}")
        
        # Activations not available in blackbox mode
        print(f"Activations supported: {model.supports_activations()}")
        
        return model
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return None

def example_anthropic():
    """Example using Anthropic API."""
    print("\n🔧 Example: Anthropic API")
    print("=" * 40)
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️ Set ANTHROPIC_API_KEY environment variable")
        return None
    
    try:
        model = create_model(
            backend="anthropic",
            api_key=api_key,
            model="claude-3-sonnet-20240229"
        )
        
        print(f"✓ Model loaded: {model.get_model_info()}")
        
        # Test generation
        response = model.generate("What is the capital of France?")
        print(f"Response: {response}")
        
        # Activations not available in blackbox mode
        print(f"Activations supported: {model.supports_activations()}")
        
        return model
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return None

def example_config_management():
    """Example of managing configurations."""
    print("\n🔧 Example: Configuration Management")
    print("=" * 40)
    
    # Load example configurations
    print("Available configs:")
    load_example_config("huggingface_hub")
    
    # Quick setup functions
    print("\nQuick setup examples:")
    setup_local_gpu_model("/path/to/your/model")
    setup_openai_api("your-api-key")
    setup_anthropic_api("your-api-key")

def example_redteam_integration():
    """Example of integrating with red-teaming harness."""
    print("\n🔧 Example: Red-Teaming Integration")
    print("=" * 40)
    
    from gpt20b_redteam import RedTeamRunner
    
    try:
        # Create model
        model = create_model(
            backend="transformers",
            model_path="microsoft/DialoGPT-medium"
        )
        
        # Use in red-teaming harness
        runner = RedTeamRunner(model, output_dir="results")
        
        print("✓ Red-teaming harness initialized")
        print(f"✓ Probes available: {list(runner.get_probe_status().keys())}")
        
        # Run a probe
        findings = runner.run_single_probe("eval_awareness", seeds=[42])
        print(f"✓ Probe completed with {len(findings.get('results', []))} results")
        
        return runner
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return None

def main():
    """Run all examples."""
    print("🚀 Model Wrapper Examples")
    print("=" * 50)
    
    # Test different backends
    models = {}
    
    # Transformers (if available)
    models["transformers"] = example_transformers()
    
    # OpenAI (if API key available)
    models["openai"] = example_openai()
    
    # Anthropic (if API key available)
    models["anthropic"] = example_anthropic()
    
    # Configuration management
    example_config_management()
    
    # Red-teaming integration
    runner = example_redteam_integration()
    
    # Summary
    print("\n📊 Summary")
    print("=" * 20)
    
    working_models = {k: v for k, v in models.items() if v is not None}
    print(f"✓ Working models: {list(working_models.keys())}")
    
    if working_models:
        print("\n🎯 Next steps:")
        print("1. Choose your preferred backend")
        print("2. Update config.py with your settings")
        print("3. Run the main harness: python main.py")
        print("4. Check results/ directory for findings")
    else:
        print("\n⚠️ No models working. Check your setup and try again.")

if __name__ == "__main__":
    main()
