import streamlit as st
import pandas as pd
from datetime import date
import streamlit.components.v1 as components

# If someone visits /admin (path), redirect client-side to add ?admin=1 so the app handles it
components.html(
        """
        <script>
        (function(){
            try {
                const p = window.location.pathname || '/';
                // normalize trailing slash
                if (p.endsWith('/')) {
                    // remove trailing slash for comparison
                }
                if (p.endsWith('/admin') && !window.location.search.includes('admin=')) {
                    const newUrl = window.location.pathname + window.location.search + (window.location.search ? '&' : '?') + 'admin=1';
                    window.location.replace(newUrl);
                }
            } catch (e) {
                // noop
            }
        })();
        </script>
        """,
        height=0,
)

# Allow direct access to admin page via query param, e.g. ?admin=1
params = st.experimental_get_query_params()
if "admin" in params:
    # Import and call the admin page directly
    try:
        from admin import main as admin_main
        admin_main()
        st.stop()
    except Exception as exc:
        st.error(f"Failed to open admin page from query param: {exc}")
        st.stop()

# ---------------- PAGE CONFIG (MUST BE FIRST) ----------------
st.set_page_config(page_title="Unlisted Share Prices", layout="wide")

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "market"

# ---------------- LOAD CLEAN DATA ----------------
df = pd.read_csv("final_clean_data.csv")

# ================= MARKET VIEW (HOME) =================
if st.session_state.page == "market":

    st.title("Unlisted Share Prices – Market View")
    st.caption("Dealer-reported prices only.")

    # Small admin link for convenience (opens admin page in a new tab)
    st.markdown(
        '<p style="text-align:right"><a href="?admin=1" target="_blank">Open Admin Panel</a></p>',
        unsafe_allow_html=True,
    )

    # ---- SEARCH (ONLY ON MARKET PAGE) ----
    search = st.text_input("Search company (e.g. bse, studds, pharmeasy)")

    market_df = df[[
        "S.No",
        "Company",
        "Dealer",
        "Price",
        "Last Updated"
    ]]

    if search:
        market_df = market_df[
            market_df["Company"].str.lower().str.contains(search.lower())
        ]

    st.dataframe(market_df, width="stretch")

    st.markdown("---")

    if st.button("Calculate Lowest Prices"):
        st.session_state.page = "lowest"
        st.rerun()

# ================= LOWEST PRICE VIEW =================
elif st.session_state.page == "lowest":

    st.title("Lowest Price per Company")
    st.caption("Calculated on demand. One cheapest dealer per company.")

    results = []

    for company in df["Company"].unique():
        subset = df[df["Company"] == company]
        best_row = subset.loc[subset["Price"].idxmin()]

        results.append({
            "Company": company,
            "Cheapest Dealer": best_row["Dealer"],
            "Lowest Price": best_row["Price"],
            "Last Updated": best_row["Last Updated"]
        })

    lowest_df = pd.DataFrame(results).sort_values("Company")

    st.dataframe(lowest_df, width="stretch")

    # ---- Download CSV with DD-MM-YYYY suffix ----
    today_str = date.today().strftime("%d-%m-%Y")

    st.download_button(
        label="Download Lowest Prices (CSV)",
        data=lowest_df.to_csv(index=False),
        file_name=f"lowest_prices_{today_str}.csv",
        mime="text/csv"
    )

    st.markdown("---")

    if st.button("Back to Market View"):
        st.session_state.page = "market"
        st.rerun()
