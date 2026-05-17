import streamlit as st
import pandas as pd
from database import get_connection

def show_dashboard():
    st.title("🏪 Vendor Terminal")
    
    conn = get_connection()
    if not conn: return
    vendor_id = st.session_state['user_id']
    cursor = conn.cursor()

    # --- TOP METRICS (Glass Card) ---
    with st.container(border=True):
        st.subheader("📊 Shop Performance")
        
        # Calculate Total Earnings
        bal_row = pd.read_sql(f"SELECT Balance FROM Wallets WHERE UserID={vendor_id}", conn)
        balance = bal_row.iloc[0]['Balance'] if not bal_row.empty else 0.0
        
        # Calculate Redeemed Count
        count = pd.read_sql(f"SELECT COUNT(*) FROM Smart_Vouchers WHERE RedeemedBy_VendorID={vendor_id}", conn).iloc[0,0]

        c1, c2 = st.columns(2)
        c1.metric("🏪 Wallet Earnings", f"PKR {balance:,.2f}")
        c2.metric("🎟️ Vouchers Redeemed", count)

    st.markdown("---")

    # ==========================================
    # TABS
    # ==========================================
    tab_redeem, tab_hist = st.tabs(["📲 Scanner", "📜 History"])

    # ------------------------------------------
    # TAB 1: REDEEM (The Scanner)
    # ------------------------------------------
    with tab_redeem:
        # Wrap Scanner in Glass
        with st.container(border=True):
            st.subheader("Voucher Validation")
            st.caption("Enter the code provided by the beneficiary to verify identity.")

            # INPUT AREA
            v_code = st.text_input("Enter Voucher Code", placeholder="e.g., V-12345").strip()
            
            # STATE MANAGEMENT
            if 'checked_voucher' not in st.session_state:
                st.session_state['checked_voucher'] = None

            # CHECK BUTTON
            if st.button("🔍 Check Validity", use_container_width=True):
                if v_code:
                    cursor.execute("EXEC sp_Vendor_CheckVoucher ?", (v_code,))
                    row = cursor.fetchone()
                    
                    if row and row[0] == 'VALID':
                        st.session_state['checked_voucher'] = {
                            'code': v_code,
                            'amount': row[1],
                            'expiry': row[2],
                            'title': row[3],
                            'mask_name': row[4],  # Last 5 Chars
                            'mask_cnic': row[5]   # Last 5 Digits
                        }
                    else:
                        st.error("❌ Invalid or Expired Voucher")
                        st.session_state['checked_voucher'] = None
                else:
                    st.warning("Please enter a code.")

        # VERIFICATION RESULT (Glass Card)
        if st.session_state['checked_voucher'] and st.session_state['checked_voucher']['code'] == v_code:
            data = st.session_state['checked_voucher']
            
            st.success("✅ **Voucher is VALID**")
            
            with st.container(border=True):
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Value", f"PKR {data['amount']:,.0f}")
                    st.caption(f"Expires: {data['expiry']}")
                    st.write(f"**Request:** {data['title']}")
                
                with c2:
                    st.markdown("#### 🆔 Identify Customer")
                    st.info(f"Name ends in: **...{data['mask_name']}**")
                    st.info(f"CNIC ends in: **...{data['mask_cnic']}**")

                st.markdown("---")
                # REDEEM BUTTON (Primary Action)
                if st.button("💰 Process Redemption & Collect Cash", type="primary", use_container_width=True):
                    try:
                        cursor.execute("EXEC sp_Vendor_RedeemVoucher ?, ?", (data['code'], vendor_id))
                        res = cursor.fetchone()[0]
                        conn.commit()
                        
                        if "SUCCESS" in res:
                            st.balloons()
                            st.success(f"Transaction Complete! PKR {data['amount']} added to your wallet.")
                            st.session_state['checked_voucher'] = None 
                            st.rerun()
                        else:
                            st.error(res)
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ------------------------------------------
    # TAB 2: HISTORY
    # ------------------------------------------
    with tab_hist:
        st.subheader("Redemption Logs")
        hist_query = f"""
        SELECT 
            VoucherCode, 
            AmountValue AS [Amount (PKR)], 
            RedeemedAt AS [Date Time]
        FROM Smart_Vouchers 
        WHERE RedeemedBy_VendorID = {vendor_id}
        ORDER BY RedeemedAt DESC
        """
        st.dataframe(pd.read_sql(hist_query, conn), use_container_width=True)

    conn.close()