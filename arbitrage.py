import streamlit as st
import math

# =========================
# 1. 核心邏輯 (CFP 專業運算)
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
# 2. Page Config & UI 優化
# =========================
st.set_page_config(page_title="FinDeck 套利計算機", layout="centered")

# CSS 優化：增加輸入框邊框清楚度，修飾按鈕
st.markdown("""
<style>
    /* 全域設定 */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* 標題優化 */
    h1, h2, h3 {
        color: #0a2342;
        font-weight: 700;
    }
    
    /* === 輸入框強化 (解決看不清楚的問題) === */
    /* 輸入框外框 */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div {
        background-color: #FAFAFA !important;
        border: 1px solid #D1D5DB !important; /* 深灰色邊框 */
        border-radius: 6px !important;
        color: #333333 !important;
    }
    
    /* 當輸入框被點擊時，邊框變色 */
    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: #0a2342 !important;
        box-shadow: 0 0 0 2px rgba(10, 35, 66, 0.1) !important;
    }

    /* 輸入框內的數字/文字 */
    input {
        color: #0a2342 !important;
        font-weight: 500 !important;
    }
    
    /* 下拉選單文字 */
    div[data-baseweb="select"] span {
        color: #0a2342 !important;
    }

    /* === 數字增減按鈕 (+/-) === */
    /* 這是您截圖中黑掉的那兩塊，這裡強制修正 */
    button[kind="secondary"] {
        background-color: #F3F4F6 !important;
        border: 1px solid #D1D5DB !important;
        color: #0a2342 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #E5E7EB !important;
        color: #00c49a !important; /* hover 變綠色 */
    }

    /* === 主要按鈕 (加入項目) === */
    div.stButton > button {
        width: 100%;
        background-color: #0a2342 !important;
        color: #FFFFFF !important;
        border: none;
        padding: 0.6rem;
        font-weight: bold;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #00c49a !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* === Expander 外觀 === */
    div[data-testid="stExpander"] {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        background-color: #FFFFFF;
    }
    
    /* 隱藏預設選單 */
    #MainMenu, header, footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# =========================
# 3. App 介面佈局
# =========================
st.markdown("<h3 style='text-align: center; color: #0a2342;'>💰 FinDeck 借貸套利計算機</h3>", unsafe_allow_html=True)

if "loans" not in st.session_state: st.session_state.loans = []
if "investments" not in st.session_state: st.session_state.investments = []

# --- Step 1: 借貸 ---
with st.expander("Step 1: 設定資金來源 (借貸)", expanded=(len(st.session_state.loans)==0)):
    c1, c2 = st.columns(2)
    loan_type = c1.selectbox("借款類型", ["房貸增貸", "信用貸款", "股票質押", "保單借款"])
    repay = c2.radio("還款方式", ["只繳息不還本", "本利均攤"], horizontal=True)
    
    c3, c4, c5 = st.columns(3)
    amount = c3.number_input("借款金額", 0, step=100000, value=1000000)
    rate = c4.number_input("年利率 (%)", 0.0, 15.0, value=2.5, step=0.1)
    years = c5.number_input("借款年期", 1, 40, value=20)

    if st.button("➕ 加入借貸條件"):
        st.session_state.loans.append({"type": loan_type, "amount": amount, "rate": rate, "years": years, "repay": repay})
        st.rerun()

    # 顯示列表 (卡片式)
    for i, l in enumerate(st.session_state.loans):
        mc = calculate_monthly_payment(l['amount'], l['rate'], l['years'], l['repay'])
        st.info(f"🔻 {l['type']} ${l['amount']:,} | {l['rate']}% | 月繳: ${mc:,.0f}")
        # 如果需要刪除功能，可在此加入

# --- Step 2: 投資 ---
with st.expander("Step 2: 設定投資標的", expanded=(len(st.session_state.loans)>0)):
    c1, c2 = st.columns(2)
    inv_type = c1.selectbox("投資工具", ["高股息 ETF", "美債 ETF", "房地產收租", "個股"])
    
    c3, c4 = st.columns(2)
    inv_amount = c3.number_input("投入金額", 0, step=100000, value=amount if amount>0 else 1000000)
    yield_rate = c4.number_input("預估年配息率 (%)", 0.0, 20.0, value=5.0, step=0.5)
    
    if st.button("➕ 加入投資項目"):
        st.session_state.investments.append({"type": inv_type, "amount": inv_amount, "yield": yield_rate})
        st.rerun()

    for i, inv in enumerate(st.session_state.investments):
        inc = inv['amount'] * (inv['yield']/100)
        st.success(f"💹 {inv['type']} ${inv['amount']:,} | 殖利率 {inv['yield']}% | 年領息: ${inc:,.0f}")

# --- Step 3: 結果分析 ---
if st.session_state.loans and st.session_state.investments:
    st.markdown("---")
    
    annual_payment = sum(calculate_monthly_payment(l['amount'], l['rate'], l['years'], l['repay']) for l in st.session_state.loans) * 12
    annual_income = sum(inv["amount"] * (inv["yield"] / 100) for inv in st.session_state.investments)
    net_annual = annual_income - annual_payment
    
    # 風險評估邏輯
    is_positive = net_annual >= 0
    bg_color = "#ECFDF5" if is_positive else "#FEF2F2" # 極淡綠 vs 極淡紅
    border_color = "#059669" if is_positive else "#DC2626"
    title_text = "✅ 套利結構成立 (正現金流)" if is_positive else "⚠️ 風險警告 (負現金流)"
    
    result_html = f"""
    <div style="background-color: {bg_color}; padding: 24px; border-radius: 12px; border: 2px solid {border_color}; text-align: center;">
        <h3 style="color: {border_color}; margin-top: 0; font-weight: 800;">{title_text}</h3>
        
        <div style="display: flex; justify-content: space-around; margin: 20px 0; color: #4B5563;">
            <div>
                <small>年還款支出</small><br>
                <span style="color: #DC2626; font-weight: bold; font-size: 1.1em;">-${annual_payment:,.0f}</span>
            </div>
            <div style="border-left: 1px solid #D1D5DB;"></div>
            <div>
                <small>年投資收入</small><br>
                <span style="color: #059669; font-weight: bold; font-size: 1.1em;">+${annual_income:,.0f}</span>
            </div>
        </div>
        
        <hr style="border: 0; border-top: 1px dashed {border_color}; margin: 15px 0;">
        
        <div style="margin-top: 10px;">
            <small style="color: #6B7280;">預估年度淨現金流</small>
            <div style="font-size: 2em; font-weight: 900; color: {border_color};">
                {'+' if is_positive else ''}${net_annual:,.0f}
            </div>
            <small style="color: #6B7280;">(平均每月 { '+' if is_positive else ''}${net_annual/12:,.0f})</small>
        </div>
    </div>
    """
    st.markdown(result_html, unsafe_allow_html=True)
