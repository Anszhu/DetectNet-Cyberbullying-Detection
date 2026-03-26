from __future__ import annotations

import re

from langdetect import DetectorFactory, LangDetectException, detect


DetectorFactory.seed = 0

HINDI_BLOCK = re.compile(r"[\u0900-\u097F]")


def detect_language(text: str) -> str:
    if HINDI_BLOCK.search(text):
        return "hi"

    try:
        detected = detect(text)
    except LangDetectException:
        return "unknown"

    if detected.startswith("hi"):
        return "hi"
    if detected.startswith("en"):
        return "en"
    return detected


def normalize_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    return cleaned.lower()
