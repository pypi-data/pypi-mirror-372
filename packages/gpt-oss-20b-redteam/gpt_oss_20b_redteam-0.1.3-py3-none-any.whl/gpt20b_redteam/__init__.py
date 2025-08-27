"""
GPT-OSS-20B Red-Teaming Harness

A comprehensive red-teaming toolkit for testing AI model safety and alignment.
Implements advanced probes for detecting misalignment, deception, and safety vulnerabilities.

Usage:
    # Command line
    gpt20b-redteam --model microsoft/DialoGPT-large
    gpt20b-redteam --openai gpt-4 --api-key sk-...
    
    # Python API
    from gpt20b_redteam import RedTeamRunner
    from gpt20b_redteam.model_wrapper import create_model
    
    model = create_model(backend="transformers", model_path="microsoft/DialoGPT-large")
    runner = RedTeamRunner(model)
    results = runner.run_all_probes(seeds=[42, 123, 456])
"""

__version__ = "0.1.0"
__author__ = "GPT-OSS-20B Team"
__email__ = "team@gpt-oss-20b.org"

from .runner import RedTeamRunner
from .model_wrapper import create_model, ModelWrapper
from .config import (
    setup_openai_api,
    setup_anthropic_api,
    load_example_config,
    get_model_config,
    get_redteam_config,
    set_model_backend
)

__all__ = [
    "RedTeamRunner",
    "create_model", 
    "ModelWrapper",
    "setup_openai_api",
    "setup_anthropic_api", 
    "load_example_config",
    "get_model_config",
    "get_redteam_config",
    "set_model_backend"
]
