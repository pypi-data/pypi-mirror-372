#!/usr/bin/env python3
"""
Run full red-teaming pipeline with OpenAI API.
"""

import os
from gpt20b_redteam.config import setup_openai_api
from gpt20b_redteam.model_wrapper import create_model
from gpt20b_redteam import RedTeamRunner

def main():
    # Set your OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("export OPENAI_API_KEY=sk-...")
        return
    
    # Configure OpenAI backend
    setup_openai_api("gpt-4")  # or "gpt-3.5-turbo"
    
    # Create model
    model = create_model(backend="openai")
    
    # Run ALL probes
    print("🚀 Starting OpenAI red-teaming pipeline...")
    runner = RedTeamRunner(model, output_dir="results_openai")
    
    # Run with multiple seeds for robustness
    seeds = [42, 123, 456]
    results = runner.run_all_probes(seeds=seeds)
    
    print(f"\n✅ Pipeline completed!")
    print(f"📊 Summary: {results['summary']}")
    print(f"📁 Results saved to: results_openai/")

if __name__ == "__main__":
    main()
