from __future__ import annotations

import re
from typing import Dict, List, Tuple

from backend.models.schemas import HighlightSpan, RuleEngineResult, RuleMatch


RULES: Dict[str, List[Tuple[str, float, str]]] = {
    "en": [
        (r"\b(stupid|idiot|loser|moron)\b", 0.18, "insult"),
        (r"\b(kill yourself|go die)\b", 0.52, "self-harm incitement"),
        (r"\b(ugly|worthless|disgusting)\b", 0.22, "appearance shaming"),
        (r"\b(hate you|nobody likes you)\b", 0.26, "social exclusion"),
        (r"\b(slut|whore)\b", 0.35, "gendered harassment"),
        (r"\b(freak|weirdo)\b", 0.16, "targeted insult"),
        (r"(ha){2,}", 0.08, "mocking laughter"),
        (r"\b(i will leak|share your photo)\b", 0.38, "threat"),
    ],
    "hi": [
        (r"\b(bekaar|bewakoof|pagal)\b", 0.18, "insult"),
        (r"\b(tu mar ja|mar ja)\b", 0.52, "self-harm incitement"),
        (r"\b(gandi|ghatiya)\b", 0.22, "appearance shaming"),
        (r"\b(kisi ko tum pasand nahi|sab tumse nafrat karte)\b", 0.26, "social exclusion"),
        (r"\b(randi)\b", 0.35, "gendered harassment"),
        (r"\b(chhakka)\b", 0.32, "identity attack"),
        (r"\b(photo viral kar dunga|photo leak kar dunga)\b", 0.38, "threat"),
    ],
}

TARGETING_PATTERNS = [
    (r"\byou\b", 0.08, "direct targeting"),
    (r"\btu\b", 0.08, "direct targeting"),
    (r"\btera\b", 0.08, "direct targeting"),
    (r"\byour\b", 0.08, "direct targeting"),
]

INTENSIFIERS = [
    (r"!{2,}", 0.04, "intensifier"),
    (r"[A-Z]{4,}", 0.06, "shouting"),
]


def run_rule_engine(text: str, language: str) -> RuleEngineResult:
    matches: List[RuleMatch] = []
    highlights: List[HighlightSpan] = []
    score = 0.0
    lowered = text.lower()

    active_rules = RULES.get(language, []) + TARGETING_PATTERNS + INTENSIFIERS

    for pattern, weight, category in active_rules:
        for found in re.finditer(pattern, text, flags=re.IGNORECASE):
            matched_text = found.group(0)
            score += weight
            matches.append(
                RuleMatch(
                    pattern=pattern,
                    category=category,
                    weight=weight,
                    matched_text=matched_text,
                )
            )
            highlights.append(
                HighlightSpan(start=found.start(), end=found.end(), label=category)
            )

    if lowered.count("@") >= 2:
        score += 0.06
        matches.append(
            RuleMatch(
                pattern="@mentions",
                category="group targeting",
                weight=0.06,
                matched_text="@",
            )
        )

    score = min(score, 1.0)

    if score >= 0.75:
        severity_hint = "critical"
    elif score >= 0.5:
        severity_hint = "high"
    elif score >= 0.25:
        severity_hint = "moderate"
    else:
        severity_hint = "low"

    return RuleEngineResult(
        score=score,
        severity_hint=severity_hint,
        matches=matches,
        highlights=highlights,
    )
