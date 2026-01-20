import re
from core.canonical import CANONICAL_COMPANIES

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    remove = ["ltd", "limited", "unlisted", "shares"]
    for r in remove:
        text = text.replace(r, "")
    return " ".join(text.split())

def resolve_company(name):
    norm = normalize(name)

    for canonical, aliases in CANONICAL_COMPANIES.items():
        for alias in aliases:
            if norm == normalize(alias):
                return canonical

    return norm.title()
