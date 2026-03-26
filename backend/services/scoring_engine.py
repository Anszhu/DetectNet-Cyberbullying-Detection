from __future__ import annotations

from backend.models.schemas import FusedResult


def fuse_scores(rule_score: float, ml_score: float) -> FusedResult:
    final_score = round((0.45 * rule_score) + (0.55 * ml_score), 4)

    if final_score >= 0.8:
        severity = "critical"
        risk_band = "Immediate review required"
    elif final_score >= 0.6:
        severity = "high"
        risk_band = "High risk"
    elif final_score >= 0.35:
        severity = "moderate"
        risk_band = "Needs moderation"
    else:
        severity = "low"
        risk_band = "Low risk"

    bullying_detected = final_score >= 0.35
    math_note = (
        f"Final score = 0.45 x rule_score ({rule_score:.2f}) + "
        f"0.55 x ml_score ({ml_score:.2f}) = {final_score:.2f}"
    )

    return FusedResult(
        final_score=final_score,
        severity=severity,
        risk_band=risk_band,
        bullying_detected=bullying_detected,
        math_note=math_note,
    )
