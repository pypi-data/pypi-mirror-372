"""
Progress tracking utilities for red-teaming probes.
Provides detailed progress reporting for better user experience.
"""

import os
import time
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum


class ProgressStage(Enum):
    """Different stages of probe execution."""
    INITIALIZING = "initializing"
    GENERATING_PROMPTS = "generating_prompts"
    RUNNING_QUERIES = "running_queries"
    ANALYZING_RESULTS = "analyzing_results"
    CALCULATING_METRICS = "calculating_metrics"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProgressUpdate:
    """Progress update information."""
    stage: ProgressStage
    current: int
    total: int
    description: str
    details: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class ProgressTracker:
    """Tracks progress for probe execution."""
    
    def __init__(self, probe_name: str, total_stages: int = 5):
        self.probe_name = probe_name
        self.total_stages = total_stages
        self.current_stage = 0
        self.stage_start_time = time.time()
        self.callback: Optional[Callable[[ProgressUpdate], None]] = None
        
        # Check if we're running in CLI mode
        self.cli_mode = os.getenv('RICH_CLI_MODE') == '1'
    
    def set_callback(self, callback: Callable[[ProgressUpdate], None]):
        """Set callback for progress updates."""
        self.callback = callback
    
    def update(self, stage: ProgressStage, current: int, total: int, 
               description: str, details: Optional[str] = None, 
               metrics: Optional[Dict[str, Any]] = None):
        """Update progress."""
        update = ProgressUpdate(
            stage=stage,
            current=current,
            total=total,
            description=description,
            details=details,
            metrics=metrics
        )
        
        if self.callback:
            self.callback(update)
        
        # Also log for debugging
        if not self.cli_mode:
            percentage = (current / total * 100) if total > 0 else 0
            print(f"[{self.probe_name}] {stage.value}: {current}/{total} ({percentage:.1f}%) - {description}")
    
    def start_stage(self, stage: ProgressStage, total: int, description: str):
        """Start a new stage."""
        self.current_stage += 1
        self.stage_start_time = time.time()
        self.update(stage, 0, total, description)
    
    def update_stage(self, current: int, total: int, details: Optional[str] = None):
        """Update current stage progress."""
        stage = ProgressStage.RUNNING_QUERIES  # Default to running queries
        description = f"Processing {current}/{total}"
        self.update(stage, current, total, description, details)
    
    def complete_stage(self, metrics: Optional[Dict[str, Any]] = None):
        """Complete current stage."""
        elapsed = time.time() - self.stage_start_time
        self.update(
            ProgressStage.COMPLETED,
            self.total_stages,
            self.total_stages,
            f"Stage completed in {elapsed:.1f}s",
            metrics=metrics
        )


class ProbeProgressMixin:
    """Mixin to add progress tracking to probes."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress_tracker = ProgressTracker(self.name)
    
    def set_progress_callback(self, callback: Callable[[ProgressUpdate], None]):
        """Set progress callback."""
        self.progress_tracker.set_callback(callback)
    
    def _track_progress(self, stage: ProgressStage, current: int, total: int, 
                       description: str, details: Optional[str] = None):
        """Track progress for this probe."""
        self.progress_tracker.update(stage, current, total, description, details)
    
    def _start_progress_stage(self, stage: ProgressStage, total: int, description: str):
        """Start a progress stage."""
        self.progress_tracker.start_stage(stage, total, description)
    
    def _update_progress(self, current: int, total: int, details: Optional[str] = None):
        """Update progress within current stage."""
        self.progress_tracker.update_stage(current, total, details)
    
    def _complete_progress(self, metrics: Optional[Dict[str, Any]] = None):
        """Complete progress tracking."""
        self.progress_tracker.complete_stage(metrics)


# Global progress callback for CLI integration
_global_progress_callback: Optional[Callable[[ProgressUpdate], None]] = None


def set_global_progress_callback(callback: Callable[[ProgressUpdate], None]):
    """Set global progress callback for CLI integration."""
    global _global_progress_callback
    _global_progress_callback = callback


def get_global_progress_callback() -> Optional[Callable[[ProgressUpdate], None]]:
    """Get global progress callback."""
    return _global_progress_callback
