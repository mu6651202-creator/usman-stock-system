import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime
import random

st.set_page_config(page_title="USMAN TECHNOLOGIES | Ultimate Stock", layout="wide", page_icon="📦")

# --- CSS + LIVE SPRINKLE ---
st.markdown("""
<style>
.main-header {background: linear-gradient(90deg, #0f172a, #1e3a8a); padding:20px; border-radius:15px; color:white; text-align:center; margin-bottom:20px;}
.stButton>button {background:#1e3a8a; color:white; border-radius:8px; height:45px; width:100%; font-weight:bold;}
.metric {background:white; padding:15px; border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.08); border-left:5px solid #1e3a8a;}
.sprinkle {position:fixed; top:-10px; width:10px; height:10px; border-radius:50%; animation: fall 3s linear infinite; z-index:9999;}
@keyframes fall {0%{transform:translateY(0) rotate(0deg); opacity:1;} 100%{transform:translateY(100vh) rotate(720deg); opacity:0;}}
</style>
""", unsafe_allow_html=True)

def show_sprinkle():
    st.balloons()
    st.snow()
    html=""
    colors=["#ff0000","#00ff00","#0000ff","#ffff00","#ff00ff","#00ffff","#ff8800"]
    for i in range(35):
        html+=f'<div class="sprinkle" style="left:{random.randint(0,100)}%; background:{random.choice(colors)}; animation-delay:{random.random()*2}s;"></div>'
    st.markdown(html, unsafe_allow_html=True)

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
    st.markdown('<div class="main-header"><h1>USMAN TECHNOLOGIES</h1><p>Ultimate Business & Stock Manager</p></div>', unsafe_allow_html=True)
    col1,col2,col3=st.columns([1,2,1])
    with col2:
        t1,t2=st.tabs(["LOGIN","CREATE ACCOUNT"])
        with t1:
            u=st.text_input("Username"); p=st.text_input("Password",type="password")
            if st.button("LOGIN"):
                conn=sqlite3.connect('usman.db'); c=conn.cursor()
                c.execute('SELECT password FROM users WHERE username=?',(u,)); d=c.fetchone(); conn.close()
                if d and check_hash(p,d[0]): st.session_state.logged_in=True; st.session_state.username=u; st.rerun()
                else: st.error("Incorrect Username or Password")
        with t2:
            nu=st.text_input("New Username",key="nu"); np=st.text_input("New Password",type="password",key="np")
            if st.button("CREATE ACCOUNT"):
                if nu and np:
                    conn=sqlite3.connect('usman.db'); c=conn.cursor()
                    try: c.execute('INSERT INTO users VALUES (?,?)',(nu,make_hash(np))); conn.commit(); st.success("Account Created! Login Now."); show_sprinkle()
                    except: st.error("Username Exists"); conn.close()
                    conn.close()

if not st.session_state.logged_in:
    login_page(); st.stop()

owner=st.session_state.username
with st.sidebar:
    st.title(f"Hi, {owner}"); st.write("USMAN TECHNOLOGIES"); st.divider()
    menu=st.radio("MENU", ["Dashboard + Graph","Stock IN / OUT","Current Stock","Credit & Pending","Cash Flow"])
    st.divider()
    if st.button("Logout"): st.session_state.logged_in=False; st.rerun()

st.markdown(f'<div class="main-header"><h2>Business Dashboard</h2><p>Owner: {owner} | {datetime.now().strftime("%d-%m-%Y")}</p></div>', unsafe_allow_html=True)

# --- LOAD DATA ---
conn=sqlite3.connect('usman.db')
df_tx=pd.read_sql_query("SELECT * FROM stock_tx WHERE owner=?",conn,params=(owner,))
df_cust=pd.read_sql_query("SELECT * FROM customers WHERE owner=?",conn,params=(owner,))
df_cash=pd.read_sql_query("SELECT * FROM cash_flow WHERE owner=?",conn,params=(owner,))
conn.close()

