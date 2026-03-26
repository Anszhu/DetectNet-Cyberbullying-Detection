from __future__ import annotations

from typing import List

from backend.models.schemas import MLEngineResult


NEGATIVE_SEMANTIC_CUES = {
    "en": {
        "tokens": ["idiot", "loser", "hate", "die", "leak", "ugly", "worthless", "stupid"],
        "supportive": ["sorry", "help", "support", "calm", "report"],
    },
    "hi": {
        "tokens": ["bewakoof", "mar", "nafrat", "ghatiya", "pagal", "randi"],
        "supportive": ["madad", "shant", "support", "report", "sahayata"],
    },
}


def run_ml_engine(text: str, language: str) -> MLEngineResult:
    """
    Lightweight transformer-ready approximation.

    For an offline student demo, this module exposes the same contract that a
    fine-tuned BERT/XLM-R model would use. It produces a confidence score from
    semantic cues so the full stack works without downloading a large model.
    """
    lowered = text.lower()
    cues = NEGATIVE_SEMANTIC_CUES.get(language, NEGATIVE_SEMANTIC_CUES["en"])

    toxic_hits = sum(1 for token in cues["tokens"] if token in lowered)
    supportive_hits = sum(1 for token in cues["supportive"] if token in lowered)
    second_person_hits = sum(1 for token in ["you", "your", "tu", "tum", "tera"] if token in lowered)

    raw_score = (toxic_hits * 0.22) + (second_person_hits * 0.08) - (supportive_hits * 0.15)
    score = max(0.02, min(0.98, 0.18 + raw_score))

    if score >= 0.7:
        label = "cyberbullying"
    elif score >= 0.45:
        label = "possibly harmful"
    else:
        label = "non-bullying"

    explanation: List[str] = []
    if toxic_hits:
        explanation.append("The ML layer found harmful semantic cues associated with insults, threats, or exclusion.")
    if second_person_hits:
        explanation.append("The text appears directed at a target, which raises cyberbullying likelihood.")
    if supportive_hits:
        explanation.append("Supportive words reduced the risk score, helping avoid false positives.")
    if not explanation:
        explanation.append("No strong harmful semantic cues were detected in the current text.")

    return MLEngineResult(
        score=score,
        label=label,
        confidence=score,
        explanation=explanation,
    )
