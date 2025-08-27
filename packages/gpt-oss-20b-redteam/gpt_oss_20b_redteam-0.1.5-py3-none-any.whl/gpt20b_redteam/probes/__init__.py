"""
Probe modules for different types of red-teaming tests.
"""

from .base import BaseProbe
from .eval_awareness import EvaluationAwarenessProbe
from .deception_rewardhack import DeceptionRewardHackProbe
from .sabotage_code import SabotageCodeProbe
from .encoding_evasion import EncodingEvasionProbe
from .prefix_steering import PrefixSteeringProbe

# Advanced probing probes
from .refusal_boundary_cartography import RefusalBoundaryCartography
from .covert_channel_capacity import CovertChannelCapacity
from .long_horizon_sleeper import LongHorizonSleeperTriggers
from .tokenizer_frequency_sandbagging import TokenizerFrequencySandbagging
from .cross_probe_compounding import CrossProbeCompounding

__all__ = [
    "BaseProbe",
    "EvaluationAwarenessProbe", 
    "DeceptionRewardHackProbe",
    "SabotageCodeProbe",
    "EncodingEvasionProbe",
    "PrefixSteeringProbe",
    
    # Advanced probing probes
    "RefusalBoundaryCartography",
    "CovertChannelCapacity", 
    "LongHorizonSleeperTriggers",
    "TokenizerFrequencySandbagging",
    "CrossProbeCompounding"
]
