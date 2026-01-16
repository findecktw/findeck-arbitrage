import streamlit as st
import math

# =========================
# 核心邏輯 (CFP 專業級運算)
# =========================
def calculate_monthly_payment(principal, annual_rate, years, method):
    """
    計算每月還款金額 (PMT)
    """
    if principal <= 0:
        return 0.0
    
    monthly_rate = (annual_rate / 100) / 12
    months = years * 12

    if method == "只繳息不還本":
        # 每月只繳利息
        return principal * monthly_rate
    else:
        # 本利均攤 (PMT 公式)
        if monthly_rate == 0:
            return principal / months
        else:
            # PMT = P * (r * (1+r)^n) / ((1+r)^n - 1)
            pmt = principal * (monthly_rate * math.pow(1 + monthly_rate, months)) / (math.pow(1 + monthly_rate, months) - 1)
            return pmt

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="FinDeck 借貸套利計算機",
    page_icon="💰",
    layout="centered", # 改為 centered 讓視覺更集中，像個 App
    initial_sidebar_state="collapsed"
)

# =========================
# UI/UX: 專業極簡風格 CSS (修復黑色區塊問題)
# =========================
st.markdown("""
<style>
    /* 全站背景：維持乾淨的淡灰/白 */
    .stApp {
        background-color: #F8F9FA;
    }

    /* 隱藏預設選單與 Footer */
    #MainMenu, header, footer {visibility: hidden;}

    /* 卡片式容器風格 */
    div.block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    /* === 關鍵修復：Expander (展開選單) === */
    /* 移除原本的深藍色背景，改為極簡白底 + 邊框 */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #E0E0E0;
        margin-bottom: 1rem;
    }
    
    div[data-testid="stExpander"] > details > summary {
        color: #333333 !important; /* 文字改為深灰 */
        font-weight: 600;
        border-radius: 8px;
    }
    
    div[data-testid="stExpander"] > details > summary:hover {
        color: #00c49a !important; /* 滑鼠懸停變色 */
        background-color: #F0FDF9;
    }

    /* 內容區域背景 */
    div[data-testid="stExpanderDetails"] {
        border-top: 1px solid #F0F0F0;
    }

    /* === 輸入框優化 === */
    /* 讓輸入框標題小一點，比較精緻 */
    label {
        font-size: 0.85rem !important;
        color: #555 !important;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF;
        border-color: #E0E0E0;
    }
    
    /* 修正輸入框內的數字增減按鈕顏色 */
    div[data-testid="stNumberInput"] button {
        color: #555;
    }

    /* === 按鈕優化 === */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        background-color: #0a2342; /* FinDeck 品牌藍 */
        color: white;
        border: none;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #00c49a; /* 品牌綠 */
        color: white;
        border: none;
    }

    /* === 結果卡片 === */
    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00c49a;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-top: 20px;
    }
    .metric-label { font-size: 0.9rem; color: #666; }
    .metric-value { font-size: 1.5rem; font-weight: bold; color: #333; }
    .metric-sub { font-size: 0.8rem; color: #888; }
</style>
""", unsafe_allow_html=True)

# =========================
# App Header
# =========================
st.markdown("<h2 style='text-align: center; color: #0a2342;'>💰 FinDeck 套利計算機</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 0.9rem;'>現金流與槓桿風險評估系統</p>", unsafe_allow_html=True)

# 初始化 Session State
if "loans" not in st.session_state: st.session_state.loans = []
if "investments" not in st.session_state: st.session_state.investments = []

# =========================
# 1. 資金來源 (借貸)
# =========================
with st.expander("Step 1: 設定資金來源 (借貸)", expanded=(len(st.session_state.loans)==0)):
    c1, c2 = st.columns(2)
    loan_type = c1.selectbox("借款類型", ["房貸增貸", "信用貸款", "股票質押", "保單借款"], key="l_type")
    repay = c2.radio("還款方式", ["只繳息不還本", "本利均攤"], horizontal=True, key="l_repay")
    
    c3, c4, c5 = st.columns(3)
    amount = c3.number_input("借款金額 (元)", 0, step=100000, value=1000000, key="l_amt")
    rate = c4.number_input("年利率 (%)", 0.0, 15.0, value=2.5, step=0.1, key="l_rate")
    years = c5.number_input("借款年期", 1, 40, value=20, key="l_years")

    if st.button("➕ 加入借貸條件"):
        st.session_state.loans.append({
            "type": loan_type, "amount": amount, "rate": rate, 
            "years": years, "repay": repay
        })
        st.rerun()

    # 顯示已加入的借貸
    if st.session_state.loans:
        st.markdown("---")
        for i, l in enumerate(st.session_state.loans):
            monthly_cost = calculate_monthly_payment(l['amount'], l['rate'], l['years'], l['repay'])
            st.caption(f"🔻 {l['type']} ${l['amount']:,} | 利率 {l['rate']}% | {l['repay']} | 月繳: ${monthly_cost:,.0f}")
            if st.button(f"刪除借貸 #{i+1}", key=f"del_loan_{i}"):
                st.session_state.loans.pop(i)
                st.rerun()

