# core/utils.py

import re
from core.canonical_registry import CANONICAL_COMPANIES

def normalize(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w\s]", "", name)

    noise = [
        "ltd", "limited", "pvt", "private",
        "unlisted", "pre ipo", "pre-ipo",
        "share", "shares"
    ]

    for n in noise:
        name = name.replace(n, "")

    return re.sub(r"\s+", " ", name).strip()

def resolve_company(raw_name: str) -> str:
    norm = normalize(raw_name)

    for canonical, aliases in CANONICAL_COMPANIES.items():
        if norm == normalize(canonical):
            return canonical

        for alias in aliases:
            if norm == normalize(alias):
                return canonical

    # Unknown company
    return norm.title()
