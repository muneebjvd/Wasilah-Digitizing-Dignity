import pyodbc
import streamlit as st

# ========================================================
# CONFIGURATION
# ========================================================
# We use raw string (r'...') to handle backslashes correctly
SERVER_NAME = r'MUNEEB\SQLEXPRESS' 
DATABASE_NAME = 'WasilahDB'

def get_connection():
    """
    Establishes a connection to the SQL Server.
    Returns the connection object or None if failed.
    """
    try:
        # Trusted_Connection=yes uses your Windows credentials
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;'
        return pyodbc.connect(conn_str)
    except Exception as e:
        # Only show error if we are running inside Streamlit
        if hasattr(st, 'error'):
            st.error(f"❌ Database Connection Failed: {e}")
        else:
            print(f"❌ Database Connection Failed: {e}")
        return None

def run_query(query, params=None):
    """
    Helper function to execute SQL queries safely.
    Returns: (cursor, connection)
    """
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor, conn
        except Exception as e:
            if hasattr(st, 'error'):
                st.error(f"⚠️ Query Error: {e}")
            else:
                print(f"⚠️ Query Error: {e}")
            conn.close()
    return None, None

# ========================================================
# INDEPENDENT TEST BLOCK (Run this file directly to test)
# ========================================================
if __name__ == "__main__":
    print("--- Testing Database Connection ---")
    conn = get_connection()
    if conn:
        print("✅ Connection Successful!")
        print(f"Connected to: {SERVER_NAME} -> {DATABASE_NAME}")
        conn.close()
    else:
        print("❌ Connection Failed. Check Server Name.")