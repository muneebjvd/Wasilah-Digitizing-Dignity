import streamlit as st
import pandas as pd
from database import get_connection, run_query

def render_skill_market():
    st.markdown("## 🛠️ Talent Exchange")
    conn = get_connection(); cursor = conn.cursor()
    user_id = st.session_state['user_id']; role = st.session_state['role']

    if role == 'Donor':
        c1, c2 = st.tabs(["🔍 Find Talent", "📤 My Offers"])
        with c1:
            term = st.text_input("Skill Search", "")
            sql = "SELECT * FROM View_Available_Talent" + (f" WHERE SkillName LIKE '%{term}%'" if term else "")
            df = pd.read_sql(sql, conn)
            for i, r in df.iterrows():
                with st.container(border=True):
                    st.write(f"**{r['SkillName']}** ({r['ExperienceLevel']}) - {r['AliasName']}")
                    st.caption(r['SkillDetails'])
                    with st.popover("Hire"):
                        title = st.text_input("Task", key=f"t{i}"); amt = st.number_input("Pay", 500.0, key=f"a{i}")
                        if st.button("Send", key=f"b{i}"):
                            cursor.execute("EXEC sp_Skill_MakeOffer ?, ?, ?, ?", (user_id, r['BeneficiaryID'], title, amt))
                            conn.commit(); st.success("Sent!")
        
        with c2:
            # Added Payment Logic Here
            df = pd.read_sql(f"SELECT OfferID, UP.AliasName, WO.ProjectTitle, WO.OfferAmount, WO.Status FROM Work_Offers WO JOIN User_Public_Profiles UP ON WO.BeneficiaryID=UP.UserID WHERE WO.DonorID={user_id} ORDER BY WO.OfferDate DESC", conn)
            for i, r in df.iterrows():
                with st.container(border=True):
                    c_a, c_b = st.columns([3,1])
                    c_a.write(f"**{r['ProjectTitle']}** - {r['AliasName']} ({r['Status']})")
                    
                    if r['Status'] == 'Accepted':
                        if c_b.button("✅ Pay & Close", key=f"pay_{r['OfferID']}"):
                            # Direct SQL to move money
                            try:
                                cursor.execute("UPDATE Wallets SET Balance = Balance - ? WHERE UserID = ?", (r['OfferAmount'], user_id))
                                cursor.execute("UPDATE Wallets SET Balance = Balance + ? WHERE UserID = (SELECT BeneficiaryID FROM Work_Offers WHERE OfferID=?)", (r['OfferAmount'], r['OfferID']))
                                cursor.execute("UPDATE Work_Offers SET Status = 'Completed' WHERE OfferID = ?", (r['OfferID'],))
                                conn.commit()
                                st.success("Paid!"); st.rerun()
                            except Exception as e:
                                st.error("Failed: " + str(e))
                    elif r['Status'] == 'Completed':
                        c_b.success("Paid")
                    else:
                        c_b.info("Pending")

    elif role == 'Beneficiary':
        c1, c2 = st.tabs(["📝 Portfolio", "📩 Offers"])
        with c1:
            with st.expander("➕ Add Skill"):
                s = st.selectbox("Skill", pd.read_sql("SELECT SkillName FROM Ref_Skills", conn)['SkillName'])
                l = st.select_slider("Level", ["Beginner", "Intermediate", "Expert"])
                d = st.text_area("Details")
                if st.button("Save"):
                    cursor.execute("EXEC sp_AddUserSkill ?, ?, ?, ?", (user_id, s, l, d))
                    conn.commit(); st.success("Saved!"); st.rerun()
            st.dataframe(pd.read_sql(f"SELECT S.SkillName, US.ExperienceLevel FROM User_Skills US JOIN Ref_Skills S ON US.SkillID=S.SkillID WHERE US.UserID={user_id}", conn), use_container_width=True)

        with c2:
            df = pd.read_sql(f"SELECT OfferID, ProjectTitle, OfferAmount FROM Work_Offers WHERE BeneficiaryID={user_id} AND Status='Pending'", conn)
            for i, r in df.iterrows():
                with st.container(border=True):
                    c_a, c_b = st.columns([3,1])
                    c_a.write(f"**{r['ProjectTitle']}** - PKR {r['OfferAmount']:,.0f}")
                    if c_b.button("Accept", key=f"ac{i}"):
                        cursor.execute("EXEC sp_Skill_RespondOffer ?, ?, 'Accepted'", (r['OfferID'], user_id)); conn.commit(); st.rerun()
                    if c_b.button("Reject", key=f"rj{i}"):
                        cursor.execute("EXEC sp_Skill_RespondOffer ?, ?, 'Rejected'", (r['OfferID'], user_id)); conn.commit(); st.rerun()

    conn.close()