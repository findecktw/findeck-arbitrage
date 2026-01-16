import streamlit as st
import pandas as pd
import math

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="FinDeck 借貸套利計算機",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# Force Brand Theme
# =========================
st.markdown("""
<style>
/* App Background */
.stApp {
    background-color: #f5f7fa;
}

/* Typography */
h1, h2, h3 {
    color: #0a2342;
}
p, label, span, div {
    color: #555555;
}

/* Inputs background */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background-color: #ffffff !important;
    border: 1px solid #d0d5dd;
    border-radius: 6px;
}

/* Input text */
input {
    color: #0a2342 !important;
    background-color: #ffffff !important;
}

/* Focus state */
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="input"] > div:focus-within {
    border: 2px solid #00c49a !important;
}

/* Buttons */
.stButton > button {
    background-color: #00c49a;
    color: white;
    border-radius: 6px;
    border: none;
}
.stButton > button:hover {
    background-color: #00b08a;
}

/* Tables */
.stDataFrame {
    background-color: #ffffff;
}
</style>
""", unsafe_allow_html=True)


# =========================
# Title
# =========================
st.title("📊 FinDeck 借貸套利計算機")
st.caption("以專業現金流與槓桿視角，評估你的套利結構是否成立")

# =========================
# Session State
# =========================
if "loans" not in st.session_state:
    st.session_state.loans = []

if "investments" not in st.session_state:
    st.session_state.investments = []

# =========================
# Functions
# =========================
def annuity_payment(p, r, y):
    r = r / 100 / 12
    n = y * 12
    return p * r * (1 + r)**n / ((1 + r)**n - 1)

# =========================
# ① Borrowing
# =========================
st.header("① 資金來源（借貸）")

with st.expander("➕ 新增借貸條件", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    loan_type = c1.selectbox("借款類型", ["房貸", "信用貸款", "保單借款", "其他"])
    amount = c2.number_input("借款金額", 0, step=100000)
    rate = c3.number_input("年利率 (%)", 0.0, step=0.1)
    years = c4.number_input("年期", 1, step=1)

    repay = st.radio("還款方式", ["本利均攤", "只繳息不還本"], horizontal=True)

    if st.button("加入借貸"):
        st.session_state.loans.append({
            "type": loan_type,
            "amount": amount,
            "rate": rate,
            "years": years,
            "repay": repay
        })

# =========================
# Borrowing Table
# =========================
if st.session_state.loans:
    st.subheader("已加入的借貸條件")

    for i, l in enumerate(st.session_state.loans):
        col = st.columns([3,2,2,2,2,1])
        col[0].write(l["type"])
        col[1].write(f'{l["amount"]:,}')
        col[2].write(f'{l["rate"]}%')
        col[3].write(l["years"])
        col[4].write(l["repay"])
        if col[5].button("🗑", key=f"del_loan_{i}"):
            st.session_state.loans.pop(i)
            st.experimental_rerun()

# =========================
# ② Investment
# =========================
st.header("② 資金運用（投資）")

with st.expander("➕ 新增投資項目", expanded=True):
    c1, c2, c3, c4 = st.columns(4)

    inv_type = c1.selectbox(
        "投資類型",
        ["股票", "股票ETF", "債券ETF", "債券", "保險", "房地產"]
    )
    inv_amount = c2.number_input("投入金額", 0, step=100000)
    growth = c3.number_input("資本增值率 (%)", 0.0, step=0.5)
    yield_rate = c4.number_input("現金流 / 配息率 (%)", 0.0, step=0.5)

    if st.button("加入投資"):
        st.session_state.investments.append({
            "type": inv_type,
            "amount": inv_amount,
            "growth": growth,
            "yield": yield_rate
        })

# =========================
# Investment Table
# =========================
if st.session_state.investments:
    st.subheader("已加入的投資項目")

    for i, inv in enumerate(st.session_state.investments):
        total_return = inv["growth"] + inv["yield"]
        cashflow = inv["amount"] * inv["yield"] / 100

        col = st.columns([3,2,2,2,2,1])
        col[0].write(inv["type"])
        col[1].write(f'{inv["amount"]:,}')
        col[2].write(f'{inv["growth"]}%')
        col[3].write(f'{inv["yield"]}%')
        col[4].write(f'{cashflow:,.0f}')
        if col[5].button("🗑", key=f"del_inv_{i}"):
            st.session_state.investments.pop(i)
            st.experimental_rerun()

# =========================
# ③ Arbitrage Analysis
# =========================
st.header("③ 套利結果分析")

if st.session_state.loans and st.session_state.investments:

    total_interest = sum(
        l["amount"] * l["rate"] / 100
        for l in st.session_state.loans
    )

    total_cashflow = sum(
        inv["amount"] * inv["yield"] / 100
        for inv in st.session_state.investments
    )

    net_cashflow = total_cashflow - total_interest

    c1, c2, c3 = st.columns(3)
    c1.metric("年利息成本", f"{total_interest:,.0f}")
    c2.metric("年現金流收入", f"{total_cashflow:,.0f}")
    c3.metric("年淨現金流", f"{net_cashflow:,.0f}")

    st.divider()

    if net_cashflow > 0:
        st.success(
            f"此結構為「正現金流套利」，每年可產生約 "
            f"{net_cashflow:,.0f} 元自由現金流。\n\n"
            "⚠️ 建議留意：升息風險與投資現金流穩定度。"
        )
    else:
        st.error(
            "此套利結構為「負現金流」，"
            "代表目前投資現金流不足以支應利息成本。\n\n"
            "👉 建議調整：降低借款利率、提高配息率或縮小槓桿比例。"
        )
else:
    st.info("請先加入借貸與投資條件，以進行套利分析")

