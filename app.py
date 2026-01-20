import streamlit as st
import pandas as pd
import re
from rapidfuzz import fuzz
import statistics

# ================= CONFIG =================
FUZZY_THRESHOLD = 88
OUTLIER_LIMIT = 0.2

# ================= HELPERS =================
def normalize(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^\w\s]", "", name)
    noise = [
        "ltd", "limited", "pvt", "private",
        "unlisted", "pre ipo", "pre-ipo",
        "shares", "share"
    ]
    for n in noise:
        name = name.replace(n, "")
    return re.sub(r"\s+", " ", name).strip()

def build_company_registry(names):
    """
    Create stable canonical company list
    """
    canonicals = []

    for n in names:
        matched = False
        for c in canonicals:
            if fuzz.token_sort_ratio(n, c) >= FUZZY_THRESHOLD:
                matched = True
                break
        if not matched:
            canonicals.append(n)

    return canonicals

def map_to_canonical(norm_name, canonicals):
    for c in canonicals:
        if fuzz.token_sort_ratio(norm_name, c) >= FUZZY_THRESHOLD:
            return c
    return norm_name

def lowest_reliable(subset: pd.DataFrame) -> pd.Series:
    if len(subset) == 1:
        return subset.iloc[0]

    prices = subset["price"].tolist()
    median = statistics.median(prices)

    filtered = subset[
        subset["price"].apply(lambda p: abs(p - median) / median < OUTLIER_LIMIT)
    ]

    if filtered.empty:
        filtered = subset

    return filtered.loc[filtered["price"].idxmin()]

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page = "market"

# ================= LOAD DATA =================
df = pd.read_csv("data.csv")

df["normalized"] = df["share_name"].apply(normalize)

# build stable company registry FIRST
canonical_list = build_company_registry(df["normalized"].unique())

df["Company"] = df["normalized"].apply(
    lambda x: map_to_canonical(x, canonical_list)
)

# ================= MARKET PAGE =================
if st.session_state.page == "market":

    st.set_page_config(page_title="Unlisted Shares Market", layout="wide")

    st.title("Unlisted Shares – Dealer Market")
    st.caption("Live dealer-reported prices. No analysis applied.")

    market_df = (
        df[["Company", "dealer", "price", "date"]]
        .rename(columns={
            "dealer": "Dealer",
            "price": "Price",
            "date": "Last Updated"
        })
        .sort_values(["Company", "Price"])
    )

    st.dataframe(market_df, width="stretch")

    st.markdown("---")

    if st.button("Calculate Lowest Prices"):
        st.session_state.page = "analysis"
        st.rerun()

# ================= ANALYSIS PAGE =================
elif st.session_state.page == "analysis":

    st.set_page_config(page_title="Lowest Prices", layout="wide")

    st.title("Lowest Reliable Price by Company")
    st.caption("Calculated on demand using validated dealer prices")

    results = []

    for company in df["Company"].unique():
        subset = df[df["Company"] == company]
        best = lowest_reliable(subset)

        results.append({
            "Company": company.title(),
            "Cheapest Dealer": best["dealer"],
            "Lowest Price": best["price"],
            "Last Updated": best["date"]
        })

    analysis_df = (
        pd.DataFrame(results)
        .sort_values("Company")
    )

    st.dataframe(analysis_df, width="stretch")

    st.markdown("---")

    if st.button("Back to Market View"):
        st.session_state.page = "market"
        st.rerun()
