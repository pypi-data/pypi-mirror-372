"""
Main runner that orchestrates all red-teaming probes.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from .metrics import MetricsCollector
from .logger import FindingsLogger
from .probes.eval_awareness import EvaluationAwarenessProbe
from .probes.deception_rewardhack import DeceptionRewardHackProbe
from .probes.sabotage_code import SabotageCodeProbe
from .probes.encoding_evasion import EncodingEvasionProbe
from .probes.prefix_steering import PrefixSteeringProbe
from .probes.cross_probe_compounding import CrossProbeCompounding
from .probes.tokenizer_frequency_sandbagging import TokenizerFrequencySandbagging
from .probes.long_horizon_sleeper import LongHorizonSleeperTriggers
from .probes.covert_channel_capacity import CovertChannelCapacity
from .probes.refusal_boundary_cartography import RefusalBoundaryCartography


class RedTeamRunner:
    """Main orchestrator for running all red-teaming probes."""
    
    def __init__(self, model, output_dir: str = "results"):
        self.model = model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.metrics = MetricsCollector()
        self.logger = FindingsLogger(self.output_dir)
        
        # Initialize ALL probes (basic + advanced)
        self.probes = {
            "eval_awareness": EvaluationAwarenessProbe(model, self.metrics),
            "deception_rewardhack": DeceptionRewardHackProbe(model, self.metrics),
            "sabotage_code": SabotageCodeProbe(model, self.metrics),
            "encoding_evasion": EncodingEvasionProbe(model, self.metrics),
            "prefix_steering": PrefixSteeringProbe(model, self.metrics),
            "cross_probe_compounding": CrossProbeCompounding(model, self.metrics),
            "tokenizer_frequency_sandbagging": TokenizerFrequencySandbagging(model, self.metrics),
            "long_horizon_sleeper": LongHorizonSleeperTriggers(model, self.metrics),
            "covert_channel_capacity": CovertChannelCapacity(model, self.metrics),
            "refusal_boundary_cartography": RefusalBoundaryCartography(model, self.metrics),
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger_instance = logging.getLogger(__name__)
    
    def run_all_probes(self, seeds: List[int] = None) -> Dict[str, Any]:
        """Run all probes and collect findings."""
        if seeds is None:
            seeds = [42, 1010, 90521]
        
        self.logger_instance.info(f"Starting red-teaming run with {len(seeds)} seeds")
        
        all_findings = {}
        
        for probe_name, probe in self.probes.items():
            self.logger_instance.info(f"Running {probe_name} probe...")
            
            try:
                findings = probe.run_probe(seeds=seeds)
                all_findings[probe_name] = findings
                
                # Save individual probe results
                self.logger.save_findings(probe_name, findings)
                
                self.logger_instance.info(f"✓ {probe_name} completed successfully")
                
            except Exception as e:
                self.logger_instance.error(f"✗ {probe_name} failed: {e}")
                all_findings[probe_name] = {"error": str(e)}
        
        # Save combined results
        combined_results = {
            "timestamp": datetime.now().isoformat(),
            "seeds": seeds,
            "findings": all_findings,
            "summary": self._generate_summary(all_findings)
        }
        
        self.logger.save_combined_results(combined_results)
        
        return combined_results
    
    def run_single_probe(self, probe_name: str, seeds: List[int] = None) -> Dict[str, Any]:
        """Run a single probe by name."""
        if probe_name not in self.probes:
            raise ValueError(f"Unknown probe: {probe_name}")
        
        if seeds is None:
            seeds = [42]
        
        probe = self.probes[probe_name]
        findings = probe.run_probe(seeds=seeds)
        
        # Save results
        self.logger.save_findings(probe_name, findings)
        
        return findings
    
    def _generate_summary(self, all_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics across all probes."""
        summary = {
            "total_probes": len(all_findings),
            "successful_probes": len([f for f in all_findings.values() if "error" not in f]),
            "failed_probes": len([f for f in all_findings.values() if "error" in f]),
            "key_metrics": {}
        }
        
        # Extract key metrics from each probe
        for probe_name, findings in all_findings.items():
            if "error" not in findings and "metrics" in findings:
                summary["key_metrics"][probe_name] = findings["metrics"]
        
        return summary
    
    def get_probe_status(self) -> Dict[str, str]:
        """Get status of all probes."""
        return {name: "ready" for name in self.probes.keys()}
