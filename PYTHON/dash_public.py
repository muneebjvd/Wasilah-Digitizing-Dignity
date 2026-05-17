import streamlit as st
import pandas as pd
from database import get_connection

def show_feed():
    conn = get_connection(); 
    if not conn: return
    
    # 1. HERO SECTION
    theme = st.session_state.get("theme", "dark")
    if theme == "light":
        hero_bg = "linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%)"
        hero_title = "#1b5e20"; hero_sub = "#2e7d32"; border = "#A5D6A7"
    else:
        hero_bg = "linear-gradient(135deg, #0e1117 0%, #1e3a29 100%)"
        hero_title = "#ffffff"; hero_sub = "#4CAF50"; border = "#4CAF50"

    st.markdown(f"""
        <style>
        .hero {{ padding: 3rem; border-radius: 24px; background: {hero_bg}; text-align: center; border: 1px solid {border}; margin-bottom: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
        .hero h1 {{ color: {hero_title}; font-size: 3.5rem; font-weight: 900; margin-bottom: 0; letter-spacing: -1px; }}
        .hero h3 {{ color: {hero_sub}; margin-top: 10px; font-weight: 500; }}
        .hero p {{ color: {hero_title}; font-size: 1.1rem; opacity: 0.8; }}
        </style>
        <div class="hero">
            <h1>WASILAH</h1>
            <h3>The Medium of Dignity</h3>
            <p>Pakistan's First Double-Blind, Guarantor-Verified Welfare Ecosystem.</p>
        </div>
    """, unsafe_allow_html=True)

    # 2. STATS
    s = pd.read_sql("SELECT * FROM View_Public_Stats", conn).iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Raised", f"PKR {s['Funds']:,.0f}"); c2.metric("🤝 Lives", s['Beneficiaries'])
    c3.metric("🛡️ Guarantors", s['Guarantors']); c4.metric("✅ Missions", s['Completed'])
    st.markdown("---")

    # 3. CONTENT
    t1, t2, t3 = st.tabs(["🔍 Needs Feed", "⚙️ How It Works", "🌟 Success Stories"])

    with t1: # LIVE FEED
        st.write("#### 📢 Verified Needs")
        df = pd.read_sql("SELECT R.RequestID, C.CategoryName, R.Title, R.AmountNeeded, R.AmountCollected, P.AliasName, R.Description FROM Requests R JOIN User_Public_Profiles P ON R.UserID=P.UserID JOIN Ref_Categories C ON R.CategoryID=C.CategoryID WHERE R.Status='Open'", conn)
        
        if not df.empty:
            for i in range(0, len(df), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(df):
                        r = df.iloc[i+j]
                        with cols[j], st.container(border=True):
                            st.markdown(f"### {r['Title']}")
                            st.caption(f"**{r['CategoryName']}** | {r['AliasName']}")
                            st.write(f"_{r['Description'][:90]}..._")
                            st.progress(min(r['AmountCollected'] / r['AmountNeeded'] if r['AmountNeeded'] > 0 else 0, 1.0))
                            k1, k2 = st.columns(2)
                            k1.write(f"Goal: **{r['AmountNeeded']:,.0f}**"); k2.write(f"Raised: **{r['AmountCollected']:,.0f}**")
                            st.button("❤️ Donate", key=f"d_{r['RequestID']}", use_container_width=True)
        else: st.info("No active requests.")

    with t2: # PROCESS
        st.subheader("The Journey")
        st.markdown("1. **Request:** Posted anonymously.\n2. **Verification:** Guarantor checks docs.\n3. **Live:** Donors see needs.\n4. **Funding:** Money locked in Wallet.\n5. **Voucher:** Spent at verified vendors.")
        st.image("https://images.unsplash.com/photo-1556761175-5973dc0f32e7?q=80&w=1000", caption="Transparency")

    with t3: # SUCCESS STORIES
        st.subheader("Impact Gallery")
        sdf = pd.read_sql("SELECT * FROM View_Success_Stories", conn)
        for i, r in sdf.iterrows():
            with st.expander(f"🎉 {r['Title']}"):
                st.balloons(); st.success(f"Fully funded ({r['CategoryName']}) for {r['AliasName']}. Raised: PKR {r['AmountCollected']:,.0f}")

    conn.close()