# =========================
# 2. 資金運用 (投資)
# =========================
with st.expander("Step 2: 設定投資標的", expanded=(len(st.session_state.loans)>0)):
    c1, c2 = st.columns(2)
    inv_type = c1.selectbox("投資工具", ["高股息 ETF", "美債 ETF", "房地產收租", "個股"], key="i_type")
    # 這裡加入 CFP 觀點：區分「現金流」與「資本利得」
    # 套利最怕「紙上富貴但沒錢繳貸款」，所以重點在現金殖利率
    
    c3, c4 = st.columns(2)
    inv_amount = c3.number_input("投入金額 (元)", 0, step=100000, value=amount if amount > 0 else 1000000, key="i_amt")
    yield_rate = c4.number_input("預估年配息率 (%)", 0.0, 20.0, value=5.0, step=0.5, help="能實際領到現金的殖利率", key="i_yield")
    
    if st.button("➕ 加入投資項目"):
        st.session_state.investments.append({
            "type": inv_type, "amount": inv_amount, "yield": yield_rate
        })
        st.rerun()

    if st.session_state.investments:
        st.markdown("---")
        for i, inv in enumerate(st.session_state.investments):
            annual_income = inv['amount'] * (inv['yield'] / 100)
            st.caption(f"💹 {inv['type']} ${inv['amount']:,} | 殖利率 {inv['yield']}% | 年領息: ${annual_income:,.0f}")
            if st.button(f"刪除投資 #{i+1}", key=f"del_inv_{i}"):
                st.session_state.investments.pop(i)
                st.rerun()

# =========================
# 3. 分析報告 (CFP 邏輯核心)
# =========================
if st.session_state.loans and st.session_state.investments:
    st.markdown("### 📊 套利結構分析報告")
    
    # 計算總和
    total_loan_amount = sum(l["amount"] for l in st.session_state.loans)
    total_inv_amount = sum(inv["amount"] for inv in st.session_state.investments)
    
    # 1. 現金流出 (年化)
    annual_loan_payment = sum(calculate_monthly_payment(l['amount'], l['rate'], l['years'], l['repay']) for l in st.session_state.loans) * 12
    
    # 2. 現金流入 (年化)
    annual_inv_income = sum(inv["amount"] * (inv["yield"] / 100) for inv in st.session_state.investments)
    
    # 3. 淨現金流
    net_annual_cashflow = annual_inv_income - annual_loan_payment
    net_monthly_cashflow = net_annual_cashflow / 12
    
    # 結果卡片顯示
    res_color = "#00c49a" if net_annual_cashflow >= 0 else "#e63946"
    res_text = "正現金流 (套利成功)" if net_annual_cashflow >= 0 else "負現金流 (風險極高)"
    
    st.markdown(f"""
    <div class="result-card" style="border-left: 5px solid {res_color};">
        <h3 style="margin-top:0; color:{res_color};">{res_text}</h3>
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
            <div>
                <div class="metric-label">每年需繳貸款 (現金流出)</div>
                <div class="metric-value" style="color:#e63946;">-${annual_loan_payment:,.0f}</div>
                <div class="metric-sub">約 ${annual_loan_payment/12:,.0f} / 月</div>
            </div>
            <div style="text-align:right;">
                <div class="metric-label">每年領取配息 (現金流入)</div>
                <div class="metric-value" style="color:#00c49a;">+${annual_inv_income:,.0f}</div>
                <div class="metric-sub">約 ${annual_inv_income/12:,.0f} / 月</div>
            </div>
        </div>
        <hr style="margin: 10px 0; border-top: 1px dashed #ddd;">
        <div style="text-align:center;">
            <div class="metric-label">每年淨獲利 (Net Cashflow)</div>
            <div class="metric-value" style="color:{res_color}; font-size: 2rem;">
                {'+' if net_annual_cashflow > 0 else ''}${net_annual_cashflow:,.0f}
            </div>
            <div class="metric-sub">每月淨 { '流入' if net_monthly_cashflow > 0 else '流出' } ${abs(net_monthly_cashflow):,.0f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CFP 專業警語
    if total_loan_amount > total_inv_amount:
         st.warning("⚠️ 注意：您的借款金額大於投資金額，這表示部分資金可能被用於消費或其他用途，會稀釋套利效果。")
    
    if any(l['repay'] == "本利均攤" for l in st.session_state.loans) and net_annual_cashflow < 0:
        st.error("🛑 重大風險提醒：您選擇了「本利均攤」，導致每月還款壓力大於配息收入。除非您有其他本業收入可覆蓋此缺口，否則不建議執行此套利。")

else:
    st.info("👋 請依序完成上方 Step 1 與 Step 2，系統將自動產生分析報告。")
