import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="USMAN TECHNOLOGIES | Premium SaaS", layout="wide", page_icon="💎")

# --- CSS Same as yours ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); background-attachment: fixed; }
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #3b82f6 100%);
        padding: 25px; border-radius: 20px; color: white; text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-bottom: 25px;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.92); backdrop-filter: blur(10px);
        padding: 18px; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.4);
    }
    .stButton>button {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        color: white; border-radius: 12px; height: 46px; font-weight: 600; border: none;
    }
    .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 22px; }
    .small-card { padding: 16px !important; }
    .pricing-card { border: 2px solid #3b82f6; text-align: center; }
    .pricing-card.pro { border-color: #f59e0b; background: linear-gradient(135deg, #fffbeb 0%, #ffffff 100%); transform: scale(1.05); }
</style>
""", unsafe_allow_html=True)

# --- DB SETUP UPDATED ---
def init_db():
    conn=sqlite3.connect('usman.db'); c=conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, plan TEXT DEFAULT "TRIAL", trial_start TEXT, sub_expiry TEXT, status TEXT DEFAULT "TRIAL", phone TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS stock_tx (id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT, product TEXT, tx_type TEXT, qty INTEGER, buy_price REAL, sell_price REAL, profit REAL, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT, name TEXT, type TEXT, amount REAL, date TEXT, notes TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cash_flow (id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT, type TEXT, amount REAL, reason TEXT, date TEXT)''')
    # Add new columns if old DB
    try: c.execute("ALTER TABLE users ADD COLUMN plan TEXT DEFAULT 'TRIAL'")
    except: pass
    try: c.execute("ALTER TABLE users ADD COLUMN trial_start TEXT")
    except: pass
    try: c.execute("ALTER TABLE users ADD COLUMN sub_expiry TEXT")
    except: pass
    try: c.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'TRIAL'")
    except: pass
    try: c.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    except: pass
    conn.commit(); conn.close()

def make_hash(p): return hashlib.sha256(str.encode(p)).hexdigest()
def check_hash(p,h): return make_hash(p)==h
init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False; st.session_state.username=""

# --- SUBSCRIPTION LOGIC ---
def check_subscription(username):
    conn=sqlite3.connect('usman.db'); c=conn.cursor()
    c.execute('SELECT plan, trial_start, sub_expiry, status FROM users WHERE username=?',(username,))
    data=c.fetchone(); conn.close()
    if not data: return True
    plan, trial_start, sub_expiry, status = data
    
    # Admin (aap) ka account hamesha active
    if username.lower() in ["usman", "admin", "muhammad usman"]:
        return True
    if status == "ACTIVE":
        if sub_expiry:
            expiry_date = datetime.strptime(sub_expiry, "%Y-%m-%d")
            if datetime.now() <= expiry_date: return True
        else: return True
    
    # Trial check (7 din)
    if trial_start:
        start_date = datetime.strptime(trial_start, "%Y-%m-%d")
        if datetime.now() <= start_date + timedelta(days=7):
            days_left = (start_date + timedelta(days=7) - datetime.now()).days
            st.sidebar.warning(f"Trial: {days_left} din baqi")
            return True
    return False

def show_lock_screen():
    st.markdown('<div class="main-header"><h2>🔒 Subscription Khatam!</h2></div>', unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        st.markdown('<div class="glass-card pricing-card"><h3>BASIC</h3><h1>Rs. 1500</h1><p>/Month</p><hr><p>✅ Stock & Sale<br>✅ 1 User<br>✅ Basic Support</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card pricing-card pro"><h3>🔥 PRO - MOST POPULAR</h3><h1>Rs. 3000</h1><p>/Month</p><hr><p>✅ Sab Kuch BASIC wala<br>✅ Barcode + Bill Print<br>✅ Unlimited Staff<br>✅ WhatsApp Support</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card" style="margin-top:25px; text-align:center;">', unsafe_allow_html=True)
    st.error("Aapka 7 din ka free trial khatam ho gaya hai.")
    st.markdown(f"""
    <h3>Easypaisa par Rs. 3000 bhejein</h3>
    <h1 style="color:#1e3a8a;">03120914675</h1>
    <p><b>Name:</b> Muhammad Usman</p>
    <p>Screenshot WhatsApp par bhejein, account 5 minute me active ho jayega.</p>
    """, unsafe_allow_html=True)
    st.link_button("📱 WhatsApp par Screenshot Bhejein", "https://wa.me/923120914675?text=Salam%20Usman%20bhai%2C%20me%20ne%203000%20bheja%20hai%20USMAN%20POS%20ke%20liye.%20Username%3A%20"+st.session_state.username)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Logout"): st.session_state.logged_in=False; st.rerun()
    st.stop()

def login_page():
    st.markdown('<div class="main-header"><h1>💎 USMAN TECHNOLOGIES</h1><p>Enterprise Business Management Platform - Ab Rs. 3000/Month</p></div>', unsafe_allow_html=True)
    col1,col2,col3=st.columns([1,2,1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t1,t2=st.tabs(["LOGIN","CREATE ACCOUNT (7 DIN FREE)"])
        with t1:
            u=st.text_input("Username", placeholder="Enter username"); p=st.text_input("Password", type="password", placeholder="Password")
            if st.button("LOGIN SECURELY"):
                conn=sqlite3.connect('usman.db'); c=conn.cursor(); c.execute('SELECT password FROM users WHERE username=?',(u,)); d=c.fetchone(); conn.close()
                if d and check_hash(p,d[0]): st.session_state.logged_in=True; st.session_state.username=u; st.rerun()
                else: st.error("Incorrect Username or Password")
        with t2:
            nu=st.text_input("New Username", key="nu"); np=st.text_input("New Password", type="password", key="np"); phone=st.text_input("WhatsApp Number")
            if st.button("START 7 DAYS FREE TRIAL"):
                if nu and np:
                    conn=sqlite3.connect('usman.db'); c=conn.cursor()
                    try: 
                        c.execute('INSERT INTO users (username,password,plan,trial_start,status,phone) VALUES (?,?,?,?,?,?)',(nu,make_hash(np),"TRIAL",datetime.now().strftime("%Y-%m-%d"),"TRIAL",phone))
                        conn.commit(); st.success("Account Created! 7 Din Free Trial Shuru. Ab Login Karo."); 
                    except: st.error("Username Exists")
                    conn.close()
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in: login_page(); st.stop()

owner=st.session_state.username

# CHECK SUBSCRIPTION BEFORE SHOWING APP
if not check_subscription(owner):
    show_lock_screen()

# --- ADMIN PANEL ---
is_admin = owner.lower() in ["usman", "admin", "muhammad usman", "03120914675"]

with st.sidebar:
    st.markdown(f"### Welcome, {owner}"); 
    if is_admin: st.success("👑 ADMIN ACCESS")
    st.divider()
    menu_options = ["📊 Dashboard & Graph","📦 Stock IN / OUT","📋 Current Stock","👥 Credit & Pending","💰 Cash Flow"]
    if is_admin: menu_options.append("🔐 ADMIN - Activate Users")
    menu=st.radio("Navigation", menu_options)
    st.divider()
    if st.button("Logout"): st.session_state.logged_in=False; st.rerun()

# ... AAPKA BAAQI KA DASHBOARD CODE WAHI RAHEGA ...
# Neeche wala hissa aapka purana wala hi hai

st.markdown(f'<div class="main-header"><h2>Premium Business Dashboard</h2><p>USMAN TECHNOLOGIES • {owner} | {datetime.now().strftime("%B %Y")}</p></div>', unsafe_allow_html=True)

conn=sqlite3.connect('usman.db')
df_tx=pd.read_sql_query("SELECT * FROM stock_tx WHERE owner=?",conn,params=(owner,))
df_cust=pd.read_sql_query("SELECT * FROM customers WHERE owner=?",conn,params=(owner,))
df_cash=pd.read_sql_query("SELECT * FROM cash_flow WHERE owner=?",conn,params=(owner,))
conn.close()

# ADMIN PANEL LOGIC
if "ADMIN" in menu and is_admin:
    st.subheader("🔐 ADMIN - User Activation")
    conn=sqlite3.connect('usman.db')
    df_users=pd.read_sql_query("SELECT username, plan, trial_start, sub_expiry, status, phone FROM users",conn)
    conn.close()
    st.dataframe(df_users, use_container_width=True)
    
    with st.form("activate_form"):
        uname=st.selectbox("Select User to Activate", df_users['username'].tolist())
        plan_select=st.selectbox("Plan", ["BASIC - 1500", "PRO - 3000"])
        days=st.number_input("Kitne Din ke Liye Active Karna Hai?", value=30)
        if st.form_submit_button("✅ ACTIVATE KARO"):
            expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            conn=sqlite3.connect('usman.db'); c=conn.cursor()
            c.execute('UPDATE users SET status="ACTIVE", sub_expiry=?, plan=? WHERE username=?',(expiry, plan_select, uname))
            conn.commit(); conn.close()
            st.success(f"{uname} ko {days} din ke liye Active kar diya!")
            st.balloons()

# ... Baaqi Dashboard, Stock IN/OUT wala code yahan se neeche paste karna hai same as before ...
elif "Dashboard" in menu:
    total_in = df_tx[df_tx['tx_type']=='IN']['qty'].sum() if not df_tx.empty else 0
    total_out = df_tx[df_tx['tx_type']=='OUT']['qty'].sum() if not df_tx.empty else 0
    current_stock_qty = total_in - total_out
    total_profit = df_tx['profit'].sum() if not df_tx.empty else 0
    color = "#10b981" if total_profit>=0 else "#ef4444"
    st.markdown(f"""
    <div class="metric-grid">
        <div class="glass-card small-card"><h4>Total IN</h4><h2>{int(total_in)}</h2></div>
        <div class="glass-card small-card"><h4>Total OUT</h4><h2>{int(total_out)}</h2></div>
        <div class="glass-card small-card"><h4>Stock Left</h4><h2>{int(current_stock_qty)}</h2></div>
        <div class="glass-card small-card" style="border-left:4px solid {color}"><h4>Profit / Loss</h4><h2>Rs. {total_profit:,.0f}</h2></div>
    </div>
    """, unsafe_allow_html=True)
    if not df_tx.empty:
        df_sorted = df_tx.sort_values('date')
        df_sorted['cumulative_profit'] = df_sorted['profit'].cumsum()
        st.line_chart(df_sorted[['cumulative_profit']])
    else: st.info("Add Stock to see graphs.")

# Baaqi tabs aapke purane code se copy kar lena
