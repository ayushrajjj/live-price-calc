import re
from core.canonical import CANONICAL_COMPANIES

UNKNOWN_LOG_FILE = "unknown_companies.csv"

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

def log_unknown(name: str):
    with open(UNKNOWN_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(name + "\n")

def resolve_company(raw_name: str) -> str:
    norm = normalize(raw_name)

    for canonical, aliases in CANONICAL_COMPANIES.items():
        if norm == normalize(canonical):
            return canonical
        for alias in aliases:
            if norm == normalize(alias):
                return canonical

    log_unknown(raw_name)
    return norm.title()
