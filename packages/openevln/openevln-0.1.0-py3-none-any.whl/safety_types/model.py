from dataclasses import dataclass
from typing import List, Dict, Any
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Overall:
    is_safe: bool
    risk_level: str
    composite_risk_score: float
    max_severity: float
    max_breadth: float
    severity_description: str
    breadth_description: str
    confidence: float


@dataclass_json
@dataclass
class Threat:
    category: str
    count: int
    severity: float
    breadth: float
    severity_desc: str
    breadth_desc: str


@dataclass_json
@dataclass
class Behavioral:
    behavioral_risk_score: float
    indicators: Dict[str, int]
    normalized_scores: Dict[str, float]
    is_high_risk: bool


@dataclass_json
@dataclass
class Detailed:
    pattern_detection: Dict[str, Any]
    behavioral_analysis: Behavioral
    context_adherence: float


@dataclass_json
@dataclass
class OverallAssessment:
    # nested wrapper for clarity
    overall: Overall
    severity_breadth_analysis: Dict[str, Any]
    detailed_analysis: Detailed
    recommendations: Dict[str, Any]


@dataclass_json
@dataclass
class Recommendations:
    action: str
    human_review_required: bool
    immediate_escalation: bool
    severity_based_action: str
    breadth_based_action: str


@dataclass_json
@dataclass
class Report:
    human_readable: str
    label: int
    structured: Dict[str, Any]


@dataclass_json
@dataclass
class SafetyResult:
    overall: Overall
    threats: List[Threat]
    detailed: Detailed
    recommendations: Recommendations
    report: Report
