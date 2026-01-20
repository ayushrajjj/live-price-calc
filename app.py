# app.py

import streamlit as st
import pandas as pd

df = pd.read_csv("final_clean_data.csv")

st.set_page_config(page_title="Unlisted Share Prices", layout="wide")

st.title("Unlisted Share Prices")
st.caption("Clean, canonical dealer data")

st.dataframe(df, width="stretch")
