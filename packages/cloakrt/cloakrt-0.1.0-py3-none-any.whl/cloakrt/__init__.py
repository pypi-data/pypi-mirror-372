from .harmony import HarmonyClient, HarmonyMessage, HarmonyResponse
from .schema import FindingValidator, Finding
from .runners import GridRunner, GridResult, RunResult
from .detector import Detector, DetectionResult, VulnerabilityType
from .scoring import Scorer, CompetitionScore
from .probes import (
    BaseProbe,
    ProbeResult,
    RewardHackingProbe,
    DeceptionProbe,
    HiddenMotivationsProbe,
    SabotageProbe,
    InappropriateToolUseProbe,
    DataExfiltrationProbe,
    SandbaggingProbe,
    EvaluationAwarenessProbe,
    ChainOfThoughtProbe,
)

__version__ = "0.1.0"
__all__ = [
    # Harmony
    "HarmonyClient",
    "HarmonyMessage", 
    "HarmonyResponse",
    # Detection
    "Detector",
    "DetectionResult",
    "VulnerabilityType",
    # Runners
    "GridRunner",
    "GridResult",
    "RunResult",
    # Schema
    "Finding",
    "FindingValidator",
    # Scoring
    "Scorer",
    "CompetitionScore",
    # Probes
    "BaseProbe",
    "ProbeResult",
    "RewardHackingProbe",
    "DeceptionProbe",
    "HiddenMotivationsProbe",
    "SabotageProbe",
    "InappropriateToolUseProbe",
    "DataExfiltrationProbe",
    "SandbaggingProbe",
    "EvaluationAwarenessProbe",
    "ChainOfThoughtProbe",
]