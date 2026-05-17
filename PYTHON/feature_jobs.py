import streamlit as st
import pandas as pd
import pyodbc # Added for error handling
from database import get_connection, run_query

def render_job_portal():
    st.markdown("## 💼 Employment Exchange")
    conn = get_connection()
    if not conn: return
    
    user_id = st.session_state['user_id']
    role = st.session_state['role']
    cursor = conn.cursor()

    # =======================================================
    # SCENARIO A: DONOR (The Employer)
    # =======================================================
    if role == 'Donor':
        tab_post, tab_manage, tab_apps = st.tabs(["➕ Post New Job", "📂 My Active Jobs", "📩 Applications Received"])
        
        # 1. POST JOB
        with tab_post:
            with st.container(border=True):
                st.subheader("Create a Job Listing")
                with st.form("post_job_form"):
                    c1, c2 = st.columns(2)
                    title = c1.text_input("Job Title")
                    skills_df = pd.read_sql("SELECT SkillName FROM Ref_Skills", conn)
                    skill_req = c2.selectbox("Required Skill", skills_df['SkillName'])
                    
                    budget = st.number_input("Budget (PKR)", min_value=500.0, step=500.0)
                    desc = st.text_area("Job Details")
                    
                    if st.form_submit_button("🚀 Publish Job"):
                        try:
                            cursor.execute("EXEC sp_Job_PostNew ?, ?, ?, ?, ?", (user_id, title, desc, skill_req, budget))
                            
                            # --- SAFE FETCH ---
                            try:
                                row = cursor.fetchone()
                                res = row[0] if row else "SUCCESS"
                            except pyodbc.ProgrammingError:
                                res = "SUCCESS" 
                            
                            conn.commit()
                            
                            if "SUCCESS" in str(res): 
                                st.success("Job Posted Successfully!")
                                st.rerun()
                            else: 
                                st.error(res)
                        except Exception as e:
                            st.error(f"Error: {e}")

        # 2. MANAGE JOBS
        with tab_manage:
            my_jobs = pd.read_sql(f"SELECT JobID, JobTitle, Budget, PostedAt, Status FROM Job_Postings WHERE DonorID={user_id}", conn)
            if not my_jobs.empty:
                st.dataframe(my_jobs, hide_index=True, use_container_width=True)
                
                with st.expander("🗑️ Remove Job"):
                    del_id = st.selectbox("Select Job to Remove", my_jobs['JobID'])
                    if st.button("Delete Job"):
                        cursor.execute(f"DELETE FROM Job_Postings WHERE JobID={del_id}")
                        conn.commit()
                        st.warning("Job Deleted.")
                        st.rerun()
            else: 
                st.info("No jobs posted.")

        # 3. VIEW APPLICANTS
        with tab_apps:
            apps = pd.read_sql(f"SELECT JobTitle, CandidateAlias, AppliedAt FROM View_My_Job_Applicants WHERE DonorID={user_id}", conn)
            if not apps.empty:
                st.write("### 📬 Candidates Applied")
                st.dataframe(apps, use_container_width=True)
            else: 
                st.info("No applications received yet.")

    # =======================================================
    # SCENARIO B: BENEFICIARY (The Job Seeker)
    # =======================================================
    elif role == 'Beneficiary':
        st.info("💡 Apply for remote tasks to earn a dignified income.")
        
        # FILTER TOGGLE
        view_mode = st.radio("Filter:", ["🎯 Best Matches", "🌍 All Open Jobs"], horizontal=True)
        sql = "SELECT * FROM View_Open_Jobs"
        
        # FILTER LOGIC
        if "Best Matches" in view_mode:
            user_skill_names = pd.read_sql(f"SELECT S.SkillName FROM User_Skills US JOIN Ref_Skills S ON US.SkillID=S.SkillID WHERE US.UserID={user_id}", conn)['SkillName'].tolist()
            if not user_skill_names:
                st.warning("⚠️ Add skills to your profile for better matches.")
            else:
                formatted_skills = "', '".join(user_skill_names)
                sql += f" WHERE RequiredSkill IN ('{formatted_skills}')"

        jobs_df = pd.read_sql(sql, conn)

        if not jobs_df.empty:
            for idx, row in jobs_df.iterrows():
                with st.container(border=True): # Glass Card
                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        st.subheader(row['JobTitle'])
                        st.caption(f"Skill: **{row['RequiredSkill']}** | Budget: PKR {row['Budget']:,.0f}")
                        st.write(row['JobDescription'])
                    with c3:
                        st.write("")
                        st.write("")
                        if st.button("📝 Apply", key=f"app_{row['JobID']}"):
                            try:
                                cursor.execute("EXEC sp_Job_Apply ?, ?", (row['JobID'], user_id))
                                
                                # --- SAFE FETCH ---
                                try:
                                    row_res = cursor.fetchone()
                                    res = row_res[0] if row_res else "SUCCESS"
                                except:
                                    res = "SUCCESS"
                                
                                conn.commit()
                                if "SUCCESS" in str(res): 
                                    st.success("Application Sent!")
                                else: 
                                    st.error(res)
                            except Exception as e:
                                st.error(f"Error: {e}")
        else: 
            st.info("No jobs found matching your criteria.")

    # =======================================================
    # SCENARIO C: ADMIN (The Moderator)
    # =======================================================
    elif role == 'Admin':
        st.subheader("👮 Job Moderation Queue")
        
        all_jobs = pd.read_sql("SELECT JobID, JobTitle, RequiredSkill, Budget, DonorEmail FROM View_Open_Jobs", conn)
        st.dataframe(all_jobs, use_container_width=True)
        
        st.write("---")
        with st.expander("❌ Force Delete"):
            c1, c2 = st.columns(2)
            with c1:
                del_id = st.number_input("Enter Job ID to Delete", min_value=1)
            with c2:
                st.write("")
                st.write("")
                if st.button("Delete Job", type="primary"):
                    cursor.execute(f"DELETE FROM Job_Postings WHERE JobID={del_id}")
                    conn.commit()
                    st.success(f"Job {del_id} removed.")
                    st.rerun()

    conn.close()