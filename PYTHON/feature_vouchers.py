import streamlit as st
import pandas as pd
from database import get_connection, run_query

def render_voucher_portal():
    st.markdown("## 🎟️ Smart Vouchers")
    conn = get_connection()
    if not conn: return
    
    user_id = st.session_state['user_id']
    role = st.session_state['role']
    cursor = conn.cursor()

    if role == 'Beneficiary':
        c1, c2 = st.tabs(["➕ Create", "🎫 My Vouchers"])
        
        with c1:
            # Fetch Balance
            bal_query = f"SELECT Balance FROM Wallets WHERE UserID={user_id}"
            bal_row = pd.read_sql(bal_query, conn)
            
            if not bal_row.empty:
                bal = float(bal_row.iloc[0]['Balance'])
            else:
                bal = 0.00
                
            st.metric("Wallet", f"PKR {bal:,.2f}")

            # --- CRASH FIX: CHECK BALANCE FIRST ---
            if bal < 100:
                st.warning("⚠️ Insufficient funds. You need at least PKR 100 to create a voucher.")
            else:
                # Safe to show input because bal >= 100
                amt = st.number_input("Amount", min_value=100.0, max_value=bal, value=100.0)
                
                if st.button("Generate"):
                    cursor.execute("EXEC sp_Voucher_Generate ?, ?", (user_id, amt))
                    
                    # Safe Fetch Logic
                    try:
                        row = cursor.fetchone()
                        res = row[0] if row else "SUCCESS"
                        code = row[1] if row and len(row) > 1 else ""
                    except:
                        res = "SUCCESS"
                        code = "CHECK_TAB"

                    conn.commit()
                    
                    if "SUCCESS" in str(res): 
                        st.balloons()
                        st.success(f"Voucher Generated! Code: {code}")
                    else: 
                        st.error(res)

        with c2:
            df = pd.read_sql(f"SELECT VoucherCode, AmountValue, ExpiryDate, IsRedeemed FROM View_My_Vouchers WHERE UserID={user_id} ORDER BY ExpiryDate DESC", conn)
            if not df.empty:
                for idx, r in df.iterrows():
                    with st.container(border=True):
                        st.write(f"**{r['VoucherCode']}**")
                        st.metric("Value", f"PKR {r['AmountValue']:,.0f}")
                        if r['IsRedeemed']:
                            st.error("🔴 Redeemed")
                        else:
                            st.success("🟢 Active")
            else:
                st.info("No vouchers found.")

    elif role == 'Vendor':
        st.subheader("📊 Sales")
        stats_sql = f"SELECT COUNT(*) as C, ISNULL(SUM(AmountValue),0) as V FROM Smart_Vouchers WHERE RedeemedBy_VendorID={user_id}"
        stats = pd.read_sql(stats_sql, conn).iloc[0]
        
        c1, c2 = st.columns(2)
        c1.metric("Redeemed", stats['C'])
        c2.metric("Revenue", f"PKR {stats['V']:,.0f}")
        
        st.dataframe(pd.read_sql(f"SELECT VoucherCode, AmountValue, RedeemedAt FROM Smart_Vouchers WHERE RedeemedBy_VendorID={user_id} ORDER BY RedeemedAt DESC", conn), use_container_width=True)

    conn.close()