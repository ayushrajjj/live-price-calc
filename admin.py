"""Admin upload: convert pasted WhatsApp-style price lines into a CSV

Features added for deploy readiness:
 - safer price parsing (handles commas and currency symbols)
 - saves to canonical pipeline file `data/raw_upload.csv` and a timestamped backup
 - ensures `data/` and `data/uploads/` exist
 - provides download button and preview
 - improved validation and user feedback
"""

from datetime import date
import io
import logging
from pathlib import Path
import re
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Admin – WhatsApp Upload", layout="wide")

st.title("Admin – Price Upload")
st.caption("Paste raw dealer messages (one per line). The system will convert them to CSV for the pipeline.")

# --------- SIMPLE AUTH (username/password) ---------
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    st.subheader("Admin Login")
    _username = st.text_input("Username")
    _password = st.text_input("Password", type="password")
    _login_clicked = st.button("Login")
    if _login_clicked:
        if _username == "admin" and _password == "admin":
            st.session_state.admin_authenticated = True
            st.success("Logged in")
        else:
            st.error("Invalid username or password")
    # stop further rendering for non-authenticated users
    if not st.session_state.admin_authenticated:
        st.stop()

# provide a logout button for authenticated users
if st.button("Logout"):
    st.session_state.admin_authenticated = False
    st.success("Logged out")

# ------ Config / Paths ------
DATA_DIR = Path("data")
RAW_UPLOAD_PATH = DATA_DIR / "raw_upload.csv"  # path used by transform.py
BACKUP_DIR = DATA_DIR / "uploads"

for p in (DATA_DIR, BACKUP_DIR):
    p.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("admin_upload")

# -------- Admin Input: single text area only --------
st.markdown("**Paste messages here (one per line).**\n\nOptionally include header lines at the top: `Dealer: NAME` and/or `Date: YYYY-MM-DD`. If absent, dealer will be set to `unknown` and date to today.")

raw_text = st.text_area(
    "Paste messages here (one per line)",
    height=360,
    placeholder=(
        "Optional header lines (top):\n"
        "Dealer: Precize\n"
        "Date: 2026-01-20\n\n"
        "Then one message per line, e.g.:\n"
        "BSE Invest @ 1,320\n"
        "CSK - 4,200\n"
        "Hexaware Tech 560\n"
    ),
)


def _sanitize_price_token(token: str) -> float:
    """Convert a matched price token into a float.

    Handles optional currency symbols and commas, e.g. '₹1,320' -> 1320.0
    """
    token = token.replace("₹", "").replace("$", "")
    token = token.replace(",", "")
    return float(token)


def parse_whatsapp_text(text: str) -> pd.DataFrame:
    """Parse pasted WhatsApp text into a DataFrame with columns:
    Dealer, Share Name, Price, Last Updated
    """
    rows = []
    # first, allow optional header lines at the very top to set dealer/date
    lines = text.splitlines()
    dealer = None
    trade_date_value = date.today()
    header_indexes = set()

    # inspect up to first 3 lines for headers like 'Dealer: Name' or 'Date: 2026-01-20'
    for i, raw_line in enumerate(lines[:3]):
        line = raw_line.strip()
        if not line:
            continue
        m = re.match(r"(?i)^\s*(dealer|from)\s*[:\-]\s*(.+)$", line)
        if m:
            dealer = m.group(2).strip()
            header_indexes.add(i)
            continue
        m2 = re.match(r"(?i)^\s*date\s*[:\-]\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})$", line)
        if m2:
            dstr = m2.group(1)
            try:
                if "-" in dstr:
                    trade_date_value = date.fromisoformat(dstr)
                else:
                    # assume DD/MM/YYYY
                    day, mon, yr = dstr.split("/")
                    trade_date_value = date(int(yr), int(mon), int(day))
                header_indexes.add(i)
            except Exception:
                logger.debug("failed to parse date header: %s", dstr)

    # build list of content lines after removing header lines
    content_lines = [l for idx, l in enumerate(lines) if idx not in header_indexes]

    # regex: currency optional, digits with optional commas and decimal
    price_rx = re.compile(r"[₹$]?\s*[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[₹$]?\d+(?:\.\d+)?")

    for raw_line in content_lines:
        line = raw_line.strip()
        if not line:
            continue

        # find all price-like tokens, take the last one as the price
        matches = price_rx.findall(line)
        if not matches:
            # skip lines with no numeric token
            logger.debug("no price found in line: %s", line)
            continue

        price_token = matches[-1]
        try:
            price = _sanitize_price_token(price_token)
        except ValueError:
            logger.exception("failed to parse price token: %s", price_token)
            continue

        # remove the price token from the line
        name_part = line
        # replace common separators with space and strip trailing price
        name_part = re.sub(r"[@\-–:|]\s*", " ", name_part)
        name_part = name_part.replace(price_token, " ")
        # remove leftover numbers (e.g. stray codes) and extra spaces
        name_part = re.sub(r"\d+(?:[,\.]\d+)*", "", name_part)
        name_part = re.sub(r"\s+", " ", name_part).strip()

        if not name_part:
            # fallback: if we couldn't extract a name, use placeholder
            name_part = "UNKNOWN"

        rows.append({
            "Dealer": (dealer or "unknown").strip(),
            "Share Name": name_part,
            "Price": float(price),
            "Last Updated": trade_date_value.strftime("%Y-%m-%d"),
        })

    if not rows:
        return pd.DataFrame(columns=["Dealer", "Share Name", "Price", "Last Updated"])

    return pd.DataFrame(rows)


# -------- Convert Button --------
if st.button("Convert Text to CSV"):

    if not raw_text or not raw_text.strip():
        st.error("Text is required. Paste messages into the single editor.")
    else:
        df = parse_whatsapp_text(raw_text)

        if df.empty:
            st.error("No valid data found. Check the format. Each line needs a numeric price.")
        else:
            # create a timestamped backup filename
            ts = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            # pick dealer from parsed rows for a safe filename (fallback to 'unknown')
            dealer_for_filename = df["Dealer"].iloc[0] if ("Dealer" in df.columns and not df["Dealer"].isnull().all()) else "unknown"
            safe_dealer = re.sub(r"[^a-z0-9_-]", "_", str(dealer_for_filename).lower())[:40]
            backup_name = f"raw_upload_{safe_dealer}_{ts}.csv"

            try:
                # canonical pipeline file (used by transform.py) - overwrite
                df.to_csv(RAW_UPLOAD_PATH, index=False)

                # also save a timestamped backup copy for audit
                backup_path = BACKUP_DIR / backup_name
                df.to_csv(backup_path, index=False)

                st.success(f"Text converted and saved to `{RAW_UPLOAD_PATH}`")
                st.info(f"Backup saved to: `{backup_path}`")

                st.subheader("Preview")
                st.dataframe(df, width="stretch")

                csv_bytes = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Parsed CSV",
                    data=csv_bytes,
                    file_name=f"parsed_upload_{ts}.csv",
                    mime="text/csv",
                )

            except Exception as exc:
                logger.exception("failed to save uploaded CSV")
                st.error(f"Failed to save CSV: {exc}")
