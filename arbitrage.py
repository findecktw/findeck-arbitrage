import streamlit as st
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
# Brand Theme (FIXED)
# =========================
st.markdown("""
<style>

/* =====================
   Global Background
===================== */
.stApp {
    background-color: #f5f7fa;
}

/* =====================
   Typography
===================== */
h1, h2, h3 {
    color: #0a2342;
}
p, label, span, div {
    color: #555555;
}

/* =====================
   Input / Select
===================== */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border: 1px solid #d0d5dd !important;
    border-radius: 6px !important;
}

input {
    background-color: #ffffff !important;
    color: #0a2342 !important;
}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within {
    border: 2px solid #00c49a !important;
}

/* =====================
   Dropdown Menu
===================== */
div[data-baseweb="popover"] {
    background-color: #ffffff !important;
    border-radius: 8px !important;
}

ul[role="listbox"] {
    background-color: #ffffff !important;
}

li[role="option"] {
    background-color: #ffffff !important;
    color: #0a2342 !important;
}

li[role="option"]:hover {
    background-color: #f0fdf9 !important;
}

li[aria-selected="true"] {
    background-color: #e6faf4 !important;
    font-weight: 600;
}

/* =====================
   Expander (新增條件)
===================== */
details > summary {
    background-color: #0a2342 !important;
    color: #ffffff !important;
    border-radius: 6px !important;
    padding: 10px 14px !important;
    font-weight: 600;
}

details[open] > summary {
    background-color: #0a2342 !important;
}

details > div {
    background-color: #f5f7fa !important;
    padding: 16px 8px 8px 8px !important;
}

/* =====================
   Number Input (+ -)
===================== */
div[data-baseweb="input"] button {
    background-color: #ffffff !important;
    color: #0a2342 !important;
    border-left: 1px solid #d0d5dd !important;
}

div[data-baseweb="input"] button:hover {
    background-color: #e6faf4 !important;
}

div[data-baseweb="spinbutton"] {
    background-color: #ffffff !important;
    border-radius: 6px !important;
}

/* =====================
   Buttons
===================== */
.stButton > button {
    background-color: #00c49a;
    color: #ffffff;
    border-radius: 6px;
    border: none;
}
.stButton > button:hover {
    background-color: #00b08a;
}

/* =====================
   Hide Streamlit UI
===================== */
header {visibility: hidden;}
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

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

if st.session_state.loans:
    st.subheader("已加入的借貸條件")
    for i, l in enumerate(st.session_state.loans):
        cols = st.columns([3,2,2,2,2,1])
        cols[0].write(l["type"])
        cols[1].write(f'{l["amount"]:,}')
        cols[2].write(f'{l["rate"]}%')
        cols[3].write(l["years"])
        cols[4].write(l["repay"])
        if cols[5].button("🗑", key=f"del_loan_{i}"):
            st.session_state.loans.pop(i)
            st.experimental_rerun()

# =========================
# ② Investment
# =========================
st.header("② 資金運用（投資）")

with st.expander("➕ 新增投資項目", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    inv_type = c1.selectbox("投資類型", ["股票", "股票ETF", "債券ETF", "債券", "保險", "房地產"])
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
# ③ Analysis
# =========================
st.header("③ 套利結果分析")

if st.session_state.loans and st.session_state.investments:
    interest = sum(l["amount"] * l["rate"] / 100 for l in st.session_state.loans)
    cashflow = sum(inv["amount"] * inv["yield"] / 100 for inv in st.session_state.investments)
    net = cashflow - interest

    c1, c2, c3 = st.columns(3)
    c1.metric("年利息成本", f"{interest:,.0f}")
    c2.metric("年現金流收入", f"{cashflow:,.0f}")
    c3.metric("年淨現金流", f"{net:,.0f}")

    if net > 0:
        st.success(
            f"此結構屬於「正現金流套利」，每年可產生約 {net:,.0f} 元自由現金流。\n\n"
            "建議持續關注利率風險與投資現金流穩定性。"
        )
    else:
        st.error(
            "此結構為負現金流，投資現金流不足以支應利息成本。\n\n"
            "建議降低借款成本或提高配息率。"
        )
else:
    st.info("請先加入借貸與投資條件，以進行套利分析")
