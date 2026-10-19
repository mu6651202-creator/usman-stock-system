import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="USMAN TECHNOLOGIES | Pro Stock Manager",
    page_icon="📦",
    layout="wide"
)

# --- PROFESSIONAL CSS + LIVE SPRINKLE EFFECT ---
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0f172a 0%, #1e3a8a 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 5px solid #1e3a8a;
    }
    .stButton>button {
        background: #1e3a8a;
        color: white;
        border-radius: 8px;
        height: 45px;
        width: 100%;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background: #0f172a;
        color: white;
    }
    /* LIVE SPRINKLE ANIMATION */
    .sprinkle {
        position: fixed;
        top: -10px;
        width: 10px;
        height: 10px;
        background: #ffcc00;
        border-radius: 50%;
        animation: fall 3s linear infinite;
        z-index: 9999;
    }
    @keyframes fall {
        0% { transform: translateY(0) rotate(0deg); opacity: 1; }
        100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
    }
</style>
""", unsafe_allow_html=True)

# --- SPRINKLE FUNCTION ---
def show_sprinkle():
    st.balloons()
    st.snow()
    sprinkle_html = ""
    colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"]
    for i in range(30):
        import random
        left = random.randint(0, 100)
        color = random.choice(colors)
        delay = random.random() * 2
        sprinkle_html += f'<div class="sprinkle" style="left:{left}%; background:{color}; animation-delay:{delay}s;"></div>'
    st.markdown(sprinkle_html, unsafe_allow_html=True)

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect('usman.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS stock 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  owner TEXT,
                  product_name TEXT,
                  quantity INTEGER,
                  price REAL,
                  date_added TEXT)''')
    conn.commit()
    conn.close()

def make_hash(p): return hashlib.sha256(str.encode(p)).hexdigest()
def check_hash(p, h): return make_hash(p) == h

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- LOGIN PAGE ---
def login_page():
    st.markdown('<div class="main-header"><h1>USMAN TECHNOLOGIES</h1><p>Professional Stock Management System</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        tab1, tab2 = st.tabs(["LOGIN", "CREATE ACCOUNT"])
        with tab1:
            st.subheader("Login to Your Account")
            u = st.text_input("Username", placeholder="Enter Username")
            p = st.text_input("Password", type="password", placeholder="Enter Password")
            if st.button("LOGIN NOW"):
                conn = sqlite3.connect('usman.db')
                c = conn.cursor()
                c.execute('SELECT password FROM users WHERE username = ?', (u,))
                data = c.fetchone()
                conn.close()
                if data and check_hash(p, data[0]):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Incorrect Username or Password")
        with tab2:
            st.subheader("Create New Account")
            nu = st.text_input("Choose Username", key="new_u")
            np = st.text_input("Choose Password", type="password", key="new_p")
            if st.button("CREATE ACCOUNT"):
                if nu and np:
                    conn = sqlite3.connect('usman.db')
                    c = conn.cursor()
                    try:
                        c.execute('INSERT INTO users (username, password) VALUES (?,?)', (nu, make_hash(np)))
                        conn.commit()
                        st.success("Account Created Successfully! Please Login Now.")
                        show_sprinkle()
                    except:
                        st.error("Username Already Exists!")
                    conn.close()
                else:
                    st.warning("Please Enter All Fields")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# --- MAIN PROFESSIONAL DASHBOARD ---
owner = st.session_state.username

# Sidebar
with st.sidebar:
    st.title(f"Welcome, {owner}")
    st.write("USMAN TECHNOLOGIES")
    st.divider()
    menu = st.radio("Navigation", ["Dashboard", "Add Stock", "View Stock"])
    st.divider()
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Header
st.markdown(f'<div class="main-header"><h2>📦 PRO STOCK MANAGER</h2><p>Owner: {owner} | Date: {datetime.now().strftime("%d-%m-%Y")}</p></div>', unsafe_allow_html=True)

conn = sqlite3.connect('usman.db')
df = pd.read_sql_query("SELECT * FROM stock WHERE owner=?", conn, params=(owner,))
conn.close()

# Dashboard Metrics
if menu == "Dashboard":
    c1, c2, c3 = st.columns(3)
    total_products = len(df)
    total_qty = df['quantity'].sum() if not df.empty else 0
    total_value = (df['quantity'] * df['price']).sum() if not df.empty else 0
    
    c1.metric("Total Products", total_products)
    c2.metric("Total Quantity", int(total_qty))
    c3.metric("Total Stock Value", f"Rs. {total_value:,.0f}")
    
    st.divider()
    st.subheader("Recent Stock Overview")
    if not df.empty:
        st.dataframe(df[['product_name','quantity','price','date_added']].rename(columns={'product_name':'Product','quantity':'Qty','price':'Price','date_added':'Date'}), use_container_width=True, hide_index=True)
    else:
        st.info("No Stock Found. Go to Add Stock.")

# Add Stock with Sprinkle
if menu == "Add Stock":
    st.subheader("➕ Add New Product")
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input("Product Name *", placeholder="e.g. iPhone 15")
            p_qty = st.number_input("Quantity *", min_value=1, step=1)
        with col2:
            p_price = st.number_input("Price Per Unit (Rs.) *", min_value=0.0, step=100.0)
            p_date = st.date_input("Date", value=datetime.now())
        
        submitted = st.form_submit_button("ADD TO STOCK")
        if submitted:
            if p_name:
                conn = sqlite3.connect('usman.db')
                c = conn.cursor()
                c.execute('INSERT INTO stock (owner, product_name, quantity, price, date_added) VALUES (?,?,?,?,?)',
                          (owner, p_name, p_qty, p_price, str(p_date)))
                conn.commit()
                conn.close()
                st.success(f"Product '{p_name}' Added Successfully!")
                show_sprinkle()
                st.toast("Live Sprinkle Effect Activated!", icon="🎉")
            else:
                st.error("Please Enter Product Name")

# View Stock
if menu == "View Stock":
    st.subheader("📋 Complete Stock List")
    search = st.text_input("🔍 Search Product", placeholder="Search by name...")
    
    conn = sqlite3.connect('usman.db')
    if search:
        df = pd.read_sql_query("SELECT id, product_name, quantity, price, date_added FROM stock WHERE owner=? AND product_name LIKE ?", conn, params=(owner, f"%{search}%"))
    else:
        df = pd.read_sql_query("SELECT id, product_name, quantity, price, date_added FROM stock WHERE owner=?", conn, params=(owner,))
    conn.close()
    
    if not df.empty:
        df['Total'] = df['quantity'] * df['price']
        df_display = df.rename(columns={'id':'ID','product_name':'Product','quantity':'Qty','price':'Price','date_added':'Date','Total':'Total Value'})
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        st.divider()
        col1, col2 = st.columns([2,1])
        with col2:
            st.write("**Manage Stock**")
            del_id = st.number_input("Enter ID to Delete", min_value=1, step=1)
            if st.button("🗑️ DELETE PRODUCT"):
                conn = sqlite3.connect('usman.db')
                c = conn.cursor()
                c.execute('DELETE FROM stock WHERE id=? AND owner=?', (del_id, owner))
                conn.commit()
                conn.close()
                st.warning("Product Deleted!")
                st.rerun()
    else:
        st.info("No Products Found.")
