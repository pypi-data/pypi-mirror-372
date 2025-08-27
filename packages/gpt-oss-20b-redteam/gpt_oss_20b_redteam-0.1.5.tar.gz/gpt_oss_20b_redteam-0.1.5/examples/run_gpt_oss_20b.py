#!/usr/bin/env python3
"""
Run full red-teaming pipeline with local GPT-OSS-20B model.
"""

from gpt20b_redteam.config import load_example_config, get_model_config, set_model_backend
from gpt20b_redteam.model_wrapper import create_model
from gpt20b_redteam import RedTeamRunner

def main():
    # Configure for local Transformers model
    set_model_backend("transformers")
    load_example_config("huggingface_hub")
    
    # Get model config and set GPT-OSS-20B path
    mc = get_model_config()
    
    # Option 1: Use HuggingFace Hub model
    mc["model_path"] = "openai/gpt-oss-20b"  # Replace with actual GPT-OSS-20B model ID
    
    # Option 2: Use local model path
    # mc["model_path"] = "/path/to/your/gpt-oss-20b-model"
    
    # Optional: Configure for your hardware
    mc["device"] = "auto"  # or "cuda", "mps", "cpu"
    mc["torch_dtype"] = "auto"  # or "float16", "bfloat16"
    
    print(f"🔧 Model config: {mc}")
    
    # Create model
    print("🔄 Loading model...")
    model = create_model(**mc)
    
    # Run ALL probes
    print("🚀 Starting GPT-OSS-20B red-teaming pipeline...")
    runner = RedTeamRunner(model, output_dir="results_gpt_oss_20b")
    
    # Run with multiple seeds for robustness
    seeds = [42, 1010, 90521]
    results = runner.run_all_probes(seeds=seeds)
    
    print(f"\n✅ Pipeline completed!")
    print(f"📊 Summary: {results['summary']}")
    print(f"📁 Results saved to: results_gpt_oss_20b/")

if __name__ == "__main__":
    main()
