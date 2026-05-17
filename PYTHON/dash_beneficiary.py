import streamlit as st
import pandas as pd
import re
from datetime import date, datetime
from database import get_connection

# IMPORT MODULES
import feature_wallet
import feature_jobs
import feature_skills
import feature_vouchers

# HELPER
def validate_cnic(text):
    return bool(re.match(r"^\d{5}-\d{7}-\d{1}$", text))

def show_dashboard():
    st.title("📝 Beneficiary Dashboard")
    conn = get_connection(); 
    if not conn: return
    user_id = st.session_state['user_id']
    cursor = conn.cursor()

    # STATUS
    row = pd.read_sql(f"SELECT VerificationStatus, AliasName FROM User_Public_Profiles WHERE UserID={user_id}", conn).iloc[0]
    c1, c2 = st.columns([3,1])
    c1.write(f"Logged in as: **{row['AliasName']}**")
    if row['VerificationStatus'] == 'Verified': c2.success("✅ Verified")
    else: c2.warning(f"⚠️ {row['VerificationStatus']}")
    
    st.markdown("---")

    # NAV (Fixed Names)
    view = st.radio("Menu", ["💰 Wallet", "📢 Requests", "🆔 Verify", "🛠️ Skills", "💼 Jobs"], horizontal=True, label_visibility="collapsed")

    # === WALLET ===
    if view == "💰 Wallet":
        feature_wallet.render_wallet('Beneficiary')
        st.markdown("---")
        feature_vouchers.render_voucher_portal()

    # === REQUESTS ===
    elif view == "📢 Requests":
        with st.container(border=True):
            st.subheader("Manage Needs")
            with st.expander("➕ Post New Request"):
                with st.form("new_req"):
                    cat = st.selectbox("Category", pd.read_sql("SELECT CategoryName FROM Ref_Categories", conn)['CategoryName'])
                    tit = st.text_input("Title"); amt = st.number_input("Amount", 1000.0)
                    desc = st.text_area("Story"); ded = st.date_input("Deadline")
                    if st.form_submit_button("Post"):
                        cursor.execute("EXEC sp_Ben_PostRequest ?, ?, ?, ?, ?, ?", (user_id, cat, tit, desc, amt, ded)); conn.commit(); st.success("Posted!"); st.rerun()
            
            st.write("#### Active Requests")
            # Logic for Edit/Delete
            my_reqs = pd.read_sql(f"SELECT RequestID, Title FROM Requests WHERE UserID={user_id} AND Status='Open'", conn)
            if not my_reqs.empty:
                req_opt = st.selectbox("Edit Request", my_reqs['Title'])
                req_id = my_reqs[my_reqs['Title'] == req_opt]['RequestID'].iloc[0]
                curr = pd.read_sql(f"SELECT * FROM Requests WHERE RequestID={req_id}", conn).iloc[0]
                
                with st.form("edit_req"):
                    nt = st.text_input("Title", value=curr['Title'])
                    na = st.number_input("Amount", value=float(curr['AmountNeeded']))
                    nd = st.text_area("Desc", value=curr['Description'])
                    c_u, c_d = st.columns(2)
                    if c_u.form_submit_button("💾 Save"):
                        cursor.execute("EXEC sp_Ben_UpdateRequest ?, ?, ?, ?, ?", (req_id, nt, nd, na, date.today())); conn.commit(); st.success("Saved!"); st.rerun()
                    if c_d.form_submit_button("🗑️ Delete"):
                        cursor.execute("EXEC sp_Ben_DeleteRequest ?", (req_id,)); conn.commit(); st.warning("Deleted"); st.rerun()

            st.dataframe(pd.read_sql(f"SELECT Title, AmountNeeded, Status FROM Requests WHERE UserID={user_id}", conn), use_container_width=True)

    # === VERIFY ===
    elif view == "🆔 Verify":
        with st.container(border=True):
            st.subheader("Verification Center")
            c1, c2 = st.columns(2)
            with c1:
                with st.form("up"):
                    dt = st.selectbox("Type", ["CNIC Front", "Bill", "Affidavit"])
                    f = st.file_uploader("File")
                    cnic = st.text_input("CNIC No (If applicable)")
                    if st.form_submit_button("Upload"):
                        if "CNIC" in dt and not validate_cnic(cnic): st.error("Invalid CNIC")
                        elif f: 
                            cursor.execute("EXEC sp_Ben_UploadDoc ?, ?, ?", (user_id, dt, f.name + (f" | {cnic}" if cnic else ""))); conn.commit(); st.success("Uploaded!"); st.rerun()
            with c2:
                docs = pd.read_sql(f"SELECT DocID, DocType, UploadDate FROM Verification_Documents WHERE UserID={user_id}", conn)
                if not docs.empty:
                    st.dataframe(docs, hide_index=True)
                    del_id = st.selectbox("Delete Doc", docs['DocID'])
                    if st.button("Delete"):
                        cursor.execute("EXEC sp_Ben_DeleteDoc ?, ?", (del_id, user_id)); conn.commit(); st.rerun()

    # === SKILLS ===
    elif view == "🛠️ Skills":
        feature_skills.render_skill_market()

    # === JOBS ===
    elif view == "💼 Jobs":
        feature_jobs.render_job_portal()

    conn.close()