from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from backend.models.schemas import EvidenceRecord


DATA_DIR = Path(__file__).resolve().parents[2] / "storage"
EVIDENCE_FILE = DATA_DIR / "evidence_log.jsonl"
REPORTS_FILE = DATA_DIR / "reports.jsonl"


def _ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def create_hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def log_evidence(payload: Dict[str, Any], source: str, consent: bool) -> EvidenceRecord:
    _ensure_storage()
    timestamp = datetime.now(timezone.utc)
    request_hash = create_hash(payload)

    record = {
        "timestamp": timestamp.isoformat(),
        "request_hash": request_hash,
        "source": source,
        "consent": consent,
        "payload": payload,
    }
    with EVIDENCE_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    return EvidenceRecord(
        timestamp=timestamp,
        request_hash=request_hash,
        source=source,
        consent=consent,
    )


def log_report(payload: Dict[str, Any]) -> Dict[str, str]:
    _ensure_storage()
    payload_hash = create_hash(payload)
    with REPORTS_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"payload_hash": payload_hash, "payload": payload}, ensure_ascii=False) + "\n")
    return {"payload_hash": payload_hash}
