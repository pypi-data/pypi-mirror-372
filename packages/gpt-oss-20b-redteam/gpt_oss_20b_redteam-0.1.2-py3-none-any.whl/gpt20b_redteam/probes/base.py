"""
Base class for all red-teaming probes.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import random
import json
from pathlib import Path


class BaseProbe(ABC):
    """Abstract base class for all red-teaming probes."""
    
    def __init__(self, model, metrics_collector, name: str = None):
        self.model = model
        self.metrics = metrics_collector
        self.name = name or self.__class__.__name__
        self.results_cache = {}
    
    @abstractmethod
    def generate_prompts(self, seed: int = None) -> List[Dict[str, Any]]:
        """Generate prompts for this probe type."""
        pass
    
    @abstractmethod
    def run_probe(self, seeds: List[int] = None) -> Dict[str, Any]:
        """Run the probe and return findings."""
        pass
    
    @abstractmethod
    def analyze_outputs(self, outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze probe outputs and calculate metrics."""
        pass
    
    def to_json(self) -> Dict[str, Any]:
        """Convert probe results to JSON format for Kaggle submission."""
        return {
            "probe_name": self.name,
            "timestamp": self._get_timestamp(),
            "results": self.results_cache,
            "metrics": getattr(self, 'current_metrics', {})
        }
    
    def _set_random_seed(self, seed: int):
        """Set random seed for reproducible results."""
        if seed is not None:
            random.seed(seed)
            # Also set numpy seed if available
            try:
                import numpy as np
                np.random.seed(seed)
            except ImportError:
                pass
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _generate_id(self, prefix: str = "probe") -> str:
        """Generate unique ID for probe runs."""
        import uuid
        return f"{prefix}_{uuid.uuid4().hex[:8]}"
    
    def _save_intermediate_results(self, results: Dict[str, Any], filename: str = None):
        """Save intermediate results to file."""
        if filename is None:
            filename = f"{self.name}_intermediate_{self._get_timestamp()}.json"
        
        output_path = Path("results") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return output_path
    
    def _load_intermediate_results(self, filename: str) -> Dict[str, Any]:
        """Load intermediate results from file."""
        file_path = Path("results") / filename
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the probe."""
        return {
            "name": self.name,
            "status": "ready",
            "cached_results": len(self.results_cache),
            "last_run": getattr(self, 'last_run_timestamp', None)
        }

    # Shared helper for querying the underlying model
    def _query_model(self, prompt: str, **kwargs) -> str:
        """Query the wrapped model safely and return a string response."""
        try:
            response = self.model.generate(prompt, **kwargs)
            # Some backends might return tuples or objects; coerce to string
            if isinstance(response, tuple):
                # Join non-empty string-like parts if possible
                parts = [str(p) for p in response if p is not None]
                return " ".join(parts)
            return str(response)
        except Exception as e:
            return f"Error: {e}"
