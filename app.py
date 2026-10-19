import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="USMAN TECHNOLOGIES | Premium SaaS", layout="wide", page_icon="💎")

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
    .pricing-card { border: 2px solid #3b82f6; text-align: center; border-radius: 16px; }
    .pricing-card.pro { border-color: #f59e0b; background: linear-gradient(135deg, #fffbeb 0%, #ffffff 100%); transform: scale(1.02); }
    @media only screen and (max-width: 768px) {
        .metric-grid { grid-template-columns: repeat(2, 1fr) !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIG ---
EASYPAISA_NUMBER = "03120914675"
EASYPAISA_TITLE = "Muhammad Usman"

def init_db():
    conn=sqlite3.connect('usman.db'); c=conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, plan TEXT DEFAULT "TRIAL", trial_start TEXT, sub_expiry TEXT, status TEXT DEFAULT "TRIAL", phone TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS stock_tx (id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT, product TEXT, tx_type TEXT, qty INTEGER, buy_price REAL, sell_price REAL, profit REAL, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT, name TEXT, type TEXT, amount REAL, date TEXT, notes TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cash_flow (id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT, type TEXT, amount REAL, reason TEXT, date TEXT)''')
    conn.commit(); conn.close()

def make_hash(p): return hashlib.sha256(str.encode(p)).hexdigest()
def check_hash(p,h): return make_hash(p)==h
init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False; st.session_state.username=""

def check_subscription(username):
    conn=sqlite3.connect('usman.db'); c=conn.cursor()
    c.execute('SELECT trial_start, sub_expiry, status FROM users WHERE username=?',(username,))
    data=c.fetchone(); conn.close()
    if not data: return True
    trial_start, sub_expiry, status = data
    if username.lower() in ["usman", "admin", "muhammad usman", "usman1234"]:
        return True
    if status == "ACTIVE" and sub_expiry:
        try:
            expiry_date = datetime.strptime(sub_expiry, "%Y-%m-%d")
            if datetime.now() <= expiry_date: return True
        except: pass
    if trial_start:
        try:
            start_date = datetime.strptime(trial_start, "%Y-%m-%d")
            if datetime.now() <= start_date + timedelta(days=7):
                days_left = (start_date + timedelta(days=7) - datetime.now()).days
                st.sidebar.warning(f"Trial: {days_left} days left")
                return True
        except: pass
    return False

def show_lock_screen():
    st.markdown('<div class="main-header"><h2>🔒 Subscription Expired</h2><p>Your 7-day free trial has ended</p></div>', unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        st.markdown('<div class="glass-card pricing-card"><h3>BASIC</h3><h1>Rs. 1500</h1><p>/Month</p><hr><p>✅ Stock & Sales<br>✅ 1 User<br>✅ Basic Support</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card pricing-card pro"><h3>🔥 PRO - MOST POPULAR</h3><h1>Rs. 3000</h1><p>/Month</p><hr><p>✅ Everything in BASIC<br>✅ Barcode + Bill Print<br>✅ Unlimited Staff<br>✅ Premium Support</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card" style="margin-top:25px; text-align:center;">', unsafe_allow_html=True)
    st.markdown(f"""
    <h3>Please Pay via Easypaisa</h3>
    <h1 style="color:#1e3a8a;">{EASYPAISA_NUMBER}</h1>
    <p><b>Account Title:</b> {EASYPAISA_TITLE}</p>
    <p>After payment, send screenshot on WhatsApp. Your account will be activated within 5 minutes.</p>
    """, unsafe_allow_html=True)
    st.link_button("📱 Send Screenshot on WhatsApp", f"https://wa.me/923120914675?text=Hello%20Usman,%20I%20paid%20Rs%203000%20for%20USMAN%20POS.%20Username:%20{st.session_state.username}")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Logout"): st.session_state.logged_in=False; st.rerun()
    st.stop()

def login_page():
    st.markdown('<div class="main-header"><h1>💎 USMAN TECHNOLOGIES</h1><p>Enterprise Business Management Platform - Rs. 3000 / Month</p></div>', unsafe_allow_html=True)
    col1,col2,col3=st.columns([1,2,1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t1,t2=st.tabs(["LOGIN","CREATE ACCOUNT - 7 DAYS FREE"])
        with t1:
            u=st.text_input("Username", placeholder="Enter username"); p=st.text_input("Password", type="password", placeholder="Enter password")
            if st.button("LOGIN SECURELY"):
                conn=sqlite3.connect('usman.db'); c=conn.cursor(); c.execute('SELECT password FROM users WHERE username=?',(u,)); d=c.fetchone(); conn.close()
                if d and check_hash(p,d[0]): st.session_state.logged_in=True; st.session_state.username=u; st.rerun()
                else: st.error("Incorrect Username or Password")
        with t2:
            nu=st.text_input("Choose Username", key="nu"); np=st.text_input("Choose Password", type="password", key="np"); phone=st.text_input("WhatsApp Number", placeholder="03XX-XXXXXXX")
            if st.button("START 7 DAYS FREE TRIAL"):
                if nu and np:
                    conn=sqlite3.connect('usman.db'); c=conn.cursor()
                    try: 
                        c.execute('INSERT INTO users (username,password,plan,trial_start,status,phone) VALUES (?,?,?,?,?,?)',(nu,make_hash(np),"TRIAL",datetime.now().strftime("%Y-%m-%d"),"TRIAL",phone))
                        conn.commit(); st.success("Account Created! 7 Days Free Trial Started. Please Login Now."); 
                    except: st.error("Username Already Exists")
                    conn.close()
                else: st.warning("Please fill all fields")
        st.markdown('</div>', unsafe_allow_html=True)
        st.info(f"💰 Payment: Easypaisa {EASYPAISA_NUMBER} | Title: {EASYPAISA_TITLE}")

if not st.session_state.logged_in: login_page(); st.stop()

owner=st.session_state.username
if not check_subscription(owner): show_lock_screen()

is_admin = owner.lower() in ["usman", "admin", "muhammad usman", "usman1234"]

with st.sidebar:
    st.markdown(f"### Welcome, {owner}"); 
    if is_admin: st.success("👑 ADMIN ACCESS")
    st.divider()
    menu_options = ["📊 Dashboard & Graph","📦 Stock IN / OUT","📋 Current Stock","👥 Credit & Pending","💰 Cash Flow"]
    if is_admin: menu_options.append("🔐 ADMIN - Activate Users")
    menu=st.radio("Navigation", menu_options)
    st.divider()
    st.markdown(f"""
    <div style="background:white; padding:12px; border-radius:12px; text-align:center; border:1px solid #e2e8f0;">
    <p style="margin:0; font-size:12px; color:gray;">EASYPAISA PAYMENT</p>
    <h3 style="margin:5px 0; color:#1e3a8a;">{EASYPAISA_NUMBER}</h3>
    <p style="margin:0; font-size:12px;"><b>{EASYPAISA_TITLE}</b><br>Rs. 3000 / Month</p>
    </div>
    """, unsafe_allow_html=True)
    st.link_button("📱 Pay on WhatsApp", f"https://wa.me/923120914675")
    st.divider()
    if st.button("Logout"): st.session_state.logged_in=False; st.rerun()

st.markdown(f'<div class="main-header"><h2>Premium Business Dashboard</h2><p>USMAN TECHNOLOGIES • {owner} | {datetime.now().strftime("%B %Y")}</p></div>', unsafe_allow_html=True)

conn=sqlite3.connect('usman.db')
df_tx=pd.read_sql_query("SELECT * FROM stock_tx WHERE owner=?",conn,params=(owner,))
df_cust=pd.read_sql_query("SELECT * FROM customers WHERE owner=?",conn,params=(owner,))
df_cash=pd.read_sql_query("SELECT * FROM cash_flow WHERE owner=?",conn,params=(owner,))
conn.close()

if "ADMIN" in menu and is_admin:
    st.subheader("🔐 ADMIN - User Activation Panel")
    conn=sqlite3.connect('usman.db')
    df_users=pd.read_sql_query("SELECT username, plan, trial_start, sub_expiry, status, phone FROM users",conn)
    conn.close()
    st.dataframe(df_users, use_container_width=True, hide_index=True)
    with st.form("activate_form"):
        st.write("Activate User Account")
        uname=st.selectbox("Select User", df_users['username'].tolist() if not df_users.empty else ["No Users"])
        plan_select=st.selectbox("Plan", ["BASIC - Rs. 1500", "PRO - Rs. 3000"])
        days=st.number_input("Activate for how many days?", value=30, min_value=1)
        if st.form_submit_button("✅ ACTIVATE NOW"):
            expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            conn=sqlite3.connect('usman.db'); c=conn.cursor()
            c.execute('UPDATE users SET status="ACTIVE", sub_expiry=?, plan=? WHERE username=?',(expiry, plan_select, uname))
            conn.commit(); conn.close()
            st.success(f"{uname} activated for {days} days!"); st.balloons()

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
    st.subheader("📈 Profit / Loss Graph")
    if not df_tx.empty:
        df_sorted = df_tx.sort_values('date')
        df_sorted['cumulative_profit'] = df_sorted['profit'].cumsum()
        st.line_chart(df_sorted[['cumulative_profit']])
    else: st.info("Add some Stock IN/OUT to see graphs.")

elif "Stock IN" in menu:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Stock Movement")
    with st.form("tx_form"):
        col1,col2=st.columns(2)
        with col1:
            product=st.text_input("Product Name *", placeholder="e.g. iPhone Cover")
            tx_type=st.selectbox("Type *", ["IN - Stock Coming", "OUT - Stock Going (Sale)"])
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
                c.execute('INSERT INTO stock_tx (owner,product,tx_type,qty,buy_price,sell_price,profit,date) VALUES (?,?,?,?,?,?,?,?)',(owner,product,real_type,qty,buy_price,sell_price,profit,str(date)))
                conn.commit(); conn.close(); st.success(f"Saved! Profit: Rs. {profit}"); st.balloons()
    st.markdown('</div>', unsafe_allow_html=True)

elif "Current Stock" in menu:
    st.subheader("📋 Current Stock Left")
    if not df_tx.empty:
        summary = df_tx.groupby('product').apply(lambda x: pd.Series({'Total IN': x[x['tx_type']=='IN']['qty'].sum(),'Total OUT': x[x['tx_type']=='OUT']['qty'].sum(),'Current Left': x[x['tx_type']=='IN']['qty'].sum() - x[x['tx_type']=='OUT']['qty'].sum(),'Total Profit': x['profit'].sum()})).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True); st.bar_chart(summary.set_index('product')['Current Left'])
    else: st.info("No data yet.")

elif "Credit" in menu:
    st.subheader("👥 Credit & Pending Customers")
    with st.form("cust_form"):
        col1,col2=st.columns(2)
        with col1:
            name=st.text_input("Customer Name *")
            c_type=st.selectbox("Type *", ["CREDIT - Customer Owes Me","PENDING - I Owe Cash"])
        with col2:
            amount=st.number_input("Amount Rs. *", min_value=0.0); notes=st.text_input("Notes")
        if st.form_submit_button("Add Customer"):
            if name:
                real_c_type="CREDIT" if "CREDIT" in c_type else "PENDING"
                conn=sqlite3.connect('usman.db'); c=conn.cursor()
                c.execute('INSERT INTO customers (owner,name,type,amount,date,notes) VALUES (?,?,?,?,?,?)',(owner,name,real_c_type,amount,str(datetime.now().date()),notes))
                conn.commit(); conn.close(); st.success("Customer Added!"); st.balloons()
    if not df_cust.empty: st.dataframe(df_cust[['name','type','amount','date','notes']], use_container_width=True, hide_index=True)

elif "Cash Flow" in menu:
    st.subheader("💰 Cash IN / OUT")
    with st.form("cash_form"):
        col1,col2=st.columns(2)
        with col1: cash_type=st.selectbox("Type", ["CASH OUT - Expense","CASH IN - Income"]); amount=st.number_input("Amount Rs.", min_value=0.0)
        with col2: reason=st.text_input("Reason", placeholder="e.g. Rent, Bill")
        if st.form_submit_button("Save Cash Flow"):
            real_cash="OUT" if "OUT" in cash_type else "IN"
            conn=sqlite3.connect('usman.db'); c=conn.cursor()
            c.execute('INSERT INTO cash_flow (owner,type,amount,reason,date) VALUES (?,?,?,?,?)',(owner,real_cash,amount,reason,str(datetime.now().date())))
            conn.commit(); conn.close(); st.success(f"Cash {real_cash} Saved!"); st.balloons()
    if not df_cash.empty: st.dataframe(df_cash[['type','amount','reason','date']], use_container_width=True, hide_index=True)