# --- DASHBOARD + GRAPH ---
if menu=="Dashboard + Graph":
    # Calculations
    total_in = df_tx[df_tx['tx_type']=='IN']['qty'].sum() if not df_tx.empty else 0
    total_out = df_tx[df_tx['tx_type']=='OUT']['qty'].sum() if not df_tx.empty else 0
    current_stock_qty = total_in - total_out
    total_profit = df_tx['profit'].sum() if not df_tx.empty else 0
    credit_total = df_cust[df_cust['type']=='CREDIT']['amount'].sum() if not df_cust.empty else 0
    pending_total = df_cust[df_cust['type']=='PENDING']['amount'].sum() if not df_cust.empty else 0

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Total Stock IN", int(total_in))
    c2.metric("Total Stock OUT", int(total_out))
    c3.metric("Current Stock Left", int(current_stock_qty))
    c4.metric("Total Profit/Loss", f"Rs. {total_profit:,.0f}", delta=f"{'Profit' if total_profit>=0 else 'Loss'}")

    c1,c2=st.columns(2)
    c1.metric("Credit Customers Amount", f"Rs. {credit_total:,.0f}")
    c2.metric("Cash Pending Amount", f"Rs. {pending_total:,.0f}")

    st.divider()
    st.subheader("📈 Full Business Graph - Profit & Loss (Goes Down If Loss)")
    if not df_tx.empty:
        # Create cumulative profit for graph
        df_tx_sorted = df_tx.sort_values('date')
        df_tx_sorted['cumulative_profit'] = df_tx_sorted['profit'].cumsum()
        df_tx_sorted['cumulative_stock'] = df_tx_sorted.apply(lambda x: x['qty'] if x['tx_type']=='IN' else -x['qty'], axis=1).cumsum()
        
        st.write("**Profit/Loss Graph (If loss, graph goes down)**")
        st.line_chart(df_tx_sorted[['cumulative_profit']], height=300)
        
        st.write("**Stock Quantity Graph (IN = Up, OUT = Down)**")
        st.line_chart(df_tx_sorted[['cumulative_stock']], height=300)
        
        st.write("**Detailed Transaction History**")
        st.dataframe(df_tx_sorted[['date','product','tx_type','qty','buy_price','sell_price','profit']], use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet. Add Stock IN/OUT first.")

# --- STOCK IN / OUT ---
elif menu=="Stock IN / OUT":
    st.subheader("Stock Movement - IN (Coming) / OUT (Going)")
    with st.form("tx_form"):
        col1,col2=st.columns(2)
        with col1:
            product=st.text_input("Product Name *", placeholder="e.g. Mobile Cover")
            tx_type=st.selectbox("Transaction Type *", ["IN - Stock Coming","OUT - Stock Going/Sale"])
            qty=st.number_input("Quantity *", min_value=1, step=1)
        with col2:
            buy_price=st.number_input("Buy Price (Cost) Rs.", min_value=0.0)
            sell_price=st.number_input("Sell Price (Sale) Rs.", min_value=0.0)
            date=st.date_input("Date", value=datetime.now())
        submit=st.form_submit_button("SAVE TRANSACTION")
        if submit:
            if product:
                real_type = "IN" if "IN" in tx_type else "OUT"
                profit = (sell_price - buy_price) * qty if real_type=="OUT" else 0
                conn=sqlite3.connect('usman.db'); c=conn.cursor()
                c.execute('INSERT INTO stock_tx (owner,product,tx_type,qty,buy_price,sell_price,profit,date) VALUES (?,?,?,?,?,?,?,?)',
                          (owner,product,real_type,qty,buy_price,sell_price,profit,str(date)))
                conn.commit(); conn.close()
                st.success(f"Stock {real_type} Recorded! Profit: Rs. {profit}"); show_sprinkle()
            else: st.error("Enter Product Name")

# --- CURRENT STOCK ---
elif menu=="Current Stock":
    st.subheader("📦 How Much Stock Is Left?")
    if not df_tx.empty:
        summary = df_tx.groupby('product').apply(lambda x: pd.Series({
            'Total IN': x[x['tx_type']=='IN']['qty'].sum(),
            'Total OUT': x[x['tx_type']=='OUT']['qty'].sum(),
            'Current Left': x[x['tx_type']=='IN']['qty'].sum() - x[x['tx_type']=='OUT']['qty'].sum(),
            'Total Profit': x['profit'].sum()
        })).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.bar_chart(summary.set_index('product')['Current Left'])
    else: st.info("No stock data.")

# --- CREDIT & PENDING ---
elif menu=="Credit & Pending":
    st.subheader("People With Credit & Pending Cash")
    with st.form("cust_form"):
        col1,col2=st.columns(2)
        with col1:
            name=st.text_input("Customer Name *")
            c_type=st.selectbox("Type *", ["CREDIT - He has to pay me","PENDING - My cash is pending with him"])
        with col2:
            amount=st.number_input("Amount Rs. *", min_value=0.0)
            notes=st.text_input("Notes", placeholder="e.g. Mobile repair")
        if st.form_submit_button("ADD CUSTOMER"):
            if name and amount:
                real_c_type = "CREDIT" if "CREDIT" in c_type else "PENDING"
                conn=sqlite3.connect('usman.db'); c=conn.cursor()
                c.execute('INSERT INTO customers (owner,name,type,amount,date,notes) VALUES (?,?,?,?,?,?)',
                          (owner,name,real_c_type,amount,str(datetime.now().date()),notes))
                conn.commit(); conn.close()
                st.success("Customer Added!"); show_sprinkle()
            else: st.error("Enter Name & Amount")
    
    st.divider()
    if not df_cust.empty:
        st.dataframe(df_cust[['name','type','amount','date','notes']].rename(columns={'name':'Customer','type':'Type','amount':'Amount'}), use_container_width=True, hide_index=True)
        # Delete
        del_id=st.number_input("Enter ID to Delete Customer", min_value=1, step=1)
        if st.button("Delete Customer"):
            conn=sqlite3.connect('usman.db'); c=conn.cursor()
            c.execute('DELETE FROM customers WHERE id=? AND owner=?',(del_id,owner)); conn.commit(); conn.close(); st.rerun()
    else: st.info("No credit/pending customers yet.")

# --- CASH FLOW ---
elif menu=="Cash Flow":
    st.subheader("Cash Going & Coming")
    with st.form("cash_form"):
        col1,col2=st.columns(2)
        with col1:
            cash_type=st.selectbox("Cash Type", ["CASH OUT - Cash Going","CASH IN - Cash Coming"])
            amount=st.number_input("Amount Rs.", min_value=0.0)
        with col2:
            reason=st.text_input("Reason", placeholder="e.g. Shop Rent, Petrol")
        if st.form_submit_button("SAVE CASH FLOW"):
            real_cash = "OUT" if "OUT" in cash_type else "IN"
            conn=sqlite3.connect('usman.db'); c=conn.cursor()
            c.execute('INSERT INTO cash_flow (owner,type,amount,reason,date) VALUES (?,?,?,?,?)',
                      (owner,real_cash,amount,reason,str(datetime.now().date())))
            conn.commit(); conn.close()
            st.success(f"Cash {real_cash} Recorded!"); show_sprinkle()
    
    if not df_cash.empty:
        st.dataframe(df_cash[['type','amount','reason','date']], use_container_width=True, hide_index=True)
        total_cash_in = df_cash[df_cash['type']=='IN']['amount'].sum()
        total_cash_out = df_cash[df_cash['type']=='OUT']['amount'].sum()
        st.metric("Net Cash", f"Rs. {total_cash_in - total_cash_out:,.0f}")
    else: st.info("No cash flow records.")
