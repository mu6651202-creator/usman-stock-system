import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime
import random

st.set_page_config(page_title="USMAN TECHNOLOGIES | Premium", layout="wide", page_icon="💎")

# --- PREMIUM DESIGN + SMALL LIVE SPRINKLES UP-DOWN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        background-attachment: fixed;
    }
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #3b82f6 100%);
        padding: 25px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 25px;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.3);
    }
    .stButton>button {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        color: white;
        border-radius: 12px;
        height: 48px;
        font-weight: 600;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(30,58,138,0.4);
    }
    .sprinkle-bg {
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    .dot {
        position: absolute;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        opacity: 0.7;
        animation: floatUpDown 4s ease-in-out infinite;
    }
    @keyframes floatUpDown {
        0% { transform: translateY(100vh) translateX(0) scale(0.5); opacity: 0; }
        10% { opacity: 0.8; }
        50% { transform: translateY(50vh) translateX(20px) scale(1); opacity: 1; }
        90% { opacity: 0.8; }
        100% { transform: translateY(-10vh) translateX(-20px) scale(0.5); opacity: 0; }
    }
    .dot2 {
        position: absolute;
        width: 4px;
        height: 4px;
        border-radius: 50%;
        opacity: 0.5;
        animation: floatDownUp 6s ease-in-out infinite;
    }
    @keyframes floatDownUp {
        0% { transform: translateY(-10vh) translateX(0); opacity: 0; }
        50% { transform: translateY(50vh) translateX(-15px); opacity: 0.7; }
        100% { transform: translateY(110vh) translateX(15px); opacity: 0; }
    }
</style>
""", unsafe_allow_html=True)

def inject_sprinkles():
    colors = ["#3b82f6","#10b981","#f59e0b","#ef4444","#8b5cf6","#ec4899","#06b6d4"]
    html = '<div class="sprinkle-bg">'
    for i in range(40):
        left = random.randint(0, 100)
        delay = random.uniform(0, 5)
        duration = random.uniform(3, 7)
        color = random.choice(colors)
        size = random.randint(4, 7)
        cls = "dot" if i % 2 == 0 else "dot2"
        html += f'<div class="{cls}" style="left:{left}%; background:{color}; width:{size}px; height:{size}px; animation-delay:{delay}s; animation-duration:{duration}s;"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

inject_sprinkles()

def show_celebration():
    st.balloons()
    st.toast("✨ Transaction Saved!", icon="🎉")

def init_db():
    conn=sqlite3.connect('usman.db')
    c=conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS stock_tx 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT, product TEXT, tx_type TEXT, qty INTEGER, buy_price REAL, sell_price REAL, profit REAL, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT, name TEXT, type TEXT, amount REAL, date TEXT, notes TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cash_flow
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT, type TEXT, amount REAL, reason TEXT, date TEXT)''')
    conn.commit(); conn.close()

def make_hash(p): return hashlib.sha256(str.encode(p)).hexdigest()
def check_hash(p,h): return make_hash(p)==h
init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False
    st.session_state.username=""

def login_page():
    st.markdown('<div class="main-header"><h1>💎 USMAN TECHNOLOGIES</h1><p>Enterprise Business Management Platform</p></div>', unsafe_allow_html=True)
    col1,col2,col3=st.columns([1,2,1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t1,t2=st.tabs(["LOGIN","CREATE ACCOUNT"])
        with t1:
            u=st.text_input("Username", placeholder="Enter your username")
            p=st.text_input("Password", type="password", placeholder="Enter password")
            if st.button("LOGIN SECURELY"):
                conn=sqlite3.connect('usman.db'); c=conn.cursor()
                c.execute('SELECT password FROM users WHERE username=?',(u,)); d=c.fetchone(); conn.close()
                if d and check_hash(p,d[0]): st.session_state.logged_in=True; st.session_state.username=u; st.rerun()
                else: st.error("Incorrect Username or Password")
        with t2:
            nu=st.text_input("New Username", key="nu"); np=st.text_input("New Password", type="password", key="np")
            if st.button("CREATE ACCOUNT"):
                if nu and np:
                    conn=sqlite3.connect('usman.db'); c=conn.cursor()
                    try: c.execute('INSERT INTO users VALUES (?,?)',(nu,make_hash(np))); conn.commit(); st.success("Account Created! Please Login."); show_celebration()
                    except: st.error("Username Already Exists")
                    conn.close()
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    login_page(); st.stop()

owner=st.session_state.username
with st.sidebar:
    st.markdown(f"### Welcome, {owner}")
    st.write("Premium Dashboard")
    st.divider()
    menu=st.radio("Navigation", ["📊 Dashboard & Graph","📦 Stock IN / OUT","📋 Current Stock","👥 Credit & Pending","💰 Cash Flow"])
    st.divider()
    if st.button("Logout"): st.session_state.logged_in=False; st.rerun()

st.markdown(f'<div class="main-header"><h2>Premium Business Dashboard</h2><p>USMAN TECHNOLOGIES • Enterprise Stock & Ledger System | {datetime.now().strftime("%B %Y")}</p></div>', unsafe_allow_html=True)

conn=sqlite3.connect('usman.db')
df_tx=pd.read_sql_query("SELECT * FROM stock_tx WHERE owner=?",conn,params=(owner,))
df_cust=pd.read_sql_query("SELECT * FROM customers WHERE owner=?",conn,params=(owner,))
df_cash=pd.read_sql_query("SELECT * FROM cash_flow WHERE owner=?",conn,params=(owner,))
conn.close()

if "Dashboard" in menu:
    total_in = df_tx[df_tx['tx_type']=='IN']['qty'].sum() if not df_tx.empty else 0
    total_out = df_tx[df_tx['tx_type']=='OUT']['qty'].sum() if not df_tx.empty else 0
    current_stock_qty = total_in - total_out
    total_profit = df_tx['profit'].sum() if not df_tx.empty else 0
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(f'<div class="glass-card"><h4>Total IN</h4><h2>{int(total_in)}</h2></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="glass-card"><h4>Total OUT</h4><h2>{int(total_out)}</h2></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="glass-card"><h4>Stock Left</h4><h2>{int(current_stock_qty)}</h2></div>', unsafe_allow_html=True)
    with c4: color = "#10b981" if total_profit>=0 else "#ef4444"; st.markdown(f'<div class="glass-card" style="border-left:5px solid {color}"><h4>Profit / Loss</h4><h2>Rs. {total_profit:,.0f}</h2></div>', unsafe_allow_html=True)
    st.divider()
    st.subheader("📈 Profit / Loss Graph - Goes Down If Loss")
    if not df_tx.empty:
        df_sorted = df_tx.sort_values('date')
        df_sorted['cumulative_profit'] = df_sorted['profit'].cumsum()
        df_sorted['c_stock'] = df_sorted.apply(lambda x: x['qty'] if x['tx_type']=='IN' else -x['qty'], axis=1).cumsum()
        st.line_chart(df_sorted[['cumulative_profit']], height=280)
        st.write("Stock Level Graph")
        st.area_chart(df_sorted[['c_stock']], height=250)
    else:
        st.info("Add some Stock IN/OUT to see graphs.")
elif "Stock IN" in menu:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Stock Movement")
    with st.form("tx_form"):
        col1,col2=st.columns(2)
        with col1:
            product=st.text_input("Product Name *", placeholder="e.g. iPhone Cover")
            tx_type=st.selectbox("Type *", ["IN - Stock Coming (Kharid)", "OUT - Stock Going (Sale)"])
            qty=st.number_input("Quantity *", min_value=1, step=1)
        with col2:
            buy_price=st.number_input("Buy Price Rs.", min_value=0.0)
            sell_price=st.number_input("Sell Price Rs.", min_value=0.0)
            date=st.date_input("Date", value=datetime.now())
        if st.form_submit_button("💾 SAVE TRANSACTION"):
            if product:
                real_type="IN" if "IN" in tx_type else "OUT"
                profit=(sell_price-buy_price)*qty if real_type=="OUT" else 0
                conn=sqlite3.connect('usman.db'); c=conn.cursor()
                c.execute('INSERT INTO stock_tx (owner,product,tx_type,qty,buy_price,sell_price,profit,date) VALUES (?,?,?,?,?,?,?,?)',
                          (owner,product,real_type,qty,buy_price,sell_price,profit,str(date)))
                conn.commit(); conn.close()
                st.success(f"Saved! Profit: Rs. {profit}"); show_celebration()
    st.markdown('</div>', unsafe_allow_html=True)
elif "Current Stock" in menu:
    st.subheader("📋 Current Stock Left")
    if not df_tx.empty:
        summary = df_tx.groupby('product').apply(lambda x: pd.Series({
            'Total IN': x[x['tx_type']=='IN']['qty'].sum(),
            'Total OUT': x[x['tx_type']=='OUT']['qty'].sum(),
            'Current Left': x[x['tx_type']=='IN']['qty'].sum() - x[x['tx_type']=='OUT']['qty'].sum(),
            'Total Profit': x['profit'].sum()
        })).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.bar_chart(summary.set_index('product')['Current Left'])
    else: st.info("No data yet.")
elif "Credit" in menu:
    st.subheader("👥 Credit & Pending Customers")
    with st.form("cust_form"):
        col1,col2=st.columns(2)
        with col1:
            name=st.text_input("Customer Name *")
            c_type=st.selectbox("Type *", ["CREDIT - He has to pay me","PENDING - My cash is pending"])
        with col2:
            amount=st.number_input("Amount Rs. *", min_value=0.0)
            notes=st.text_input("Notes")
        if st.form_submit_button("Add Customer"):
            if name:
                real_c_type="CREDIT" if "CREDIT" in c_type else "PENDING"
                conn=sqlite3.connect('usman.db'); c=conn.cursor()
                c.execute('INSERT INTO customers (owner,name,type,amount,date,notes) VALUES (?,?,?,?,?,?)',
                          (owner,name,real_c_type,amount,str(datetime.now().date()),notes))
                conn.commit(); conn.close()
                st.success("Customer Added!"); show_celebration()
    if not df_cust.empty:
        st.dataframe(df_cust[['name','type','amount','date','notes']], use_container_width=True, hide_index=True)
elif "Cash Flow" in menu:
    st.subheader("💰 Cash IN / OUT")
    with st.form("cash_form"):
        col1,col2=st.columns(2)
        with col1:
            cash_type=st.selectbox("Type", ["CASH OUT - Going","CASH IN - Coming"])
            amount=st.number_input("Amount Rs.", min_value=0.0)
        with col2:
            reason=st.text_input("Reason", placeholder="e.g. Rent, Bill")
        if st.form_submit_button("Save Cash"):
            real_cash="OUT" if "OUT" in cash_type else "IN"
            conn=sqlite3.connect('usman.db'); c=conn.cursor()
            c.execute('INSERT INTO cash_flow (owner,type,amount,reason,date) VALUES (?,?,?,?,?)',
                      (owner,real_cash,amount,reason,str(datetime.now().date())))
            conn.commit(); conn.close()
            st.success(f"Cash {real_cash} Saved!"); show_celebration()
    if not df_cash.empty:
        st.dataframe(df_cash[['type','amount','reason','date']], use_container_width=True, hide_index=True)
