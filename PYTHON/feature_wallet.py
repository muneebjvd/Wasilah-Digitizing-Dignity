import streamlit as st
import pandas as pd
from database import get_connection, run_query

# HELPER: Get Balance
def get_balance(user_id):
    cursor, conn = run_query("SELECT Balance FROM Wallets WHERE UserID = ?", (user_id,))
    if cursor:
        row = cursor.fetchone()
        conn.close()
        return float(row[0]) if row else 0.00
    return 0.00

# HELPER: Process Donation
def process_donation(donor_id, request_id, amount):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # 1. Deduct from Donor
            cursor.execute("UPDATE Wallets SET Balance = Balance - ? WHERE UserID = ?", (amount, donor_id))
            
            # 2. Add to Beneficiary Wallet
            cursor.execute("UPDATE Wallets SET Balance = Balance + ? WHERE UserID = (SELECT UserID FROM Requests WHERE RequestID = ?)", (amount, request_id))

            # 3. Update Request Progress
            cursor.execute("UPDATE Requests SET AmountCollected = AmountCollected + ? WHERE RequestID = ?", (amount, request_id))
            
            # 4. Log Donation
            cursor.execute("INSERT INTO Donations (DonorID, RequestID, Amount) VALUES (?, ?, ?)", (donor_id, request_id, amount))
            
            conn.commit(); conn.close()
            return True
        except Exception as e:
            conn.rollback(); st.error(f"Transaction Failed: {e}"); return False
    return False

# MAIN UI
def render_wallet(role):
    user_id = st.session_state['user_id']
    bal = get_balance(user_id)
    
    # WRAP IN GLASS
    with st.container(border=True):
        st.markdown("### 💳 Digital Wallet")
        c1, c2 = st.columns([1, 2])
        with c1: st.metric("Balance", f"PKR {bal:,.2f}")
        
        conn = get_connection(); 
        if not conn: return
        cursor = conn.cursor()

        with c2:
            if role == 'Donor':
                with st.expander("➕ Deposit"):
                    amt = st.number_input("Amount", 500.0, step=500.0)
                    if st.button("Add Funds"):
                        try:
                            cursor.execute("EXEC sp_Wallet_AddFunds ?, ?", (user_id, amt))
                            conn.commit()
                            st.success("Added!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

            elif role == 'Beneficiary':
                with st.expander("💸 Withdraw"):
                    w_amt = st.number_input("Amount", 100.0, max_value=float(bal) if bal >= 100 else 100.0)
                    if st.button("Withdraw"):
                        if bal >= w_amt:
                            try:
                                cursor.execute("EXEC sp_Wallet_Withdraw ?, ?", (user_id, w_amt))
                                
                                # --- FIXED LOGIC ---
                                # Only fetch if the procedure returns data (cursor.description is not None)
                                if cursor.description:
                                    row = cursor.fetchone()
                                    conn.commit()
                                    if row and row[0] == 'SUCCESS':
                                        st.balloons()
                                        st.success("Withdrawn!")
                                        st.rerun()
                                    elif row:
                                        st.error(f"Server Message: {row[0]}")
                                else:
                                    # If no result returned, assume success if no error was raised
                                    conn.commit()
                                    st.balloons()
                                    st.success("Withdrawn Successfully!")
                                    st.rerun()
                                # -------------------
                                
                            except Exception as e:
                                st.error(f"Transaction Failed: {e}")
                        else:
                            st.error("Insufficient Funds")

            elif role == 'Admin':
                try:
                    st.dataframe(pd.read_sql("SELECT * FROM View_Global_Wallet_Stats", conn), use_container_width=True)
                except:
                    st.info("No Global Stats View found.")

    st.markdown("---")
    with st.expander("📜 History"):
        try:
            st.dataframe(pd.read_sql(f"SELECT LogDate, ActionType, Description FROM System_Logs WHERE UserID={user_id} AND ActionType IN ('DEPOSIT', 'WITHDRAWAL', 'GEN_DONATION', 'VOUCHER_GEN') ORDER BY LogDate DESC", conn), use_container_width=True)
        except: st.caption("No history.")

    conn.close()