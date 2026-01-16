import streamlit as st
import math

# =========================
# 1. 核心邏輯 (PMT 與 現金流計算)
# =========================
def calculate_monthly_payment(principal, annual_rate, years, method):
    if principal <= 0: return 0.0
    monthly_rate = (annual_rate / 100) / 12
    months = years * 12

    if method == "只繳息不還本":
        return principal * monthly_rate
    else: # 本利均攤
        if monthly_rate == 0: return principal / months
        return principal * (monthly_rate * math.pow(1 + monthly_rate, months)) / (math.pow(1 + monthly_rate, months) - 1)

# =========================
# 2. Page Config & CSS 強制修正
# =========================
st.set_page_config(page_title="FinDeck 套利計算機", layout="centered")

# CSS 優化重點：
# 1. 強制 Input 文字為深灰 (#333)
# 2. 強制 Input 背景為純白
# 3. 增加輸入框邊框對比度
st.markdown("""
<style>
    /* 全域字體顏色強制修正 */
    .stApp, p, label, .stMarkdown, h1, h2, h3, li {
        color: #0a2342 !important;
    }

    /* 背景色 */
    .stApp {
        background-color: #F8F9FA !important;
    }

    /* === 輸入框 (Input Fields) 核心修正 === */
    /* 針對 Streamlit 的 Input 內部文字 */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] {
        background-color: #FFFFFF !important;
        border: 1px solid #ced4da !important;
        color: #333333 !important; /* 強制深色文字 */
    }
    
    /* 輸入框內的文字顏色 (包含 Placeholder) */
    input[type="number"], input[type="text"] {
        color: #333333 !important;
        background-color: transparent !important;
    }

    /* 修正 +/- 按鈕 */
    button[kind="secondary"] {
        background-color: #e9ecef !important;
        color: #333333 !important;
        border: none !important;
    }

    /* === 下拉選單 (Dropdown) === */
    div[data-baseweb="select"] span {
        color: #333333 !important;
    }
    /* 下拉選單展開後的選項 */
    ul[role="listbox"] li {
        color: #333333 !important;
        background-color: #FFFFFF !important;
    }

    /* === Expander (展開選單) === */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    div[data-testid="stExpander"] summary {
        color: #0a2342 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stExpander"] summary:hover {
        color: #00c49a !important;
    }

    /* === 按鈕樣式 === */
    div.stButton > button {
        width: 100%;
        background-color: #0a2342 !important;
        color: #FFFFFF !important;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #00c49a !important;
        color: #FFFFFF !important;
    }
    
    /* 隱藏 Streamlit 預設選單 */
    #MainMenu, header, footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# =========================
# 3. 介面佈局 (UI Layout)
# =========================
st.markdown("<h3 style='text-align: center;'>💰 FinDeck 借貸套利計算機</h3>", unsafe_allow_html=True)

# Session State
if "loans" not in st.session_state: st.session_state.loans = []
if "investments" not in st.session_state: st.session_state.investments = []

# --- Step 1: 借貸 ---
with st.expander("Step 1: 設定資金來源 (借貸)", expanded=(len(st.session_state.loans)==0)):
    c1, c2 = st.columns(2)
    loan_type = c1.selectbox("借款類型", ["房貸增貸", "信用貸款", "股票質押", "保單借款"], key="l_type")
    repay = c2.radio("還款方式", ["只繳息不還本", "本利均攤"], horizontal=True, key="l_repay")
    
    c3, c4, c5 = st.columns(3)
    amount = c3.number_input("借款金額", 0, step=100000, value=1000000, key="l_amt")
    rate = c4.number_input("年利率 (%)", 0.0, 15.0, value=2.5, step=0.1, key="l_rate")
    years = c5.number_input("借款年期", 1, 40, value=20, key="l_years")

    if st.button("➕ 加入借貸條件"):
        st.session_state.loans.append({"type": loan_type, "amount": amount, "rate": rate, "years": years, "repay": repay})
        st.rerun()

    # 顯示列表
    for i, l in enumerate(st.session_state.loans):
        mc = calculate_monthly_payment(l['amount'], l['rate'], l['years'], l['repay'])
        st.info(f"🔻 {l['type']} ${l['amount']:,} | 利率 {l['rate']}% | 月繳: ${mc:,.0f}")

# --- Step 2: 投資 ---
with st.expander("Step 2: 設定投資標的", expanded=(len(st.session_state.loans)>0)):
    c1, c2 = st.columns(2)
    inv_type = c1.selectbox("投資工具", ["高股息 ETF", "美債 ETF", "房地產收租", "個股"], key="i_type")
    inv_amount = c1.number_input("投入金額", 0, step=100000, value=amount if amount>0 else 1000000, key="i_amt")
    yield_rate = c2.number_input("預估年配息率 (%)", 0.0, 20.0, value=5.0, step=0.5, key="i_yield")
    
    if st.button("➕ 加入投資項目"):
        st.session_state.investments.append({"type": inv_type, "amount": inv_amount, "yield": yield_rate})
        st.rerun()

    for i, inv in enumerate(st.session_state.investments):
        inc = inv['amount'] * (inv['yield']/100)
        st.success(f"💹 {inv['type']} ${inv['amount']:,} | 殖利率 {inv['yield']}% | 年領息: ${inc:,.0f}")

# --- Step 3: 結果分析 ---
if st.session_state.loans and st.session_state.investments:
    st.markdown("---")
    
    # 計算邏輯
    annual_payment = sum(calculate_monthly_payment(l['amount'], l['rate'], l['years'], l['repay']) for l in st.session_state.loans) * 12
    annual_income = sum(inv["amount"] * (inv["yield"] / 100) for inv in st.session_state.investments)
    net_annual = annual_income - annual_payment
    
    # 樣式定義
    card_color = "#d1fae5" if net_annual >= 0 else "#fee2e2" # 淺綠 vs 淺紅背景
    text_color = "#065f46" if net_annual >= 0 else "#991b1b" # 深綠 vs 深紅文字
    status = "✅ 正現金流 (套利可行)" if net_annual >= 0 else "⚠️ 負現金流 (風險極高)"
    
    st.markdown(f"""
    <div style="background-color: {card_color}; padding: 20px; border-radius: 10px; border: 1px solid {text_color};">
        <h3 style="color: {text_color}; margin-top:0;">{status}</h3>
        <p style="color: #333; margin-bottom: 5px;">年現金流出 (還款): <b>-${annual_payment:,.0f}</b></p>
        <p style="color: #333; margin-bottom: 5px;">年現金流入 (配息): <b>+${annual_income:,.0f}</b></p>
        <hr style="border-top: 1px solid {text_color}; opacity: 0.3;">
        <h2 style="color: {text_color}; margin:0;">淨利: ${net_annual:,.0f} / 年</h2>
        <small style="color: #555;">(平均每月 ${net_annual/12:,.0f})</small>
    </div>
    """, unsafe_allow_html=True)
