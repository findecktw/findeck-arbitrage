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
# 2. Page Config & 強力 CSS 修復
# =========================
st.set_page_config(page_title="FinDeck 套利計算機", layout="centered")

st.markdown("""
<style>
    /* 全域設定 */
    .stApp {
        background-color: #FFFFFF;
        color: #0a2342;
    }
    
    /* 隱藏右上角選單與 Footer */
    #MainMenu, header, footer {visibility: hidden;}

    /* === 1. 輸入框本體 (中間打數字的地方) === */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 6px !important;
        color: #333333 !important;
    }
    input { color: #0a2342 !important; font-weight: 500 !important; }

    /* === 2. 修正 +/- 按鈕 (Spinbuttons) === */
    /* 這是您截圖中黑掉的地方，強制改回淺灰色 */
    div[data-baseweb="spinbutton"] > div,
    div[data-baseweb="spinbutton"] button {
        background-color: #F3F4F6 !important; /* 淺灰底 */
        color: #0a2342 !important; /* 深藍字符 */
        border-color: #E5E7EB !important;
    }
    
    /* 滑鼠移過去 +/- 時 */
    div[data-baseweb="spinbutton"] button:hover {
        background-color: #E5E7EB !important;
        color: #00c49a !important; /* 變綠 */
    }
    
    /* 如果還有漏網之魚 (針對舊版元件) */
    button[kind="secondary"] {
        background-color: #F3F4F6 !important;
        color: #0a2342 !important;
        border: 1px solid #D1D5DB !important;
    }

    /* === 3. 修正「加入按鈕」字體顏色 === */
    div.stButton > button {
        width: 100%;
        background-color: #0a2342 !important;
        color: #FFFFFF !important; /* ★強制白色文字★ */
        border: none;
        padding: 0.6rem;
        font-weight: bold;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #00c49a !important;
        color: #FFFFFF !important; /* Hover時文字保持白色 */
        border: none !important;
    }
    
    /* === 4. 結果卡片優化 === */
    div[data-testid="stExpander"] {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        background-color: #FFFFFF;
        color: #0a2342;
    }
    
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

    for i, l in enumerate(st.session_state.loans):
        mc = calculate_monthly_payment(l['amount'], l['rate'], l['years'], l['repay'])
        st.markdown(f"""
        <div style="background-color:#F3F4F6; padding:8px 12px; border-radius:6px; margin-top:5px; border-left: 3px solid #0a2342; font-size:0.9rem;">
            <b>🔻 {l['type']}</b> | 金額 ${l['amount']:,} | 利率 {l['rate']}% | 月繳: <b>${mc:,.0f}</b>
        </div>
        """, unsafe_allow_html=True)

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
        st.markdown(f"""
        <div style="background-color:#ECFDF5; padding:8px 12px; border-radius:6px; margin-top:5px; border-left: 3px solid #00c49a; font-size:0.9rem;">
            <b>💹 {inv['type']}</b> | 金額 ${inv['amount']:,} | 殖利率 {inv['yield']}% | 年領息: <b>${inc:,.0f}</b>
        </div>
        """, unsafe_allow_html=True)

# --- Step 3: 結果分析 (HTML 縮排修復版) ---
if st.session_state.loans and st.session_state.investments:
    st.markdown("---")
    
    annual_payment = sum(calculate_monthly_payment(l['amount'], l['rate'], l['years'], l['repay']) for l in st.session_state.loans) * 12
    annual_income = sum(inv["amount"] * (inv["yield"] / 100) for inv in st.session_state.investments)
    net_annual = annual_income - annual_payment
    
    is_positive = net_annual >= 0
    bg_color = "#ECFDF5" if is_positive else "#FEF2F2" 
    border_color = "#059669" if is_positive else "#DC2626"
    text_color = "#047857" if is_positive else "#B91C1C"
    title_text = "✅ 套利結構成立 (正現金流)" if is_positive else "⚠️ 風險警告 (負現金流)"
    
    # 使用緊湊的 HTML 寫法避免 Markdown 誤判
    st.markdown(f"""
<div style="background-color: {bg_color}; padding: 20px; border-radius: 12px; border: 2px solid {border_color}; text-align: center;">
<h3 style="color: {text_color}; margin-top: 0;">{title_text}</h3>
<div style="display: flex; justify-content: space-around; margin: 15px 0; color: #4B5563;">
<div><small>年還款支出</small><br><span style="color: #DC2626; font-weight: bold; font-size: 1.1rem;">-${annual_payment:,.0f}</span></div>
<div style="border-left: 1px solid #ccc;"></div>
<div><small>年投資收入</small><br><span style="color: #059669; font-weight: bold; font-size: 1.1rem;">+${annual_income:,.0f}</span></div>
</div>
<hr style="border:0; border-top:1px dashed {border_color}; margin:10px 0;">
<div><small>預估年度淨現金流</small><div style="font-size: 2rem; font-weight: 900; color: {text_color};">{'+' if is_positive else ''}${net_annual:,.0f}</div></div>
</div>""", unsafe_allow_html=True)
