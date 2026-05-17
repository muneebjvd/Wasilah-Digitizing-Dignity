import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection

def show_impact_metrics():
    """Shows the big KPI cards in a Premium Glass Container"""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        
        # 1. Total Funds
        cursor.execute("SELECT SUM(Amount) FROM Donations")
        total = cursor.fetchone()[0]
        
        # 2. Total Users
        cursor.execute("SELECT COUNT(*) FROM Users")
        users = cursor.fetchone()[0]
        
        # WRAP IN GLASS CARD (Styles.py handles the blur/border)
        with st.container(border=True):
            st.markdown("### 🚀 System Impact")
            c1, c2 = st.columns(2)
            c1.metric("💰 Total Impact", f"PKR {total if total else 0:,.0f}")
            c2.metric("👥 Community Size", f"{users} Users")
        
        conn.close()

def plot_user_demographics():
    """Generates the Pie Chart with Premium Apple Colors & Transparency"""
    conn = get_connection()
    if conn:
        # Fetch Data
        df = pd.read_sql("SELECT UserRole, COUNT(*) as Count FROM Users GROUP BY UserRole", conn)
        conn.close()
        
        if not df.empty:
            with st.container(border=True):
                st.markdown("### 📊 User Distribution")
                
                # Apple-style Color Palette
                premium_colors = ['#007AFF', '#A3D900', '#FF9F0A', '#AF52DE', '#FF3B30']
                
                fig = px.pie(
                    df, 
                    values='Count', 
                    names='UserRole', 
                    hole=0.6, # Modern Thin Donut
                    color_discrete_sequence=premium_colors
                )
                
                # Force Transparency & Font Style
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", # Transparent background
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter, sans-serif", size=14, color="#86868b"),
                    margin=dict(t=20, b=20, l=20, r=20),
                    showlegend=True
                )
                
                # Remove hover clutter
                fig.update_traces(textinfo='percent+label')

                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No user data available for charts.")