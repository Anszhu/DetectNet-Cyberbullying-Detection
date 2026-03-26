from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict

from backend.models.schemas import DashboardSnapshot


EVIDENCE_FILE = Path(__file__).resolve().parents[2] / "storage" / "evidence_log.jsonl"


def load_dashboard_snapshot() -> DashboardSnapshot:
    if not EVIDENCE_FILE.exists():
        return DashboardSnapshot(
            total_requests=0,
            severity_counts={},
            language_counts={},
            avg_score=0.0,
        )

    severity_counter: Counter[str] = Counter()
    language_counter: Counter[str] = Counter()
    scores = []

    with EVIDENCE_FILE.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            payload: Dict[str, object] = json.loads(line)
            request_payload = payload.get("payload", {})
            severity = str(request_payload.get("severity", "unknown"))
            language = str(request_payload.get("language", "unknown"))
            score = float(request_payload.get("final_score", 0.0))
            severity_counter[severity] += 1
            language_counter[language] += 1
            scores.append(score)

    avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0

    return DashboardSnapshot(
        total_requests=sum(severity_counter.values()),
        severity_counts=dict(severity_counter),
        language_counts=dict(language_counter),
        avg_score=avg_score,
    )
