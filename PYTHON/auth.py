import streamlit as st
from database import run_query, get_connection

def login_user(email, password):
    """Simple Login Check"""
    cursor, conn = run_query("SELECT UserID, UserRole FROM Users WHERE Email = ? AND PasswordHash = ?", (email, password))
    if cursor:
        user = cursor.fetchone()
        conn.close()
        return user
    return None

def register_user(email, password, role):
    """Registration via Stored Procedure"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Capture Output Parameter
            sql = "DECLARE @Msg NVARCHAR(100); EXEC sp_RegisterUser ?, ?, ?, @Result=@Msg OUTPUT; SELECT @Msg;"
            cursor.execute(sql, (email, password, role))
            res = cursor.fetchone()[0]
            conn.commit(); conn.close()
            return res
        except Exception as e:
            conn.close()
            if "CHK_EmailFormat" in str(e): return "ERROR: Invalid Email Format"
            return f"Error: {e}"
    return "Connection Failed"