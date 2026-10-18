import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

conn = sqlite3.connect('pro_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS stock (id INTEGER PRIMARY KEY, item TEXT, qty REAL, type TEXT, price REAL, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS khata (id INTEGER PRIMARY KEY, name TEXT, amount REAL, type TEXT, date TEXT)')
conn.commit()

st.set_page_config(page_title="Usman Technologies - Stock Manager", layout="wide", page_icon="💎")

# --- BRANDED CSS + SPRINKLE + USMAN TECHNOLOGIES ---
st.markdown("""
<style>
.stApp { background: #f0f2f6; }
.snow { position: fixed; top: -10px; z-index: 9999; font-size: 18px; animation: fall linear infinite; }
@keyframes fall { 0% {top:-10%} 100%{top:110%} }
.login-card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); text-align: center; margin-top: 30px; }
.brand-header { background: linear-gradient(90deg, #6c5ce7, #a29bfe); color: white; padding: 12px 20px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.brand-footer { background: #2d3436; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-top: 40px; font-size: 14px; }
</style>
<div class="snow" style="left:10%; animation-duration:6s;">✨</div>
<div class="snow" style="left:50%; animation-duration:7s;">💎</div>
<div class="snow" style="left:85%; animation-duration:6s;">✨</div>
""", unsafe_allow_html=True)

if 'entered' not in st.session_state:
    st.session_state.entered = False

# --- WELCOME PAGE WITH GOOGLE + BRANDING ---
if not st.session_state.entered:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <h2 style="color:#6c5ce7; margin-bottom:0;">USMAN TECHNOLOGIES</h2>
            <p style="letter-spacing:3px; color:#636e72; font-size:12px; font-weight:bold;">SOFTWARE SOLUTIONS</p>
            <hr>
            <h1 style="color:#2d3436;">Pro Stock Manager</h1>
            <p style="color:#636e72;">Secure Inventory & Credit Management System</p>
            <br>
        </div>
        """, unsafe_allow_html=True)
        
        # Google Button Design
        st.markdown("""
        <button style="background:white; border:1px solid #dadce0; border-radius:8px; padding:12px; width:100%; font-weight:500; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:10px;">
        <img src="https://www.google.com/favicon.ico" width="20"> Continue with Google
        </button>
        """, unsafe_allow_html=True)
        st.write("")
        
        if st.button("Continue to Dashboard ->", use_container_width=True, type="primary"):
            st.session_state.entered = True
            st.rerun()
            
        st.markdown("""
        <div style="text-align:center; margin-top:30px; color:gray; font-size:12px;">
        Developed & Maintained by<br>
        <b style="color:#6c5ce7; font-size:14px;">USMAN TECHNOLOGIES</b><br>
        Professional Web Solutions | 2026
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# --- MAIN APP WITH BRANDING ---
st.markdown("""
<div class="brand-header">
    <div><b>💎 USMAN TECHNOLOGIES</b> | Pro Stock System</div>
    <div style="font-size:12px;">v2.0 Professional</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    if st.button("← Logout"):
        st.session_state.entered = False
        st.rerun()
    st.markdown("### Developed by")
    st.markdown("**USMAN TECHNOLOGIES**")
    st.caption("Software Solutions Provider")
    st.divider()
    st.header("Add Data")
    with st.form("s1", clear_on_submit=True):
        item = st.text_input("Item Name")
        qty = st.number_input("Quantity", 1)
        price = st.number_input("Price per Unit", 1)
        t = st.selectbox("Type", ["STOCK IN", "STOCK OUT"])
        if st.form_submit_button("Save Stock"):
            c.execute("INSERT INTO stock (item, qty, type, price, date) VALUES (?,?,?,?,?)", (item, qty, t, price, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            st.rerun()
    with st.form("s2", clear_on_submit=True):
        name = st.text_input("Customer Name")
        amt = st.number_input("Amount", 1)
        kt = st.selectbox("Type", ["Credit Receivable", "Pending Cash", "Cash Outgoing"])
        if st.form_submit_button("Save Account"):
            c.execute("INSERT INTO khata (name, amount, type, date) VALUES (?,?,?,?)", (name, amt, kt, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            st.rerun()

df_stock = pd.read_sql_query("SELECT * FROM stock", conn)

c1, c2, c3 = st.columns(3)
c1.metric("Total Stock IN", int(df_stock[df_stock['type']=="STOCK IN"]['qty'].sum()) if not df_stock.empty else 0)
c2.metric("Total Stock OUT", int(df_stock[df_stock['type']=="STOCK OUT"]['qty'].sum()) if not df_stock.empty else 0)
c3.metric("Current Stock Left", int(df_stock[df_stock['type']=="STOCK IN"]['qty'].sum() - df_stock[df_stock['type']=="STOCK OUT"]['qty'].sum()) if not df_stock.empty else 0)

st.subheader("Profit / Loss Graph - Loss Down, Profit UP")
if not df_stock.empty:
    df_stock['value'] = df_stock['qty']*df_stock['price']
    df_stock['pnl'] = df_stock.apply(lambda x: x['value'] if x['type']=="STOCK OUT" else -x['value'], axis=1)
    df_stock['cumulative'] = df_stock['pnl'].cumsum()
    st.line_chart(df_stock, y="cumulative")
else:
    st.info("No data yet. Add stock to see graph.")

st.dataframe(df_stock, use_container_width=True)

# --- FOOTER ---
st.markdown("""
<div class="brand-footer">
    © 2026 <b>USMAN TECHNOLOGIES</b> - All Rights Reserved<br>
    Developed by Usman Technologies | Professional Web & Software Solutions<br>
    Contact: Usman Technologies | Chakwal, Pakistan
</div>
""", unsafe_allow_html=True)
