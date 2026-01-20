import pandas as pd
from core.resolver import resolve_company

# ---------------- LOAD RAW DATA ----------------
df = pd.read_csv("data/raw_upload.csv")

# ---------------- NORMALIZE COLUMN NAMES ----------------
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

# ---------------- FIND SHARE NAME COLUMN ----------------
POSSIBLE_SHARE_COLS = [
    "share_name",
    "shares_name",
    "company",
    "company_name",
    "shares"
]

share_col = None
for col in POSSIBLE_SHARE_COLS:
    if col in df.columns:
        share_col = col
        break

if not share_col:
    raise ValueError(
        f"No share name column found. Columns present: {list(df.columns)}"
    )

# ---------------- APPLY CANONICAL RESOLUTION ----------------
df["Company"] = df[share_col].apply(resolve_company)

# ---------------- OPTIONAL: SORT FOR CLEAN OUTPUT ----------------
if "price" in df.columns:
    df = df.sort_values(["Company", "price"])

# ---------------- SAVE CLEAN DATA ----------------
df.to_csv("data/final_clean.csv", index=False)

print("Data cleaned and ready")
