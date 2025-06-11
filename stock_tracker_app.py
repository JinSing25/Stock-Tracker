import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Malaysia Stock Tracker", layout="wide")

st.title("🇲🇾 Malaysia Stock Tracker")
st.markdown("Track your KLSE holdings, get automatic P&L calculations, and indicator-based suggestions.")

# Session state to hold stock records
if "stocks" not in st.session_state:
    st.session_state.stocks = []
if "history" not in st.session_state:
    st.session_state.history = []

# Input section
st.sidebar.header("➕ Add New Stock")
code = st.sidebar.text_input("Stock Code (e.g., RHBBANK.KL)").strip().upper()
qty = st.sidebar.number_input("Quantity", min_value=1, step=1)
buy_price = st.sidebar.number_input("Buy Price (RM)", min_value=0.01, step=0.01)
add = st.sidebar.button("Add to Portfolio")

if add and code and qty > 0 and buy_price > 0:
    st.session_state.stocks.append({"code": code, "qty": qty, "buy_price": buy_price})
    st.sidebar.success(f"{code} added.")

# Display portfolio
if st.session_state.stocks:
    st.subheader("📊 Portfolio Overview")
    rows = []
    for stock in st.session_state.stocks:
        ticker = yf.Ticker(stock["code"])
        data = ticker.history(period="1d")
        if not data.empty:
            current_price = data["Close"].iloc[-1]
            amount = stock["qty"]
            buy_cost = stock["buy_price"]
            fees = max(0.08/100 * amount * buy_cost, 8) + (amount * buy_cost // 1000) + 0.03/100 * amount * buy_cost
            pnl = (current_price - buy_cost) * amount
            pnl_pct = (current_price - buy_cost) / buy_cost * 100
            rows.append([stock["code"], amount, buy_cost, round(current_price, 2),
                         round(pnl, 2), round(pnl_pct, 2)])
    df = pd.DataFrame(rows, columns=["Code", "Qty", "Buy Price", "Now", "P&L (RM)", "P&L (%)"])
    st.dataframe(df, use_container_width=True)

# Sell section
st.sidebar.header("💸 Sell Stock")
sell_code = st.sidebar.selectbox("Select Code", [s["code"] for s in st.session_state.stocks] + [""])
sell_price = st.sidebar.number_input("Sell Price (RM)", min_value=0.01, step=0.01)
sell_btn = st.sidebar.button("Sell and Record")

if sell_btn and sell_code and sell_price > 0:
    stock = next((s for s in st.session_state.stocks if s["code"] == sell_code), None)
    if stock:
        pnl = (sell_price - stock["buy_price"]) * stock["qty"]
        st.session_state.history.append({**stock, "sell_price": sell_price, "pnl": pnl})
        st.session_state.stocks = [s for s in st.session_state.stocks if s["code"] != sell_code]
        st.sidebar.success(f"{sell_code} sold and recorded.")

# History
if st.session_state.history:
    st.subheader("📁 Trade History")
    h = st.session_state.history
    dfh = pd.DataFrame(h)
    dfh["P&L"] = dfh["pnl"].round(2)
    st.dataframe(dfh[["code", "qty", "buy_price", "sell_price", "P&L"]], use_container_width=True)