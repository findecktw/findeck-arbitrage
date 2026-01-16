import streamlit as st

# ==============================
# Page Config（只會影響瀏覽器分頁）
# ==============================
st.set_page_config(
    page_title="FinDeck｜借貸套利計算機",
    page_icon="📊",
    layout="wide"
)

# ==============================
# Session State 初始化
# ==============================
def init_session_state():
    if "loans" not in st.session_state:
        st.session_state.loans = []

    if "investments" not in st.session_state:
        st.session_state.investments = []

init_session_state()

# ==============================
# Header 區塊（只出現一次）
# ==============================
st.title("📊 借貸套利計算機")
st.caption("試算不同資金成本與投資報酬情境下的套利可行性")

st.divider()

# ==============================
# ① 資金來源（借貸）
# ==============================
st.header("① 資金來源（借貸）")

col1, col2, col3 = st.columns(3)

with col1:
    loan_type = st.selectbox(
        "借貸類型",
        ["房貸增貸", "信用貸款", "保單借款", "其他"]
    )

with col2:
    loan_amount = st.number_input(
        "借款金額",
        min_value=0,
        step=10000,
        value=0
    )

with col3:
    loan_rate = st.number_input(
        "年利率 (%)",
        min_value=0.0,
        step=0.01,
        format="%.2f"
    )

loan_years = st.number_input(
    "年期（年）",
    min_value=1,
    step=1,
    value=1
)

if st.button("➕ 新增借貸"):
    st.session_state.loans.append({
        "type": loan_type,
        "amount": loan_amount,
        "rate": loan_rate,
        "years": loan_years
    })
    st.success("借貸已加入")

# ==============================
# 借貸清單顯示
# ==============================
if st.session_state.loans:
    st.subheader("📄 已加入的借貸條件")
    st.dataframe(st.session_state.loans, use_container_width=True)

st.divider()

# ==============================
# ② 資金運用（投資）
# （先留結構，下一步會補）
# ==============================
st.header("② 資金運用（投資）")
st.info("投資模組即將完成（下一步）")

st.divider()

# ==============================
# ③ 套利試算結果
# ==============================
st.header("③ 套利結果分析")
st.warning("尚未計算，請先加入借貸與投資條件")
