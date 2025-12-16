import streamlit as st
from kiteconnect import KiteConnect
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 🔁 Auto-refresh every 5 seconds
count = st_autorefresh(interval=5*1000, limit=None, key="datarefresh")

# 🔐 Credentials — replace with your real ones
API_KEY = "5sglhryo8fynoqi7"
ACCESS_TOKEN = "xoM2x8Ty6PFEMmUiSYab17eroXBVWDsC"

st.set_page_config(page_title="Zerodha Positions", layout="wide")
st.title("📊 Zerodha Open Positions")

# Refresh button (manual override)
if st.button("🔄 Refresh Now"):
    st.experimental_rerun()

# Initialize Kite
kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

# Fetch positions
positions = kite.positions()["net"]

rows = []
total_pnl = 0.0

for p in positions:
    if p["quantity"] != 0:
        pnl = round(p["pnl"], 2)
        total_pnl += pnl
        rows.append({
            "Symbol": p["tradingsymbol"],
            "Quantity": p["quantity"],
            "Avg Price": round(p["average_price"], 2),
            "P&L": pnl
        })

# --- LIVE CHART: P&L history ---
if "pnl_history" not in st.session_state:
    st.session_state.pnl_history = []

st.session_state.pnl_history.append(total_pnl)

# Optional: limit history length
if len(st.session_state.pnl_history) > 500:
    st.session_state.pnl_history.pop(0)

# Display total P&L
if rows:
    pnl_color = "green" if total_pnl >= 0 else "red"
    st.markdown(
        f"## 🧮 Total MTM P&L: <span style='color:{pnl_color}'>₹{round(total_pnl,2)}</span>",
        unsafe_allow_html=True
    )
    
    # Show live P&L chart
    st.line_chart(st.session_state.pnl_history)

    # Build table
    df = pd.DataFrame(rows)

    def color_pnl(val):
        if val > 0:
            return "color: green"
        elif val < 0:
            return "color: red"
        return ""

    st.dataframe(df.style.applymap(color_pnl, subset=["P&L"]))
else:
    st.info("No open positions")



