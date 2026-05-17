import streamlit as st
import pandas as pd
from database import get_connection

def show_dashboard():
    st.title("🤝 Guarantor Dashboard")
    conn = get_connection(); cursor = conn.cursor()
    gid = st.session_state['user_id']

    t1, t2 = st.tabs(["⏳ Pending", "📜 History"])

    with t1:
        pdf = pd.read_sql("SELECT * FROM View_Pending_Verifications", conn)
        if not pdf.empty:
            opt = st.selectbox("Select Applicant", pdf['RealName'] + " (ID: " + pdf['UserID'].astype(str) + ")")
            tid = int(opt.split("(ID: ")[1][:-1])
            row = pdf[pdf['UserID'] == tid].iloc[0]

            with st.container(border=True):
                st.info(f"Reviewing: **{row['RealName']}**")
                c1, c2 = st.columns(2)
                c1.write(f"**CNIC:** {row['CNIC_Number']}"); c2.write(f"**Address:** {row['AddressText']}")
                
                st.write("#### 📄 Docs")
                docs = pd.read_sql(f"SELECT DocType, DocContent, UploadDate FROM Verification_Documents WHERE UserID={tid}", conn)
                if not docs.empty: st.dataframe(docs, use_container_width=True)
                else: st.warning("No docs uploaded.")

                rem = st.text_area("Remarks", placeholder="Verification notes...")
                c_a, c_r = st.columns(2)
                
                if c_a.button("✅ Approve"):
                    if rem: cursor.execute("EXEC sp_Guarantor_VerifyAction ?, ?, 'Verified', ?", (gid, tid, rem)); conn.commit(); st.success("Verified!"); st.rerun()
                    else: st.error("Add remarks.")
                
                if c_r.button("❌ Reject"):
                    if rem: cursor.execute("EXEC sp_Guarantor_VerifyAction ?, ?, 'Rejected', ?", (gid, tid, rem)); conn.commit(); st.error("Rejected."); st.rerun()
                    else: st.error("Add remarks.")
        else: st.success("No pending verifications.")

    with t2:
        st.dataframe(pd.read_sql(f"SELECT P.RealName, P.CNIC_Number, GL.VerificationDate, UP.VerificationStatus, GL.Remarks FROM Guarantor_Links GL JOIN User_PII P ON GL.BeneficiaryID=P.UserID JOIN User_Public_Profiles UP ON GL.BeneficiaryID=UP.UserID WHERE GL.GuarantorID={gid} ORDER BY GL.VerificationDate DESC", conn), use_container_width=True)

    conn.close()