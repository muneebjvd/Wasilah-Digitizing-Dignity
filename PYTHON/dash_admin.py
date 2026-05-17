import streamlit as st
import pandas as pd
import plotly.express as px
import reports
from database import get_connection

def show_dashboard():
    st.title("🛡️ Admin DASHBOARD")
    conn = get_connection(); 
    if not conn: return
    cursor = conn.cursor(); aid = st.session_state['user_id']

    # SEARCH
    with st.expander("🔎 Universal Search", expanded=False):
        term = st.text_input("Keyword")
        if term:
            c1, c2, c3 = st.columns(3)
            c1.dataframe(pd.read_sql(f"SELECT UserID, Email, UserRole FROM Users WHERE Email LIKE '%{term}%' OR CAST(UserID AS VARCHAR) = '{term}'", conn), hide_index=True)
            c2.dataframe(pd.read_sql(f"SELECT RequestID, Title, AmountNeeded FROM Requests WHERE Title LIKE '%{term}%'", conn), hide_index=True)
            c3.dataframe(pd.read_sql(f"SELECT TOP 5 LogID, Description FROM System_Logs WHERE Description LIKE '%{term}%'", conn), hide_index=True)

    t1, t2, t3, t4, t5 = st.tabs(["👤 Users", "📝 Content", "💰 Bank", "🧪 SQL", "🧠 Intel"])

    with t1: # USERS
        st.subheader("User Management")
        uid = st.number_input("User ID", min_value=1)
        uinfo = pd.read_sql(f"SELECT * FROM Users WHERE UserID={uid}", conn)
        
        if not uinfo.empty:
            row = uinfo.iloc[0]
            st.success(f"Selected: **{row['Email']}** ({row['UserRole']})")
            
            # DOSSIER
            if row['UserRole'] == 'Beneficiary':
                with st.expander("📂 Dossier"):
                    st.table(pd.read_sql(f"SELECT RealName, CNIC_Number, PhoneNumber, AddressText FROM User_PII WHERE UserID={uid}", conn))
                    st.dataframe(pd.read_sql(f"SELECT DocType, UploadDate FROM Verification_Documents WHERE UserID={uid}", conn))

            # ACTIONS
            with st.expander("⚙️ Actions"):
                nem = st.text_input("Email", value=row['Email']); nrl = st.selectbox("Role", ["Donor", "Beneficiary", "Guarantor", "Vendor", "Admin"], index=["Donor", "Beneficiary", "Guarantor", "Vendor", "Admin"].index(row['UserRole']))
                if st.button("Save"): cursor.execute("EXEC sp_Admin_UpdateUser ?, ?, ?, ?", (uid, nem, nrl, aid)); conn.commit(); st.success("Updated!"); st.rerun()
                c_a, c_b = st.columns(2)
                if c_a.button("Hold/Active"): cursor.execute("EXEC sp_Admin_ToggleStatus ?, ?, ?", (uid, 0 if row['IsActive'] else 1, aid)); conn.commit(); st.rerun()
                if c_b.button("DELETE"): cursor.execute("EXEC sp_Admin_DeleteUser ?, ?", (uid, aid)); conn.commit(); st.warning("Deleted"); st.rerun()

        st.markdown("---"); st.subheader("🔗 Linker")
        c1, c2, c3 = st.columns(3)
        ben = c1.selectbox("Ben", pd.read_sql("SELECT Email FROM Users WHERE UserRole='Beneficiary'", conn)['Email'])
        guar = c2.selectbox("Guar", pd.read_sql("SELECT Email FROM Users WHERE UserRole='Guarantor'", conn)['Email'])
        if c3.button("Link"):
            bid = pd.read_sql(f"SELECT UserID FROM Users WHERE Email='{ben}'", conn).iloc[0,0]
            gid = pd.read_sql(f"SELECT UserID FROM Users WHERE Email='{guar}'", conn).iloc[0,0]
            cursor.execute("EXEC sp_Admin_AssignGuarantor ?, ?, ?", (int(bid), int(gid), aid)); conn.commit(); st.success("Linked!")

    with t2: # CONTENT
        c1, c2 = st.columns(2)
        with c1:
            st.dataframe(pd.read_sql("SELECT RequestID, Title FROM Requests", conn), height=200)
            dr = st.number_input("Del Req ID", 1)
            if st.button("Del Req"): cursor.execute("EXEC sp_Admin_DeleteRequest ?, ?", (dr, aid)); conn.commit(); st.success("Deleted"); st.rerun()
        with c2:
            st.dataframe(pd.read_sql("SELECT JobID, JobTitle FROM Job_Postings", conn), height=200)
            dj = st.number_input("Del Job ID", 1)
            if st.button("Del Job"): cursor.execute(f"DELETE FROM Job_Postings WHERE JobID={dj}"); conn.commit(); st.success("Deleted"); st.rerun()

    with t3: # BANK
        st.dataframe(pd.read_sql("SELECT TOP 10 DonationID, Amount, TransactionDate FROM Donations ORDER BY Amount DESC", conn))
        vid = st.number_input("Verify Donation ID", 1)
        if st.button("Verify"): cursor.execute("EXEC sp_Admin_VerifyTransaction ?, ?", (vid, aid)); conn.commit(); st.success("Verified")

    with t4: # SQL LAB
        s1, s2, s3 = st.tabs(["UNION", "INTERSECT", "EXCEPT"])
        s1.dataframe(pd.read_sql("SELECT TOP 20 * FROM View_Master_Money_Log", conn))
        s2.dataframe(pd.read_sql("SELECT * FROM View_Skilled_Beneficiaries", conn))
        s3.dataframe(pd.read_sql("SELECT * FROM View_Inactive_Beneficiaries", conn))

    with t5: # INTEL
        reports.show_impact_metrics(); st.markdown("---"); reports.plot_user_demographics()
        with st.expander("Logs"): st.dataframe(pd.read_sql("SELECT TOP 50 * FROM System_Logs ORDER BY LogDate DESC", conn))

    conn.close()