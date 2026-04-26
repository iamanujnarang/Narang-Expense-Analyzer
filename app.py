import streamlit as st
import pandas as pd
import pdfplumber
import plotly.express as px

st.set_page_config(page_title="Narang Expense Analyzer", layout="wide")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
body {background-color: #0e1117; color: white;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- TITLE ----------
st.markdown("<h1 style='text-align:center;'>💰 Narang Expense Analyzer</h1>", unsafe_allow_html=True)

# ---------- CATEGORY ----------
def categorize(desc):
    d = desc.lower()

    if any(x in d for x in ["zepto","dominos","restaurant","cafe"]):
        return "Food & Dining"
    elif any(x in d for x in ["petrol","fuel","indian oil"]):
        return "Fuel"
    elif any(x in d for x in ["railway","uber","ola"]):
        return "Travel"
    elif any(x in d for x in ["amazon","flipkart","retail"]):
        return "Shopping"
    elif any(x in d for x in ["jio","airtel","pspcl","bill"]):
        return "Bills & Utilities"
    elif any(x in d for x in ["sip","groww","mutual"]):
        return "Investments"
    elif any(x in d for x in ["loan","emi"]):
        return "EMI"
    elif any(x in d for x in ["netflix","spotify"]):
        return "Subscriptions"
    else:
        return "Miscellaneous"

# ---------- PDF PARSER ----------
def extract(file):
    rows = []
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text = p.extract_text()
            if not text:
                continue

            for line in text.split("\n"):
                parts = line.split()

                if len(parts) > 4:
                    try:
                        amt = float(parts[-2].replace(",", ""))
                        desc = " ".join(parts[1:-3])

                        # CREDIT/DEBIT DETECTION
                        if "deposit" in line.lower() or "cr" in line.lower():
                            ttype = "Credit"
                        else:
                            ttype = "Debit"

                        cat = categorize(desc)

                        rows.append([desc, amt, cat, ttype])
                    except:
                        pass

    return pd.DataFrame(rows, columns=["desc","amt","cat","type"])

# ---------- UI ----------
file = st.file_uploader("📤 Upload Bank Statement PDF")

if file:
    df = extract(file)

    if not df.empty:

        debit = df[df["type"]=="Debit"]["amt"].sum()
        credit = df[df["type"]=="Credit"]["amt"].sum()
        net = credit - debit

        # ---------- KPI ----------
        c1, c2, c3 = st.columns(3)
        c1.metric("💸 Total Spent", f"₹{debit:,.0f}")
        c2.metric("💰 Total Credit", f"₹{credit:,.0f}")
        c3.metric("📊 Net Balance Change", f"₹{net:,.0f}")

        # ---------- CATEGORY ----------
        cat_df = df[df["type"]=="Debit"].groupby("cat")["amt"].sum().reset_index()

        # PIE
        fig1 = px.pie(cat_df, values="amt", names="cat", title="Spending Breakdown")
        st.plotly_chart(fig1, use_container_width=True)

        # BAR
        fig2 = px.bar(cat_df, x="cat", y="amt", title="Category Spend")
        st.plotly_chart(fig2, use_container_width=True)

        # ---------- TOP TRANSACTIONS ----------
        st.subheader("🔝 Top Transactions")
        st.dataframe(df.sort_values(by="amt", ascending=False).head(10))

        # ---------- MICRO SPENDS ----------
        micro = df[(df["amt"]<200) & (df["type"]=="Debit")]
        st.subheader("⚠️ Micro Spending")
        st.write(f"Count: {len(micro)} | Total: ₹{micro['amt'].sum():,.0f}")

        # ---------- INSIGHTS ----------
        st.subheader("🧠 Smart Insights")

        top_cat = cat_df.sort_values("amt", ascending=False).iloc[0]
        st.write(f"👉 Highest spending: {top_cat['cat']} (₹{top_cat['amt']:,.0f})")

        if micro["amt"].sum() > 5000:
            st.warning("⚠️ Too many small spends (UPI leaks)")

        if "Food & Dining" in cat_df["cat"].values:
            food_amt = cat_df[cat_df["cat"]=="Food & Dining"]["amt"].values[0]
            if food_amt > 5000:
                st.warning("🍔 High food spending")

    else:
        st.error("Unable to read PDF properly")

# ---------- FOOTER ----------
st.markdown("""
<hr>
<p style='text-align:center;'>
❤️ Made with love by <b>@iamanujnarang</b><br>
📱 Instagram | Facebook | X<br><br>
Sponsored by <a href="https://beeclue.com/" target="_blank">Beeclue Tech</a>
</p>
""", unsafe_allow_html=True)