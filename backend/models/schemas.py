from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


SeverityLevel = Literal["low", "moderate", "high", "critical"]


class AnalysisRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=2000)
    source: str = Field(default="web-ui")
    consent: bool = Field(default=True)
    user_id: Optional[str] = None


class RuleMatch(BaseModel):
    pattern: str
    category: str
    weight: float
    matched_text: str


class HighlightSpan(BaseModel):
    start: int
    end: int
    label: str


class RuleEngineResult(BaseModel):
    score: float
    severity_hint: SeverityLevel
    matches: List[RuleMatch]
    highlights: List[HighlightSpan]


class MLEngineResult(BaseModel):
    score: float
    label: str
    confidence: float
    explanation: List[str]


class FusedResult(BaseModel):
    final_score: float
    severity: SeverityLevel
    risk_band: str
    bullying_detected: bool
    math_note: str


class EvidenceRecord(BaseModel):
    timestamp: datetime
    request_hash: str
    source: str
    consent: bool


class AnalysisResponse(BaseModel):
    language: str
    normalized_text: str
    rule_engine: RuleEngineResult
    ml_engine: MLEngineResult
    fused: FusedResult
    evidence: EvidenceRecord
    recommendations: List[str]
    disclaimer: str


class DashboardSnapshot(BaseModel):
    total_requests: int
    severity_counts: Dict[str, int]
    language_counts: Dict[str, int]
    avg_score: float


class ReportRequest(BaseModel):
    text: str
    reporter_name: str
    reporter_email: str
    incident_channel: str
    notes: Optional[str] = ""


class ReportResponse(BaseModel):
    report_id: str
    created_at: datetime
    payload_hash: str
    status: str
    export_ready: Dict[str, str]
