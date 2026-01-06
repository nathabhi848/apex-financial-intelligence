import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Apex Enterprise Terminal", layout="wide", page_icon="🔐")

# --- CUSTOM CSS FOR DARK MODE ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #334155; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .metric-container { background-color: #1e293b; color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #3b82f6; }
    .portfolio-matrix { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .net-score-box { background-color: #064e3b; color: #a7f3d0; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #10b981; margin-top: 10px; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; height: 50px; background-color: #3b82f6; color: white; border: none; }
    
    /* Input Box Styling */
    .stTextInput>div>div>input { background-color: #374151; color: white; border: 1px solid #4b5563; }
    h1, h2, h3, h4 { font-family: 'Helvetica Neue', sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'active_client' not in st.session_state: st.session_state.active_client = None
if 'active_ticker' not in st.session_state: st.session_state.active_ticker = "RELIANCE.NS"
if 'advisor_name' not in st.session_state: st.session_state.advisor_name = "Alex Mercer"
if 'email_draft' not in st.session_state: st.session_state.email_draft = ""

# --- MOCK DATABASE ---
CLIENT_DB = {
    "raj": {
        "name": "Raj Malhotra", 
        "risk": "Balanced Growth", 
        "holdings": {"Reliance": 30, "HDFC Bank": 25, "Gold Bonds": 25, "Nifty 50": 20}
    }
}

# --- HELPER: ROBUST DATA ---
def get_safe_data(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1d", interval="5m")
        if len(data) > 0: return data, "LIVE"
        data = yf.Ticker(ticker).history(period="5d", interval="15m")
        if len(data) > 0: return data, "5-Day"
        data = yf.Ticker(ticker).history(period="1mo", interval="1d")
        if len(data) > 0: return data, "Daily"
    except: pass
    return pd.DataFrame(), "Offline"

# ==========================================
# 🔐 THE LOGIN SCREEN
# ==========================================
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.title("🔒 Apex Secure Login")
        st.caption("Enterprise Financial Command Center v4.0")
        with st.form("login_form"):
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Access Terminal")
            if submitted:
                if user == "admin" and pw == "apex2025":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Access Denied")
    st.stop()

# ==========================================
# 📡 THE MAIN DASHBOARD
# ==========================================

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 👤 Advisor Profile")
    
    # 1. EDITABLE NAME (Restored)
    new_name = st.text_input("Advisor Name", value=st.session_state.advisor_name)
    if new_name != st.session_state.advisor_name:
        st.session_state.advisor_name = new_name
    
    st.markdown("---")
    
    st.header("1. Market Data")
    
    # 2. FIXED TICKER INPUT (Type & Enter Logic)
    def update_ticker():
        # This function runs immediately when you hit Enter
        st.session_state.active_ticker = st.session_state.ticker_input_val.upper().strip()

    st.text_input(
        "Ticker Symbol", 
        value=st.session_state.active_ticker, 
        key="ticker_input_val", 
        on_change=update_ticker 
    )
    
    st.markdown("---")
    st.header("2. Client Focus")
    client_query = st.text_input("Search Client", placeholder="e.g. Raj")
    if st.button("🔍 Analyze Portfolio"):
        found = None
        for key, val in CLIENT_DB.items():
            if key in client_query.lower():
                found = val
                break
        if found:
            st.session_state.active_client = found
            st.session_state.email_draft = ""
            st.success(f"Linked: {found['name']}")

# --- MAIN CONTENT ---
st.title("📡 Apex Financial Terminal")
st.markdown(f"**Advisor:** `{st.session_state.advisor_name}` | **Status:** `CONNECTED`")
st.markdown("---")

# 1. EMAIL TRIGGER
st.subheader("📩 Priority Inbox")
st.text_area("Latest Message", height=80, value="I'm seeing a drop in the market. Is my whole portfolio crashing? Should I sell everything?")

# 2. CHARTING ENGINE
st.markdown("---")
st.subheader(f"📊 Market Intelligence: {st.session_state.active_ticker}")

data, timeframe = get_safe_data(st.session_state.active_ticker)

if not data.empty:
    curr = data['Close'].iloc[-1]
    open_p = data['Open'].iloc[0]
    change = curr - open_p
    pct = (change / open_p) * 100 if open_p != 0 else 0
    color = "green" if change >= 0 else "red"
    
    c1, c2 = st.columns([3, 1])
    with c1:
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], increasing_line_color='#22c55e', decreasing_line_color='#ef4444')])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown(f"""
        <div class="metric-container">
            <h2>${curr:,.2f}</h2>
            <h3 style="color:{color}">{change:+.2f} ({pct:.2f}%)</h3>
            <p>Source: <strong>{timeframe}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        st.info("🤖 **AI Sentiment:** Volatility Detected.")
else:
    st.error(f"Could not load data for {st.session_state.active_ticker}. Check ticker symbol.")

# 3. TOTAL PORTFOLIO MATRIX
if st.session_state.active_client:
    st.markdown("---")
    client = st.session_state.active_client
    st.subheader(f"🎯 Total Portfolio Performance: {client['name']}")
    
    col_visuals, col_data, col_score = st.columns([1, 1, 1])
    
    # A. Visuals (Pie)
    with col_visuals:
        st.markdown("**Allocation Strategy**")
        labels = list(client['holdings'].keys())
        values = list(client['holdings'].values())
        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
        fig_pie.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # B. The Matrix (Data Proof)
    with col_data:
        st.markdown("**Real-Time Asset Performance**")
        st.markdown("""
        <div class="portfolio-matrix">
            <p>🔴 <strong>Reliance (30%):</strong> -1.8% (Impact: -0.54%)</p>
            <p>🟢 <strong>Gold Bonds (25%):</strong> +1.2% (Impact: +0.30%)</p>
            <p>🟢 <strong>HDFC Bank (25%):</strong> +0.8% (Impact: +0.20%)</p>
            <p>⚪ <strong>Nifty 50 (20%):</strong> 0.0% (Impact: 0.00%)</p>
        </div>
        """, unsafe_allow_html=True)

    # C. The Net Score (The Answer)
    with col_score:
        st.markdown("**Net Portfolio Impact**")
        st.markdown("""
        <div class="net-score-box">
            <h1>-0.04%</h1>
            <h4>STATUS: STABLE</h4>
            <p>Diversification Shield Active</p>
        </div>
        """, unsafe_allow_html=True)
        st.caption("The drop in Reliance is 95% offset by gains in Gold & HDFC.")

    # --- EMAIL LOGIC ---
    if st.button("⚡ Generate Compliance-Approved Email"):
        with st.spinner("Drafting..."):
            time.sleep(1.5)
            st.session_state.email_draft = f"""Subject: Portfolio Review - You are Safe

Hi {client['name']},

I reviewed your concern regarding the market drop. I ran a full performance check on your **ENTIRE** portfolio.

**The Reality:**
While {st.session_state.active_ticker} is down today, your **Gold Bonds** and **HDFC Bank** positions are UP.

**Net Result:**
Your total portfolio is virtually unchanged (Net Impact: -0.04%). The "Hedge" strategy is working exactly as intended.

**Recommendation:**
Do not sell. You are safe.

Best,
{st.session_state.advisor_name}"""

    if st.session_state.email_draft:
        st.text_area("Draft", value=st.session_state.email_draft, height=250)
        st.button("🚀 Send Reply")

else:
    st.info("👇 **Action Required:** Search for a Client to run the Impact Engine.")