import streamlit as st
import pandas as pd
from database import get_connection

# IMPORT FEATURES
import feature_wallet
import feature_jobs
import feature_skills

def show_dashboard():
    st.title("💰 Donor Dashboard")
    conn = get_connection(); 
    if not conn: return
    user_id = st.session_state['user_id']
    cursor = conn.cursor()

    # 1. WALLET (Imported)
    feature_wallet.render_wallet('Donor')
    st.markdown("---")

    # 2. MAIN NAV
    view = st.radio("Menu", ["💸 Financial Support", "📦 Donate Items", "💼 Jobs Market", "🛠️ Hire Talent", "📜 History"], horizontal=True, label_visibility="collapsed")

    if view == "💸 Financial Support":
        st.subheader("Support a Cause")
        with st.expander("🏛️ General Fund"):
            amt = st.number_input("Amount", 100.0, step=500.0)
            if st.button("Donate"):
                cursor.execute("EXEC sp_Donor_GeneralDonation ?, ?", (user_id, amt)); conn.commit(); st.success("Donated!"); st.rerun()

        st.write("#### 🎯 Active Requests")
        df = pd.read_sql("SELECT * FROM View_Safe_Beneficiary_Info", conn)
        for i, r in df.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{r['Title']}** ({r['CategoryName']})"); c1.caption(f"{r['AliasName']} | {r['BioSummary']}")
                c1.progress(min(r['AmountCollected']/r['AmountNeeded'] if r['AmountNeeded']>0 else 0, 1.0))
                val = c2.number_input("Amt", 100.0, key=f"d_{i}")
                if c2.button("Donate", key=f"b_{i}"):
                    if feature_wallet.process_donation(user_id, r['RequestID'], val): st.balloons(); st.success("Donated!"); st.rerun()

    elif view == "📦 Donate Items":
        with st.form("item"):
            cat = st.selectbox("Category", ["Food", "Clothes", "Medical", "Furniture"])
            qty = st.number_input("Qty", 1); name = st.text_input("Item")
            if st.form_submit_button("Pledge"):
                cursor.execute("EXEC sp_Donor_DonateItem ?, ?, ?, ?", (user_id, cat, name, qty)); conn.commit(); st.success("Recorded!")
        st.dataframe(pd.read_sql(f"SELECT ItemName, Quantity, Status FROM InKind_Donations WHERE DonorID={user_id}", conn), use_container_width=True)

    elif view == "💼 Jobs Market": feature_jobs.render_job_portal()

    elif view == "🛠️ Hire Talent": feature_skills.render_skill_market()

    elif view == "📜 History":
        st.dataframe(pd.read_sql(f"SELECT R.Title, D.Amount, D.TransactionDate FROM Donations D JOIN Requests R ON D.RequestID=R.RequestID WHERE D.DonorID={user_id} ORDER BY D.TransactionDate DESC", conn), use_container_width=True)

    conn.close()