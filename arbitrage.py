import streamlit as st

st.set_page_config(
    page_title="FinDeck｜借貸套利計算機",
    page_icon="📊",
    layout="wide"
)

st.title("借貸套利計算機")

# =========================
# 狀態初始化
# =========================
if "loans" not in st.session_state:
    st.session_state.loans = []

if "investments" not in st.session_state:
    st.session_state.investments = []

st.title("借貸套利計算機")

st.caption("試算不同資金成本與投資報酬下的套利可行性")

# =========================
# 1️⃣ 資金來源（借貸）
# =========================
st.subheader("① 資金來源（借貸）")

with st.form("add_loan"):
    loan_type = st.selectbox("借貸類型", ["房貸增貸", "信貸", "股票質押", "其他"])
    amount = st.number_input("借款金額", min_value=0, step=100_000)
    rate = st.number_input("年利率 (%)", min_value=0.0, step=0.1)
    years = st.number_input("年期 (年)", min_value=1, max_value=40)
    repay = st.radio("還款方式", ["本利攤還", "只繳息"], horizontal=True)

    if st.form_submit_button("加入借貸"):
        st.session_state.loans.append({
            "amount": amount,
            "rate": rate,
            "years": years,
            "repay": repay
        })

if st.session_state.loans:
    for i, l in enumerate(st.session_state.loans):
        st.write(
            f"• ${l['amount']:,}｜{l['rate']}%｜{l['years']} 年｜{l['repay']}"
        )
        if st.button("刪除", key=f"del_loan_{i}"):
            st.session_state.loans.pop(i)
            st.rerun()

# =========================
# 2️⃣ 資金去向（投資）
# =========================
st.subheader("② 資金去向（投資）")

with st.form("add_invest"):
    invest_type = st.selectbox("投資標的", ["ETF", "股票", "債券", "其他"])
    invest_amount = st.number_input("投入金額", min_value=0, step=100_000)
    roi = st.number_input("預期年報酬率 (%)", min_value=0.0, step=0.1)

    if st.form_submit_button("加入投資"):
        st.session_state.investments.append({
            "amount": invest_amount,
            "roi": roi
        })

if st.session_state.investments:
    for i, inv in enumerate(st.session_state.investments):
        st.write(
            f"• ${inv['amount']:,}｜{inv['roi']}%"
        )
        if st.button("刪除", key=f"del_inv_{i}"):
            st.session_state.investments.pop(i)
            st.rerun()

# =========================
# 3️⃣ 核心計算邏輯
# =========================
total_loan = sum(l["amount"] for l in st.session_state.loans)
total_invest = sum(i["amount"] for i in st.session_state.investments)

# 借貸成本
monthly_payment = 0
weighted_loan_rate = 0

for l in st.session_state.loans:
    p = l["amount"]
    r = l["rate"] / 100 / 12
    n = l["years"] * 12

    if l["repay"] == "本利攤還" and r > 0:
        pmt = p * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    else:
        pmt = p * r

    monthly_payment += pmt
    weighted_loan_rate += p * l["rate"]

if total_loan > 0:
    weighted_loan_rate /= total_loan

# 投資報酬
annual_return = sum(i["amount"] * i["roi"] / 100 for i in st.session_state.investments)
monthly_income = annual_return / 12

weighted_roi = 0
if total_invest > 0:
    weighted_roi = sum(i["amount"] * i["roi"] for i in st.session_state.investments) / total_invest

# =========================
# 4️⃣ 結果輸出
# =========================
st.divider()
st.subheader("📊 套利結果")

spread = weighted_roi - weighted_loan_rate
net_cashflow = monthly_income - monthly_payment

c1, c2, c3, c4 = st.columns(4)
c1.metric("借貸成本", f"{weighted_loan_rate:.2f}%")
c2.metric("投資報酬", f"{weighted_roi:.2f}%")
c3.metric("利差", f"{spread:.2f}%")
c4.metric("每月現金流", f"${int(net_cashflow):,}")

if spread <= 0:
    st.error("借貸成本高於投資報酬，套利不可行")
elif net_cashflow < 0:
    st.warning("利差為正，但現金流為負，需自行補貼")
else:
    st.success("套利結構健康，可產生正向現金流")
