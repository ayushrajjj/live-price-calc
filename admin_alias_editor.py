import streamlit as st
from core.canonical_registry import CANONICAL_COMPANIES

st.set_page_config(page_title="Alias Manager", layout="wide")
st.title("Company Alias Manager")

company = st.selectbox("Select Company", list(CANONICAL_COMPANIES.keys()))
new_alias = st.text_input("Add new alias")

if st.button("Add Alias"):
    if new_alias:
        CANONICAL_COMPANIES[company].append(new_alias.lower())
        st.success(f"Alias '{new_alias}' added to {company}")
    else:
        st.warning("Alias cannot be empty")

st.subheader("Current Aliases")
st.write(CANONICAL_COMPANIES[company])
