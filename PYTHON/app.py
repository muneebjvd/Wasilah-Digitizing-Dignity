import streamlit as st
import styles
import auth

# Import Dashboards
import dash_public
import dash_beneficiary
import dash_donor
import dash_guarantor
import dash_vendor
import dash_admin

# --- CONFIG ---
st.set_page_config(page_title="Wasilah", page_icon="✨", layout="wide")

# --- STATE MANAGEMENT ---
if "user_id" not in st.session_state:
    st.session_state.update({"user_id": None, "role": None, "theme": "dark", "nav": "Home"})

# --- LOAD VISUALS ---
st.markdown(styles.get_design_system(st.session_state["theme"]), unsafe_allow_html=True)
styles.render_top_nav(st.session_state["theme"])

# --- NAVIGATION BAR ---
c1, c2, c3 = st.columns([1, 6, 1])

with c1:
    # Theme Toggle
    icon = "☀️" if st.session_state["theme"] == "dark" else "🌙"
    if st.button(icon, key="theme_toggle"):
        st.session_state["theme"] = "light" if st.session_state["theme"] == "dark" else "dark"
        st.rerun()

with c2:
    # NAVIGATION PILLS (Only Show if NOT Logged In)
    if not st.session_state["user_id"]:
        menu = ["Home", "Live Feed", "Login"]
        current_nav = st.session_state.get("nav", "Home")
        idx = menu.index(current_nav) if current_nav in menu else 0
        
        selected = st.radio("Nav", menu, horizontal=True, label_visibility="collapsed", index=idx)
        
        if selected != st.session_state["nav"]:
            st.session_state["nav"] = selected
            st.rerun()
    else:
        # If Logged In, Show Badge instead of Menu
        st.markdown(f"<div style='text-align: center; font-weight: 800; opacity: 0.8; padding-top: 10px; font-size: 18px;'>👤 Signed in as <span style='color:#A3D900'>{st.session_state['role']}</span></div>", unsafe_allow_html=True)

with c3:
    # Logout Button (Only if Logged In)
    if st.session_state["user_id"]:
        if st.button("Log Out"):
            st.session_state.update({"user_id": None, "role": None, "nav": "Home"})
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- CONTENT ROUTER ---

# GUEST VIEWS (Only if NOT Logged In)
if not st.session_state["user_id"]:
    
    # 1. HOME PAGE
    if st.session_state["nav"] == "Home":
        with st.container(border=True):
            c_text, c_img = st.columns([6, 5])
            with c_text:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<h1 style='font-size: 72px; line-height: 1.1;'>The Medium for <br><span class='gradient-text'>Dignity</span></h1>", unsafe_allow_html=True)
                st.markdown("<h3 style='opacity: 0.7; font-weight: 600;'>A double-blind, guarantor-verified welfare ecosystem.</h3>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("Get Started →"):
                    st.session_state["nav"] = "Login"
                    st.rerun()
            with c_img:
                st.image("https://images.unsplash.com/photo-1593113598332-cd288d649433?q=80&w=1600", use_container_width=True)

    # 2. LIVE FEED
    elif st.session_state["nav"] == "Live Feed":
        dash_public.show_feed()

    # 3. LOGIN / SIGNUP
    elif st.session_state["nav"] == "Login":
        c_spacer, c_main, c_spacer2 = st.columns([1, 2, 1])
        with c_main:
            with st.container(border=True):
                st.subheader("Welcome Back")
                
                tab_log, tab_reg = st.tabs(["Sign In", "Create Account"])
                
                with tab_log:
                    with st.form("login"):
                        e = st.text_input("Email", placeholder="name@example.com")
                        p = st.text_input("Password", type="password")
                        if st.form_submit_button("Enter Portal", use_container_width=True):
                            u = auth.login_user(e, p)
                            if u:
                                st.session_state.update({"user_id": u[0], "role": u[1]})
                                st.rerun()
                            else:
                                st.error("Invalid credentials.")

                with tab_reg:
                    with st.form("reg"):
                        ne = st.text_input("New Email")
                        np = st.text_input("New Password", type="password")
                        nr = st.selectbox("I am a...", ["Donor", "Beneficiary", "Guarantor", "Vendor"])
                        if st.form_submit_button("Join Wasilah", use_container_width=True):
                            msg = auth.register_user(ne, np, nr)
                            if "SUCCESS" in msg: 
                                st.success("Created! Please login.")
                            else: 
                                st.error(msg)

# --- LOGGED IN DASHBOARDS ---
else:
    role = st.session_state["role"]
    
    if role == 'Beneficiary':
        dash_beneficiary.show_dashboard()
    elif role == 'Donor':
        dash_donor.show_dashboard()
    elif role == 'Admin':
        dash_admin.show_dashboard()
    elif role == 'Guarantor':
        dash_guarantor.show_dashboard()
    elif role == 'Vendor':
        dash_vendor.show_dashboard()

# --- FOOTER ---
st.markdown("<br><br><div style='text-align: center; opacity: 0.4; font-size: 12px; font-weight: 600;'>© 2025 Wasilah • Designed in Lahore By Muneeb Javed</div>", unsafe_allow_html=True)