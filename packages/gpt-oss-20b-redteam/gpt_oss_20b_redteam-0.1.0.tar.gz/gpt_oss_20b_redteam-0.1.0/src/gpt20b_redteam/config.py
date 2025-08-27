"""
Configuration file for the red-teaming harness.
Modify these settings to use different models and backends.
"""

import os
from pathlib import Path

# Model configuration
MODEL_CONFIG = {
    # Choose your backend: "transformers", "openai", "anthropic", "mock"
    "backend": "mock",
    
    # Transformers backend settings
    "transformers": {
        "model_path": "microsoft/DialoGPT-medium",  # Replace with your actual model
        "device": "auto",  # "auto", "cpu", "cuda", "mps"
        "torch_dtype": "auto",  # "auto", "float16", "bfloat16", "float32"
        "trust_remote_code": True,
        "low_cpu_mem_usage": True
    },
    
    # OpenAI backend settings
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY", "your-api-key-here"),
        "model": "gpt-4",
        "base_url": None,  # For Azure OpenAI, etc.
        "max_tokens": 200,
        "temperature": 0.7
    },
    
    # Anthropic backend settings
    "anthropic": {
        "api_key": os.getenv("ANTHROPIC_API_KEY", "your-api-key-here"),
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 200,
        "temperature": 0.7
    }
}

# Red-teaming configuration
REDTEAM_CONFIG = {
    "output_dir": "results",
    "seeds": [42, 1010, 90521],  # Random seeds for reproducibility
    "max_samples_per_probe": 100,  # Limit samples for faster testing
    
    # Probe-specific settings
    "eval_awareness": {
        "enabled": True,
        "domains": ["geography", "history", "science"],
        "samples_per_domain": 10
    },
    
    "deception_rewardhack": {
        "enabled": False,  # Not implemented yet
        "samples": 50
    },
    
    "sabotage_code": {
        "enabled": False,  # Not implemented yet
        "low_stakes_samples": 25,
        "high_stakes_samples": 25
    },
    
    "encoding_evasion": {
        "enabled": False,  # Not implemented yet
        "encoding_depths": [1, 2, 3, 4, 5],
        "refusal_prompts": 10
    },
    
    "prefix_steering": {
        "enabled": False,  # Not implemented yet
        "prefix_styles": 5,
        "samples_per_style": 10
    }
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "redteam.log"
}

# Whitebox analysis configuration (for transformers models)
WHITEBOX_CONFIG = {
    "enabled": True,
    "layers_to_probe": "auto",  # "auto" or list of layer indices
    "activation_analysis": {
        "save_activations": True,
        "activation_dir": "activations",
        "probe_training": True,
        "probe_epochs": 100
    }
}

# Example configurations for different setups
EXAMPLE_CONFIGS = {
    "local_gpu": {
        "backend": "transformers",
        "model_path": "/path/to/your/local/model",
        "device": "cuda",
        "torch_dtype": "float16"
    },
    
    "local_cpu": {
        "backend": "transformers", 
        "model_path": "/path/to/your/local/model",
        "device": "cpu",
        "torch_dtype": "float32"
    },
    
    "huggingface_hub": {
        "backend": "transformers",
        "model_path": "microsoft/DialoGPT-medium",
        "device": "auto",
        "torch_dtype": "auto"
    },
    
    "openai_api": {
        "backend": "openai",
        "api_key": "your-openai-key",
        "model": "gpt-4"
    },
    
    "anthropic_api": {
        "backend": "anthropic",
        "api_key": "your-anthropic-key",
        "model": "claude-3-sonnet-20240229"
    }
}

def get_model_config():
    """Get the current model configuration."""
    backend = MODEL_CONFIG["backend"]
    
    if backend == "mock":
        return {"backend": "mock"}
    
    if backend not in MODEL_CONFIG:
        raise ValueError(f"Unknown backend: {backend}")
    
    config = {"backend": backend}
    config.update(MODEL_CONFIG[backend])
    
    return config

def get_redteam_config():
    """Get the red-teaming configuration."""
    return REDTEAM_CONFIG

def get_whitebox_config():
    """Get the whitebox analysis configuration."""
    return WHITEBOX_CONFIG

def set_model_backend(backend: str):
    """Change the model backend."""
    if backend not in ["transformers", "openai", "anthropic", "mock"]:
        raise ValueError(f"Unknown backend: {backend}")
    
    MODEL_CONFIG["backend"] = backend
    print(f"Model backend changed to: {backend}")

def load_example_config(config_name: str):
    """Load an example configuration."""
    if config_name not in EXAMPLE_CONFIGS:
        raise ValueError(f"Unknown config: {config_name}")
    
    config = EXAMPLE_CONFIGS[config_name]
    MODEL_CONFIG.update(config)
    print(f"Loaded example config: {config_name}")

# Quick setup functions
def setup_local_gpu_model(model_path: str):
    """Quick setup for local GPU model."""
    MODEL_CONFIG.update({
        "backend": "transformers",
        "model_path": model_path,
        "device": "cuda",
        "torch_dtype": "float16"
    })
    print(f"Configured for local GPU model: {model_path}")

def setup_openai_api(api_key: str, model: str = "gpt-4"):
    """Quick setup for OpenAI API."""
    MODEL_CONFIG.update({
        "backend": "openai",
        "api_key": api_key,
        "model": model
    })
    print(f"Configured for OpenAI API: {model}")

def setup_anthropic_api(api_key: str, model: str = "claude-3-sonnet-20240229"):
    """Quick setup for Anthropic API."""
    MODEL_CONFIG.update({
        "backend": "anthropic",
        "api_key": api_key,
        "model": model
    })
    print(f"Configured for Anthropic API: {model}")

if __name__ == "__main__":
    print("🔧 Red-Teaming Harness Configuration")
    print("=" * 40)
    
    print(f"Current backend: {MODEL_CONFIG['backend']}")
    print(f"Output directory: {REDTEAM_CONFIG['output_dir']}")
    print(f"Whitebox enabled: {WHITEBOX_CONFIG['enabled']}")
    
    print("\n📋 Available configurations:")
    for name in EXAMPLE_CONFIGS.keys():
        print(f"  • {name}")
    
    print("\n💡 Usage examples:")
    print("  • setup_local_gpu_model('/path/to/model')")
    print("  • setup_openai_api('your-key')")
    print("  • load_example_config('local_gpu')")
