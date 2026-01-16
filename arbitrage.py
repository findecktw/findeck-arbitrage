import streamlit as st
import pandas as pd
import math

# =========================
# Brand Style
# =========================
st.set_page_config(
    page_title="FinDeck 借貸套利計算機",
    layout="wide"
)

st.markdown("""
<style>
body {
    background-color: #f5f7fa;
}
h1, h2, h3 {
    color: #0a2342;
}
p, label, div {
    color: #555555;
}
.stButton>button {
    background-color: #00c49a;
    color: white;
    border-radius: 6px;
    border: none;
}
.stButton>button:hover {
    background-color: #00b08a;
}
[data-testid="stSidebar"] {
    background-color: #0a2342;
}
</style>
""", unsafe_allow_html=True)

# =========================
# Title
# =========================
st.title("📊 FinDeck 借貸套利計算機")
st.caption("專為槓桿投資、現金流管理與套利決策設計")

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
def annuity_payment(principal, rate, years):
    r = rate / 100 / 12
    n = years * 12
    return principal * r * (1 + r)**n / ((1 + r)**n - 1)

# =========================
# 1️⃣ Borrowing Section
# =========================
st.header("① 資金來源（借貸）")

with st.expander("➕ 新增借貸條件", expanded=True):
    col1, col2, col3, col4 = st.columns(4)

    loan_type = col1.selectbox(
        "借款類型",
        ["信用貸款", "房貸", "房屋增貸", "保單借款", "其他"]
    )
    amount = col2.number_input("借款金額", min_value=0, step=100000)
    rate = col3.number_input("年利率 (%)", min_value=0.0, step=0.1)
    years = col4.number_input("年期（年）", min_value=1, step=1)

    repay_type = st.radio(
        "還款方式",
        ["本利均攤", "只繳息不還本"],
        horizontal=True
    )

    if st.button("加入借貸"):
        st.session_state.loans.append({
            "type": loan_type,
            "amount": amount,
            "rate": rate,
            "years": years,
            "repay": repay_type
        })

# =========================
# Loan Summary
# =========================
if st.session_state.loans:
    loan_rows = []
    total_monthly_payment = 0
    total_annual_interest = 0

    for loan in st.session_state.loans:
        if loan["repay"] == "本利均攤":
            monthly = annuity_payment(loan["amount"], loan["rate"], loan["years"])
            annual_interest = monthly * 12 - loan["amount"] / loan["years"]
        else:
            monthly = loan["amount"] * loan["rate"] / 100 / 12
            annual_interest = loan["amount"] * loan["rate"] / 100

        total_monthly_payment += monthly
        total_annual_interest += annual_interest

        loan_rows.append({
            "借款類型": loan["type"],
            "金額": loan["amount"],
            "利率 (%)": loan["rate"],
            "年期": loan["years"],
            "還款方式": loan["repay"],
            "每月還款": round(monthly, 0)
        })

    st.subheader("已加入的借貸條件")
    st.dataframe(pd.DataFrame(loan_rows), use_container_width=True)

# =========================
# 2️⃣ Investment Section
# =========================
st.header("② 資金運用（投資）")

with st.expander("➕ 新增投資項目", expanded=True):
    col1, col2, col3, col4 = st.columns(4)

    invest_type = col1.selectbox(
        "投資類型",
        ["股票", "股票ETF", "債券ETF", "債券", "保險", "房地產"]
    )
    invest_amount = col2.number_input("投入金額", min_value=0, step=100000)
    return_rate = col3.number_input("預期年化報酬率 (%)", min_value=0.0, step=0.5)
    cash_yield = col4.number_input("年配息 / 現金流 (%)", min_value=0.0, step=0.5)

    if st.button("加入投資"):
        st.session_state.investments.append({
            "type": invest_type,
            "amount": invest_amount,
            "return": return_rate,
            "yield": cash_yield
        })

# =========================
# Investment Summary
# =========================
if st.session_state.investments:
    invest_rows = []
    total_invest_return = 0
    total_cashflow = 0

    for inv in st.session_state.investments:
        annual_return = inv["amount"] * inv["return"] / 100
        annual_cash = inv["amount"] * inv["yield"] / 100

        total_invest_return += annual_return
        total_cashflow += annual_cash

        invest_rows.append({
            "投資類型": inv["type"],
            "金額": inv["amount"],
            "年化報酬 (%)": inv["return"],
            "配息率 (%)": inv["yield"],
            "年現金流": round(annual_cash, 0)
        })

    st.subheader("已加入的投資項目")
    st.dataframe(pd.DataFrame(invest_rows), use_container_width=True)

# =========================
# 3️⃣ Arbitrage Analysis
# =========================
st.header("③ 套利結果分析")

if st.session_state.loans and st.session_state.investments:
    net_cashflow = total_cashflow - total_annual_interest
    arbitrage_spread = (
        (total_invest_return / sum(l["amount"] for l in st.session_state.loans)) * 100
        - (total_annual_interest / sum(l["amount"] for l in st.session_state.loans)) * 100
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("年投資報酬", f"{total_invest_return:,.0f}")
    col2.metric("年利息成本", f"{total_annual_interest:,.0f}")
    col3.metric("年淨現金流", f"{net_cashflow:,.0f}")

    st.markdown(f"""
### 🔍 顧問分析結論
- 年化套利差：約 **{arbitrage_spread:.2f}%**
- 此結構{'可行' if net_cashflow > 0 else '存在現金流壓力'}
- 建議檢視 **利率變動風險與投資波動**
""")
else:
    st.info("請先加入借貸與投資條件以進行分析")
