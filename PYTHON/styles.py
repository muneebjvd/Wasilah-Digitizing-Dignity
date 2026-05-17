import streamlit as st

def get_design_system(theme):
    """Defines the Ultra-Premium Apple Design System."""
    
    # --- CONSTANTS (SHARP ORANGE THEME) ---
    orange_gradient = "linear-gradient(135deg, #FF9F0A 0%, #FF7B00 100%)"
    orange_solid = "#FF9F0A" # Sharp Orange
    orange_border = "rgba(255, 159, 10, 0.8)"
    Transparent = "#00000000"
    
    if theme == "dark":
        # --- DARK MODE ---
        bg_gradient = "radial-gradient(circle at 50% 0%, #1c1c1e 0%, #000000 100%)"
        card_bg = "rgba(30, 30, 30, 0.6)" 
        text_color = "#F5F5F7"
        sub_text_color = "#a1a1a6"
        border_color = "rgba(255, 255, 255, 0.15)"
        shadow = "0 8px 32px rgba(0, 0, 0, 0.4)"
        nav_bg = "rgba(20, 20, 20, 0.85)"
        
        # Input BG (Override for Dropdown below)
        input_bg = "rgba(40, 40, 40, 0.5)"
        placeholder_color = "rgba(255, 255, 255, 0.6)"
        
        # Navigation Unselected
        nav_pill_bg = "rgba(255, 255, 255, 0.1)"
        nav_pill_text = "#FFFFFF" 
        
        # Button Gradient
        btn_gradient = "linear-gradient(135deg, #007AFF 0%, #0051a8 100%)"
        
    else:
        # --- LIGHT MODE ---
        bg_gradient = "radial-gradient(circle at 50% 0%, #FFFFFF 0%, #F0F8FF 100%)"
        card_bg = "rgba(255, 255, 255, 0.75)"
        text_color = "#000000" 
        sub_text_color = "#000000" 
        border_color = "rgba(135, 206, 235, 0.3)" 
        shadow = "0 4px 24px rgba(0, 191, 255, 0.1)" 
        nav_bg = "rgba(240, 248, 255, 0.9)" 
        
        # Inputs
        input_bg = "linear-gradient(135deg, #E1F5FE 0%, #B3E5FC 100%)"
        placeholder_color = "rgba(0, 0, 0, 0.5)"

        # Navigation
        nav_pill_bg = "linear-gradient(135deg, #E1F5FE 0%, #B3E5FC 100%)"
        nav_pill_text = "#000000"
        
        # Buttons
        btn_gradient = "linear-gradient(135deg, #00BFFF 0%, #1E90FF 100%)"

    # Brand Gradients
    brand_gradient = "linear-gradient(135deg, #A3D900 0%, #FF9F0A 100%)" 

    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;700;900&display=swap');
        
        /* GLOBAL RESET */
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: {text_color} !important;
        }}
        
        p, span, div, li, .stMarkdown, .stText {{
            color: {text_color} !important;
        }}
        
        .stApp {{ background: {bg_gradient}; }}
        
        /* HIDE UI */
        #MainMenu, footer, header {{visibility: hidden;}}
        [data-testid="stSidebar"] {{display: none;}}

        /* CARDS */
        .aura-card {{
            background: {card_bg};
            backdrop-filter: blur(30px);
            -webkit-backdrop-filter: blur(30px);
            border-radius: 28px;
            padding: 40px;
            border: 1px solid {border_color};
            box-shadow: {shadow};
            margin-bottom: 24px;
        }}

        /* BUTTONS */
        .stButton > button, div[data-testid="stFormSubmitButton"] > button {{
            background: {btn_gradient} !important; 
            color: #FFFFFF !important; 
            border-radius: 30px !important;
            border: none !important;
            padding: 14px 32px !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            box-shadow: 0 4px 15px rgba(0, 191, 255, 0.3); 
            transition: transform 0.2s ease;
        }}
        .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {{ transform: scale(1.05); }}
        
        div[data-testid="column"] > div > div > div > div > button {{
             color: {text_color} !important;
        }}

        /* ========================================= */
        /* DROPDOWNS (AGGRESSIVE ORANGE OVERRIDE)    */
        /* ========================================= */
        
        /* 1. The Closed Box (What you see first) */
        .stSelectbox div[data-baseweb="select"] > div {{
            background: {orange_gradient} !important;
            border: 2px solid {orange_border} !important;
            border-radius: 16px !important;
            color: black !important; 
            font-weight: 800 !important;
        }}
        
        /* 2. The Text Inside the Closed Box */
        .stSelectbox div[data-baseweb="select"] span {{
            color: black !important;
        }}

        /* 3. The Arrow Icon */
        .stSelectbox svg {{
            fill: black !important;
        }}

        /* 4. THE POP-UP MENU LIST (The part that was invisible) */
        ul[data-baseweb="menu"] {{
            background-color: {orange_solid} !important; /* SOLID ORANGE BG */
            border-radius: 12px !important;
            padding: 5px !important;
            border: 2px solid {orange_border} !important;
        }}
        
        /* 5. The Options in the List */
        li[data-baseweb="option"] {{
            background-color: {orange_solid} !important; /* Force Orange */
            color: black !important; /* Force Black Text */
            font-weight: 600 !important;
        }}
        
        /* 6. The Selected/Hovered Option */
        li[data-baseweb="option"]:hover, li[aria-selected="true"] {{
            background-color: #FFCC80 !important; /* Lighter/Darker Orange Highlight */
            color: black !important;
            font-weight: 800 !important;
        }}
        
        /* 7. Virtualized List Container (Streamlit specific fix) */
        div[data-baseweb="popover"] div {{
             background-color: {orange_solid} !important;
        }}

        /* ========================================= */
        /* TEXT INPUTS                               */
        /* ========================================= */
        .stTextInput input, .stNumberInput input {{
            background: {input_bg} !important;
            border: 1px solid {border_color} !important;
            border-radius: 16px !important;
            color: {text_color} !important;
            font-weight: 600;
        }}

        ::placeholder {{
            color: {placeholder_color} !important;
            opacity: 1;
        }}
        
        h1, h2, h3, h4, h5, label {{ color: {text_color} !important; }}
        
        [data-testid="stMetricLabel"] {{ color: {sub_text_color} !important; opacity: 0.8; }}
        [data-testid="stMetricValue"] {{ color: {text_color} !important; font-weight: 900 !important; }}

        /* ========================================= */
        /* NAVIGATION PILLS                          */
        /* ========================================= */
        div[role="radiogroup"] {{
            background: transparent;
            display: flex;
            justify-content: center;
            gap: 12px;
            border: none;
        }}
        div[role="radiogroup"] label > div:first-child {{ display: none !important; }}

        div[role="radiogroup"] label {{
            background: {nav_pill_bg} !important;
            border: 1px solid {border_color};
            border-radius: 50px !important;
            padding: 10px 26px !important;
            color: {nav_pill_text} !important;
            font-weight: 700 !important;
            transition: all 0.3s ease;
            text-align: center;
        }}
        
        div[role="radiogroup"] label:hover {{ transform: scale(1.05); }}

        div[role="radiogroup"] label:nth-child(1):has(input:checked) {{
            background: linear-gradient(135deg, #FF9F0A 0%, #FF7B00 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 20px rgba(255, 159, 10, 0.4);
        }}
        div[role="radiogroup"] label:nth-child(2):has(input:checked) {{
            background: linear-gradient(135deg, #FFD60A 0%, #FFC107 100%) !important;
            color: #000000 !important;
            border: none !important;
            box-shadow: 0 4px 20px rgba(255, 214, 10, 0.4);
        }}
        div[role="radiogroup"] label:nth-child(3):has(input:checked) {{
            background: linear-gradient(135deg, #32D74B 0%, #28CD41 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 20px rgba(50, 215, 75, 0.4);
        }}

        /* NAVBAR */
        .nav-container {{
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 1200px;
            background: {nav_bg};
            backdrop-filter: blur(50px);
            -webkit-backdrop-filter: blur(50px);
            border-radius: 24px;
            padding: 12px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid {border_color};
            box-shadow: {shadow};
            z-index: 999999;
        }}
        
        .gradient-text {{
            background: {brand_gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .block-container {{ padding-top: 140px !important; }}
    </style>
    """

def render_top_nav(theme):
    text_c = "#F5F5F7" if theme == "dark" else "#000000"
    logo_svg = """<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#A3D900;stop-opacity:1" /><stop offset="100%" style="stop-color:#FF9F0A;stop-opacity:1" /></linearGradient></defs><path d="M6 10 L14 34 L20 16 L26 34 L34 10" stroke="url(#brandGrad)" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

    html_code = f"""
<div class="nav-container">
<div class="nav-logo">
{logo_svg}
<span class="gradient-text">Wasilah</span>
</div>
<div style="font-size: 13px; font-weight: 700; color: {text_c}; opacity: 0.9; letter-spacing: 1px; text-transform: uppercase;">
WELFARE TRUST
</div>
</div>
"""
    st.markdown(html_code, unsafe_allow_html=True)

def card_start():
    st.markdown('<div class="aura-card">', unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)