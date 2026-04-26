import streamlit as st
import pandas as pd
import pdfplumber
import sqlite3
import bcrypt
import plotly.express as px
import re

# ---------- CONFIG ----------
st.set_page_config(page_title="Narang Expense Analyzer", layout="wide")

# ---------- PREMIUM UI ----------
st.markdown("""
<style>
html, body, [class*="css"] {
    background: linear-gradient(135deg, #0f0f0f, #1a1a2e);
    color: #ffffff;
}
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    margin-bottom: 20px;
}

.title {
    font-size: 36px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 20px;
}

.metric {
    font-size: 28px;
    font-weight: bold;
}

.stButton>button {
    background: linear-gradient(90deg, #6a11cb, #2575fc);
    border-radius: 12px;
    color: white;
    border: none;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">💰 Narang Expense Analyzer</div>', unsafe_allow_html=True)

# ---------- DB ----------
conn = sqlite3.connect("finance.db", check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password BLOB)")
c.execute("""CREATE TABLE IF NOT EXISTS transactions(
    username TEXT, month TEXT, desc TEXT, amt REAL, type TEXT, cat TEXT)""")
conn.commit()

# ---------- AUTH ----------
def create_user(u,p):
    hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users VALUES (?,?)", (u, hashed))
        conn.commit()
        return True
    except:
        return False

def login_user(u,p):
    c.execute("SELECT password FROM users WHERE username=?", (u,))
    data = c.fetchone()
    if data and bcrypt.checkpw(p.encode(), data[0]):
        return True
    return False

# ---------- CATEGORY ----------
def categorize(d):
    d = d.lower()
    if any(x in d for x in ["zepto","dominos","restaurant","cafe"]): return "Food & Dining"
    if any(x in d for x in ["petrol","fuel"]): return "Fuel"
    if any(x in d for x in ["railway","uber","ola"]): return "Travel"
    if any(x in d for x in ["amazon","flipkart"]): return "Shopping"
    if any(x in d for x in ["jio","airtel","bill","pspcl"]): return "Bills & Utilities"
    if any(x in d for x in ["sip","groww","mf"]): return "Investments"
    if any(x in d for x in ["loan","emi"]): return "EMI"
    if any(x in d for x in ["netflix","spotify"]): return "Subscriptions"
    return "Miscellaneous"

# ---------- PARSER ----------
def parse_pdf(file):
    rows = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            for line in text.split("\n"):
                amt_match = re.findall(r"\d{1,3}(?:,\d{3})*\.\d{2}", line)

                if amt_match:
                    try:
                        amt = float(amt_match[-1].replace(",", ""))

                        if any(x in line.lower() for x in ["cr","credit","deposit"]):
                            ttype = "Credit"
                        else:
                            ttype = "Debit"

                        desc = line.strip()
                        cat = categorize(desc)

                        rows.append([desc, amt, ttype, cat])
                    except:
                        pass

    return pd.DataFrame(rows, columns=["desc","amt","type","cat"])

# ---------- SESSION ----------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------- LOGIN ----------
if not st.session_state.user:

    tab1, tab2 = st.tabs(["Login","Signup"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(u,p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")

        if st.button("Signup"):
            if create_user(u,p):
                st.success("Account created")
            else:
                st.error("User exists")

# ---------- DASHBOARD ----------
else:
    st.success(f"Welcome {st.session_state.user}")

    file = st.file_uploader("📤 Upload Bank Statement PDF")
    month = st.text_input("Enter Month (Apr-2026)")

    if file and month:
        df = parse_pdf(file)

        for _, r in df.iterrows():
            c.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?)",
                      (st.session_state.user, month, r["desc"], r["amt"], r["type"], r["cat"]))
        conn.commit()

        st.success("Data saved")

    # FETCH DATA
    c.execute("SELECT * FROM transactions WHERE username=?", (st.session_state.user,))
    data = pd.DataFrame(c.fetchall(), columns=["user","month","desc","amt","type","cat"])

    if not data.empty:

        debit = data[data["type"]=="Debit"]["amt"].sum()
        credit = data[data["type"]=="Credit"]["amt"].sum()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f'<div class="card"><div class="metric">₹{debit:,.0f}</div>Spent</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="card"><div class="metric">₹{credit:,.0f}</div>Credit</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="card"><div class="metric">₹{credit-debit:,.0f}</div>Net</div>', unsafe_allow_html=True)

        # CATEGORY GRAPH
        cat_df = data[data["type"]=="Debit"].groupby("cat")["amt"].sum().reset_index()

        if not cat_df.empty:
            fig = px.pie(cat_df, values="amt", names="cat",
                         color_discrete_sequence=px.colors.sequential.Plasma)
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )
            st.plotly_chart(fig, use_container_width=True)

        # COMPARISON
        st.subheader("📈 Month Comparison")

        months = list(data["month"].unique())

        if len(months) > 1:
            m1 = st.selectbox("Month 1", months)
            m2 = st.selectbox("Month 2", months)

            d1 = data[data["month"]==m1].groupby("cat")["amt"].sum()
            d2 = data[data["month"]==m2].groupby("cat")["amt"].sum()

            comp = pd.concat([d1, d2], axis=1).fillna(0)
            comp.columns = [m1, m2]

            st.dataframe(comp)

        # INSIGHTS
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧠 Smart Insights")

        top_cat = cat_df.sort_values("amt", ascending=False).iloc[0]
        st.write(f"👉 Highest spend: {top_cat['cat']}")

        if debit > credit:
            st.warning("⚠️ Spending exceeds income")

        st.markdown('</div>', unsafe_allow_html=True)

        # TABLE
        st.subheader("📋 All Transactions")
        st.dataframe(data.sort_values(by="amt", ascending=False))

# ---------- FOOTER ----------
st.markdown("""
<hr>
<div style='text-align:center; opacity:0.7;'>
❤️ Made with love by <b>@iamanujnarang</b><br><br>
🌐 Instagram | Facebook | X<br><br>
Sponsored by <a href="https://beeclue.com/" style="color:#6a11cb;">Beeclue Tech</a>
</div>
""", unsafe_allow_html=True)
