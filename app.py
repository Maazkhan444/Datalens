import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from ydata_profiling import ProfileReport

from backend.core.loader import DataLoader
from backend.core.metadata import MetadataEngine
from backend.core.cleaner import DataCleaner
from backend.core.visualizer import DataVisualizer
from backend.ai.gemini_client import GeminiClient
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# ==========================================
# 🔑 CONFIGURATION
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "PASTE_YOUR_API_KEY_HERE")

# ==========================================
# 🚀 APP SETUP & CUSTOM CSS
# ==========================================
st.set_page_config(page_title="DataLens AI", page_icon="✨", layout="wide")

# Inject High-Quality CSS for the "Gemini" Look
st.markdown("""
    <style>
    /* 1. GLOBAL THEME (Dark & Sleek) */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* 2. SIDEBAR STYLING */
    [data-testid="stSidebar"] {
        background-color: #262730;
        border-right: 1px solid #333;
    }

    /* 3. CUSTOM CARDS (Glassmorphism) */
    div.css-1r6slb0, div.stMetric {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    label.css-1qg05tj { color: #b0b0b0; } /* Metric Labels */
    div[data-testid="stMetricValue"] { color: #4c8bf5; font-weight: 700; } /* Metric Values */

    /* 4. BUTTONS (Gradient Style) */
    div.stButton > button {
        background: linear-gradient(90deg, #4c8bf5 0%, #2b86d9 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        opacity: 0.9;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(76, 139, 245, 0.4);
    }
    
    /* 5. TABS */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid #333; }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #b0b0b0;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stTabs [data-baseweb="tab"]:hover { color: white; background-color: #333; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #4c8bf5; }
    
    /* 6. CHAT BUBBLES */
    .stChatMessage {
        background-color: #1E1E1E;
        border-radius: 10px;
        border: 1px solid #333;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

if 'df' not in st.session_state: st.session_state['df'] = None
if 'chat_history' not in st.session_state: st.session_state['chat_history'] = []
if 'auto_charts' not in st.session_state: st.session_state['auto_charts'] = []

# ==========================================
# 📂 SIDEBAR
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=60)
    st.title("DataLens AI")
    st.caption("✨ Intelligent Analytics")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📂 Upload Data Source", type=['csv', 'xlsx'])
    
    if uploaded_file and st.session_state['df'] is None:
        with st.spinner("🔮 DataGuru is analyzing..."):
            df, error = DataLoader.load_file(uploaded_file)
            if df is not None:
                cleaner = DataCleaner(df)
                df, _ = cleaner.auto_clean()
                st.session_state['df'] = df
                st.session_state['auto_charts'] = DataVisualizer.auto_generate_charts(df)
                st.rerun()
            else:
                st.error(error)

    if st.session_state['df'] is not None:
        if st.button("🧹 Clear & Reset", type="primary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.download_button(
            "💾 Export Cleaned CSV",
            st.session_state['df'].to_csv(index=False).encode('utf-8'),
            "datalens_clean.csv", "text/csv", use_container_width=True
        )

# ==========================================
# 🎯 DASHBOARD
# ==========================================
if st.session_state['df'] is not None:
    df = st.session_state['df']
    
    # KPI ROW
    st.markdown("### 📊 Dataset Overview")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Rows", f"{df.shape[0]:,}")
    k2.metric("Columns", df.shape[1])
    k3.metric("Missing Values", df.isnull().sum().sum())
    k4.metric("Status", "Cleaned & Ready")
    
    st.markdown("---")

    # TABS
    tab1, tab2, tab3 = st.tabs(["📈 Smart Analytics", "📑 Deep Report", "🧞 DataGuru Chat"])

    # --- TAB 1: VISUALS (GRID) ---
    with tab1:
        charts = st.session_state['auto_charts']
        if charts:
            # Heatmap Full Width
            for i, chart in enumerate(charts):
                if chart['type'] == 'wide':
                    st.plotly_chart(chart['fig'], use_container_width=True, key=f"wide_{i}")
            
            st.markdown("#### 🔎 Key Drivers & Trends")
            # 2-Column Grid for others
            cols = st.columns(2)
            small_charts = [c for c in charts if c['type'] != 'wide']
            
            for i, chart in enumerate(small_charts):
                with cols[i % 2]:
                    st.plotly_chart(chart['fig'], use_container_width=True, key=f"chart_{i}")
        else:
            st.info("No charts generated.")

    # --- TAB 2: REPORT (FIXED!) ---
    with tab2:
        if st.button("🚀 Generate PDF-Style Report"):
            with st.spinner("Generating Report..."):
                # FIX: Removed 'dark_mode=True' which caused the crash.
                # We set the theme via config property instead.
                try:
                    pr = ProfileReport(df, explorative=True)
                    pr.config.html.navbar_show = False # Clean look
                    
                    # Render
                    components.html(pr.to_html(), height=1000, scrolling=True)
                except Exception as e:
                    st.error(f"Report Error: {e}")

    # --- TAB 3: CHAT ---
    with tab3:
        for msg in st.session_state['chat_history']:
            with st.chat_message(msg["role"], avatar="🧞" if msg["role"] == "assistant" else "👤"):
                st.write(msg["content"])
                if msg.get("image"): st.plotly_chart(msg["image"], use_container_width=True)
        
        if prompt := st.chat_input("Ask DataGuru about trends, outliers, or predictions..."):
            st.session_state['chat_history'].append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)
            
            with st.spinner("DataGuru is thinking..."):
                if "PASTE" in GEMINI_API_KEY:
                    st.error("⚠️ Please configure API Key in app.py")
                else:
                    meta = MetadataEngine.generate_metadata(df)
                    client = GeminiClient(GEMINI_API_KEY)
                    resp = client.analyze(prompt, meta)
                    
                    fig = None
                    if resp.get("visualization"):
                        fig = DataVisualizer.create_chart(df, resp["visualization"])
                    
                    st.session_state['chat_history'].append({"role": "assistant", "content": resp.get("response"), "image": fig})
                    st.rerun()

else:
    # LANDING PAGE
    st.markdown("""
    <div style="text-align: center; margin-top: 80px;">
        <h1 style="background: -webkit-linear-gradient(45deg, #4c8bf5, #d92b86); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.5rem;">
            DataLens AI
        </h1>
        <p style="font-size: 1.2rem; color: #b0b0b0;">
            Your Intelligent Data Companion. Upload. Analyze. Chat.
        </p>
    </div>
    """, unsafe_allow_html=True)
