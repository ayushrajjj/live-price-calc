import streamlit as st
import pandas as pd

MASTER_FILE = "master_shares.csv"

df = pd.read_csv(MASTER_FILE)

st.set_page_config(page_title="Master Share Editor", layout="wide")
st.title("Master Share Registry (Admin)")

st.dataframe(df, width="stretch")

st.markdown("### Add / Edit Company")

with st.form("add_company"):
    canonical = st.text_input("Canonical Company Name")
    core = st.text_input("Core Keyword (single word)")
    suffixes = st.text_input("Allowed Suffixes (comma separated)")
    lot = st.number_input("Minimum Lot Size", min_value=1)
    depo = st.text_input("Depository")

    submit = st.form_submit_button("Save")

    if submit:
        new_row = {
            "canonical_company": canonical,
            "core_keyword": core,
            "allowed_suffixes": suffixes,
            "min_lot": lot,
            "depository": depo
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(MASTER_FILE, index=False)
        st.success("Master updated. Restart apps.")
