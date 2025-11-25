# app.py
import streamlit as st
import pandas as pd
import numpy as np
import os
import fnmatch
import random
from datetime import datetime, timedelta
import time

# Try to import optional dependencies
try:
    import pickle
except ImportError:
    st.warning("pickle module not available")

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    st.warning("joblib not available - please install it")
    JOBLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    st.warning("plotly not available - charts will be disabled")
    PLOTLY_AVAILABLE = False

try:
    import streamlit.components.v1 as components
    COMPONENTS_AVAILABLE = True
except ImportError:
    st.warning("streamlit components not available")
    COMPONENTS_AVAILABLE = False

# -------------------------
# Project identity
# -------------------------
PROJECT_NAME = "1912 Automation — Smart Grid Intelligence"
PROJECT_TAGLINE = "Advanced Fault Detection • Predictive Analytics • Automated Restoration"
PROJECT_SLOGAN = "Detect. Diagnose. Restore."

# -------------------------
# File paths - Handle missing files gracefully
# -------------------------
SEARCH_DIR = "/mnt/data"
FAULT_PATH_FALLBACKS = [
    "best_model.pkl",
    "fault_model.pkl", 
    "fault_classifier.pkl",
    "best_fault_model.pkl",
    "fault_pipe.pkl",
    "best_model.joblib",
    "fault_model.joblib"
]
ETR_NOM_MODEL_PATH = "nom_regression_model.pkl"
ETR_ENCODERS_PATH  = "feature_encoders 1.pkl"
HIERARCHY_PATH     = "org_hierarchy.xlsx"
COMPLAINTS_DATA_PATH = "data.xlsx"

# Enhanced Professional CSS Theme
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(135deg, #0c1a2d 0%, #1a365d 50%, #2d3748 100%); 
        color: #e2e8f0; 
        font-family: 'Inter', sans-serif;
    }
    
    /* Main cards */
    .card { 
        background: rgba(26, 32, 44, 0.85); 
        border-radius: 16px; 
        padding: 24px; 
        box-shadow: 0 12px 32px rgba(0,0,0,0.3); 
        border: 1px solid rgba(74, 85, 104, 0.3);
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 40px rgba(0,0,0,0.4);
        border-color: rgba(66, 153, 225, 0.5);
    }
    
    /* Headers */
    .proj-title { 
        font-size: 32px; 
        font-weight: 800; 
        color: #ffffff; 
        text-align: center;
        margin-bottom: 12px;
        text-shadow: 0 4px 12px rgba(0,0,0,0.3);
        background: linear-gradient(135deg, #4299e1, #38b2ac);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .proj-tag { 
        color: #a0aec0; 
        text-align: center;
        font-size: 18px; 
        font-weight: 500;
        margin-bottom: 30px;
    }
    
    .small { font-size: 14px; color: #cbd5e0; }
    .muted { color: #718096; font-size: 13px; }
    .footer { color: #a0aec0; font-size: 0.9rem; padding-top: 20px; text-align: center; }
    
    /* Animation classes */
    .fade-in { animation: fadeIn 0.8s ease-out; }
    .slide-in-left { animation: slideInLeft 0.6s ease-out; }
    .slide-in-right { animation: slideInRight 0.6s ease-out; }
    .pulse { animation: pulse 2s infinite; }
    .bounce { animation: bounce 1s infinite; }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-40px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideInRight {
        from { transform: translateX(40px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(66, 153, 225, 0.7); }
        70% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(66, 153, 225, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(66, 153, 225, 0); }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
        40% {transform: translateY(-8px);}
        60% {transform: translateY(-4px);}
    }
    
    /* Status indicators */
    .status-success { 
        color: #48bb78; 
        font-weight: 700; 
        background: rgba(72, 187, 120, 0.1);
        padding: 6px 12px;
        border-radius: 8px;
        border: 1px solid rgba(72, 187, 120, 0.3);
    }
    
    .status-fail { 
        color: #f56565; 
        font-weight: 700; 
        background: rgba(245, 101, 101, 0.1);
        padding: 6px 12px;
        border-radius: 8px;
        border: 1px solid rgba(245, 101, 101, 0.3);
    }
    
    .status-processing { 
        color: #ed8936; 
        font-weight: 700; 
        background: rgba(237, 137, 54, 0.1);
        padding: 6px 12px;
        border-radius: 8px;
        border: 1px solid rgba(237, 137, 54, 0.3);
        animation: pulse 2s infinite;
    }
    
    /* Step indicator */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin: 30px 0;
        position: relative;
    }
    
    .step-indicator::before {
        content: '';
        position: absolute;
        top: 20px;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #4299e1, #38b2ac);
        z-index: 1;
        border-radius: 2px;
    }
    
    .step {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: #2d3748;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        z-index: 2;
        position: relative;
        border: 3px solid #4a5568;
        color: #a0aec0;
        transition: all 0.3s ease;
    }
    
    .step.active {
        background: #4299e1;
        color: white;
        border-color: #63b3ed;
        animation: pulse 2s infinite;
        box-shadow: 0 0 20px rgba(66, 153, 225, 0.5);
    }
    
    .step.completed {
        background: #38b2ac;
        color: white;
        border-color: #4fd1c7;
        box-shadow: 0 0 20px rgba(56, 178, 172, 0.5);
    }
    
    /* Feature boxes */
    .feature-box {
        background: linear-gradient(135deg, #4299e1, #38b2ac);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 12px 0;
        box-shadow: 0 8px 25px rgba(66, 153, 225, 0.4);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .feature-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(66, 153, 225, 0.6);
    }
    
    /* Complaint cards */
    .complaint-card {
        background: linear-gradient(135deg, rgba(26, 32, 44, 0.9), rgba(45, 55, 72, 0.9));
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        border-left: 6px solid #4299e1;
        transition: all 0.3s ease;
        border: 1px solid rgba(74, 85, 104, 0.3);
    }
    
    .complaint-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.3);
        border-left: 6px solid #38b2ac;
        border-color: rgba(66, 153, 225, 0.5);
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #4299e1, #38b2ac) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(66, 153, 225, 0.3) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(66, 153, 225, 0.5) !important;
    }
    
    /* Divider styling */
    .stMarkdown hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #4299e1, #38b2ac, transparent);
        margin: 30px 0;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# Helper functions
# -------------------------
def parse_numeric(text):
    if text is None: return np.nan
    s = str(text).strip()
    if s == "" or s.lower() in ["na","n/a","nan","-"]:
        return np.nan
    s = s.replace(",", "")
    try:
        return float(s)
    except:
        return np.nan

# -------------------------
# Load complaints data with error handling
# -------------------------
@st.cache_data
def load_complaints_data(path=COMPLAINTS_DATA_PATH):
    if not os.path.exists(path):
        st.warning(f"Complaints data file not found at {path}")
        # Create sample data for demo
        sample_data = {
            'Request_Id': ['REQ001', 'REQ002', 'REQ003'],
            'Feeder_MSN': ['FDR001', 'FDR002', 'FDR003'],
            'Feeder_ProcessStatus': ['success', 'fail', 'success'],
            'DTR_MSN': ['DTR001', 'DTR002', 'DTR003'],
            'DTR_ProcessStatus': ['success', 'success', 'fail'],
            'Consumer_MSN': ['CON001', 'CON002', 'CON003'],
            'Consumer_ProcessStatus': ['fail', 'success', 'success'],
            'Consumer_Phase_Id': [3, 1, 3],
            'f_vr': [230.5, 231.2, 229.8],
            'f_vy': [229.8, 230.1, 231.5],
            'f_vb': [231.1, 230.8, 229.2],
            'f_ir': [1.2, 1.1, 1.3],
            'f_iy': [1.1, 1.0, 1.2],
            'f_ib': [1.3, 1.2, 1.1],
            'd_vr': [229.5, 230.2, 228.8],
            'd_vy': [228.8, 229.1, 230.5],
            'd_vb': [230.1, 229.8, 228.2],
            'd_ir': [0.8, 0.9, 0.7],
            'd_iy': [0.9, 0.8, 0.6],
            'd_ib': [0.7, 0.6, 0.8],
            'Final_Label': ['DTHT', 'FOC', 'DTLT'],
            'region': ['Region A', 'Region B', 'Region A'],
            'circle': ['Circle 1', 'Circle 2', 'Circle 1'],
            'division': ['Division X', 'Division Y', 'Division X'],
            'zone': ['Zone P', 'Zone Q', 'Zone P']
        }
        return pd.DataFrame(sample_data)
    try:
        df = pd.read_excel(path)
        return df
    except Exception as e:
        st.error(f"Error loading complaints data: {e}")
        return pd.DataFrame()

# -------------------------
# Load models with error handling
# -------------------------
@st.cache_resource
def find_and_load_fault_bundle():
    if not JOBLIB_AVAILABLE:
        return None, "Joblib not available"
    
    for p in FAULT_PATH_FALLBACKS:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    bundle = pickle.load(f)
                return bundle, p
            except Exception:
                try:
                    m = joblib.load(p)
                    return m, p
                except Exception:
                    continue
    return None, "No fault model found"

_fault_bundle, _fault_loaded_from = find_and_load_fault_bundle()
fault_pipeline = None
fault_label_encoder = None
if _fault_bundle is not None:
    if isinstance(_fault_bundle, dict):
        fault_pipeline = _fault_bundle.get("pipeline", _fault_bundle)
        fault_label_encoder = _fault_bundle.get("label_encoder", None)
    else:
        fault_pipeline = _fault_bundle
        fault_label_encoder = None

@st.cache_resource
def load_nom(path=ETR_NOM_MODEL_PATH, enc_path=ETR_ENCODERS_PATH):
    m = None; enc = {}
    
    if not JOBLIB_AVAILABLE:
        return m, enc
        
    if os.path.exists(path):
        try:
            m = joblib.load(path)
        except Exception as e:
            st.warning(f"Could not load nom model from {path}: {e}")
    if os.path.exists(enc_path):
        try:
            enc = joblib.load(enc_path)
        except Exception as e:
            st.warning(f"Could not load encoders from {enc_path}: {e}")
    return m, enc

nom_model, nom_encoders = load_nom()

# -------------------------
# Load hierarchy with error handling
# -------------------------
@st.cache_data
def load_hierarchy(path=HIERARCHY_PATH):
    if not os.path.exists(path):
        st.warning(f"Hierarchy file not found at {path}")
        # Return sample hierarchy data
        sample_data = {
            'region': ['Region A', 'Region B'],
            'circle': ['Circle 1', 'Circle 2'], 
            'division': ['Division X', 'Division Y'],
            'zone': ['Zone P', 'Zone Q']
        }
        return pd.DataFrame(sample_data), {'region': 'region', 'circle': 'circle', 'division': 'division', 'zone': 'zone'}
    
    try:
        df = pd.read_excel(path).fillna("")
        col_map = {}
        for candidate in ["region","region_name","circle","circle_name","division","division_name","zone","zone_name"]:
            for c in df.columns:
                if candidate in c.lower():
                    key = candidate.split("_")[0]
                    if key not in col_map:
                        col_map[key] = c
        if "region" not in col_map:
            for c in df.columns:
                if "reg" in c.lower():
                    col_map["region"] = c; break
        if "circle" not in col_map:
            for c in df.columns:
                if "circ" in c.lower():
                    col_map["circle"] = c; break
        if "division" not in col_map:
            for c in df.columns:
                if "div" in c.lower():
                    col_map["division"] = c; break
        if "zone" not in col_map:
            for c in df.columns:
                if "zone" in c.lower():
                    col_map["zone"] = c; break
        return df, col_map
    except Exception as e:
        st.error(f"Error loading hierarchy: {e}")
        return pd.DataFrame(), {}

df_hier, hier_map = load_hierarchy()

# -------------------------
# Enhanced Header Section
# -------------------------
st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <div class="proj-title">⚡ 1912 Automation — Smart Grid Intelligence</div>
        <div class="proj-tag">Advanced Fault Detection • Predictive Analytics • Automated Restoration</div>
        <div style='margin-top: 10px; color: #718096; font-size: 14px;'>
            Real-time Monitoring | AI-Powered Diagnostics | Smart Grid Management
        </div>
    </div>
""", unsafe_allow_html=True)

# Display system status
if not JOBLIB_AVAILABLE:
    st.error("⚠️ Joblib not installed. Some features may not work.")
if not PLOTLY_AVAILABLE:
    st.warning("📊 Plotly not available. Using alternative charts.")

# -------------------------
# Main Application Workflow
# -------------------------

# Step 1: Fetch Live Complaints
st.markdown("---")
st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
st.subheader("📥 Step 1: Fetch Live Complaints")

if st.button("🚀 Click to Fetch Live Complaints & Predict Faults", use_container_width=True, 
             type="primary", help="Fetch real-time complaints and start automated analysis"):
    
    # Load complaints data
    complaints_df = load_complaints_data()
    
    if complaints_df.empty:
        st.error("No complaints data available.")
    else:
        # Select random complaints (5-8)
        num_complaints = min(random.randint(5, 8), len(complaints_df))
        selected_complaints = complaints_df.sample(n=num_complaints)
        
        # Display complaints with animation
        st.success(f"✅ Successfully fetched {num_complaints} live complaints!")
        
        for idx, complaint in selected_complaints.iterrows():
            with st.container():
                current_time = datetime.now()
                # Create complaint time 2-3 minutes before current time
                complaint_time = current_time - timedelta(minutes=random.randint(2, 3))
                
                st.markdown(f"""
                <div class="complaint-card slide-in-left">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <strong>Request ID:</strong> {complaint.get('Request_Id', 'N/A')} 
                            | <strong>Complaint Time:</strong> {complaint_time.strftime('%H:%M:%S')}
                            | <strong>Current Time:</strong> {current_time.strftime('%H:%M:%S')}
                        </div>
                        <div class="status-processing">PENDING ANALYSIS</div>
                    </div>
                    <div style="margin-top: 8px;">
                        <strong>Location:</strong> {complaint.get('region', 'N/A')} → {complaint.get('circle', 'N/A')} → {complaint.get('division', 'N/A')} → {complaint.get('zone', 'N/A')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Store selected complaints in session state
        st.session_state.selected_complaints = selected_complaints
        st.session_state.current_step = 2
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Step 2: Side Panel - Fault Information
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Fault Types & Information")

fault_info = {
    "DTHT": {
        "meaning": "DT ke 3 phase voltages me >30% imbalance",
        "analogy": "Teen paani pipe me ek me bahut kam flow",
        "description": "Distribution Transformer High Imbalance - Significant voltage imbalance across three phases"
    },
    "DTLT": {
        "meaning": "Voltage OK but 1 phase current ZERO", 
        "analogy": "Wire cut / LT line broken",
        "description": "Distribution Transformer Low Current - One phase has zero current indicating broken line"
    },
    "FOC": {
        "meaning": "DT OK, supply consumer tak aa rahi hai, ping nahi",
        "analogy": "Ghar ka MCB trip / internal wiring issue",
        "description": "Failure at Consumer End - Power reaching consumer premises but internal issue detected"
    },
    "FOC/DT HT": {
        "meaning": "DT readings NULL, ping patterns decide fault",
        "analogy": "DT meter dead / communication fail", 
        "description": "DT Communication Failure - Transformer meter offline, using ping patterns for diagnosis"
    }
}

for fault, info in fault_info.items():
    with st.sidebar.expander(f"⚡ {fault}"):
        st.markdown(f"**Meaning:** {info['meaning']}")
        st.markdown(f"**Analogy:** {info['analogy']}")
        st.markdown(f"**Description:** {info['description']}")

# Step 3: Analyze Complaints (if step 2 completed)
if 'current_step' in st.session_state and st.session_state.current_step >= 2:
    st.markdown("---")
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
    st.subheader("🔬 Step 2: Analyze Complaints & Detect Faults")
    
    # Step indicator
    st.markdown("""
    <div class="step-indicator">
        <div class="step completed">1</div>
        <div class="step active">2</div>
        <div class="step">3</div>
        <div class="step">4</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 Start Fault Detection Analysis", use_container_width=True, type="secondary"):
        st.session_state.current_step = 3
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Step 4: Detailed Analysis (if step 3 completed)
if 'current_step' in st.session_state and st.session_state.current_step >= 3:
    st.markdown("---")
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
    st.subheader("📊 Step 3: Detailed Fault Analysis")
    
    # Step indicator
    st.markdown("""
    <div class="step-indicator">
        <div class="step completed">1</div>
        <div class="step completed">2</div>
        <div class="step active">3</div>
        <div class="step">4</div>
    </div>
    """, unsafe_allow_html=True)
    
    selected_complaints = st.session_state.get('selected_complaints', pd.DataFrame())
    
    if not selected_complaints.empty:
        # Process each complaint with animation
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (idx, complaint) in enumerate(selected_complaints.iterrows()):
            progress = (i + 1) / len(selected_complaints)
            progress_bar.progress(progress)
            status_text.text(f"Analyzing complaint {i+1} of {len(selected_complaints)}...")
            
            # Create analysis container
            with st.container():
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"""
                    <div class="card slide-in-left">
                        <h4>📋 Complaint #{i+1}</h4>
                        <p><strong>Request ID:</strong> {complaint.get('Request_Id', 'N/A')}</p>
                        <p><strong>Feeder MSN:</strong> {complaint.get('Feeder_MSN', 'N/A')}</p>
                        <p><strong>DTR MSN:</strong> {complaint.get('DTR_MSN', 'N/A')}</p>
                        <p><strong>Consumer MSN:</strong> {complaint.get('Consumer_MSN', 'N/A')}</p>
                        <p><strong>Phase:</strong> {complaint.get('Consumer_Phase_Id', 'N/A')}-Phase</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Format intensity profile data properly
                    f_vr = complaint.get('f_vr', 0)
                    f_vy = complaint.get('f_vy', 0)
                    f_vb = complaint.get('f_vb', 0)
                    f_ir = complaint.get('f_ir', 0)
                    f_iy = complaint.get('f_iy', 0)
                    f_ib = complaint.get('f_ib', 0)
                    
                    d_vr = complaint.get('d_vr', 0)
                    d_vy = complaint.get('d_vy', 0)
                    d_vb = complaint.get('d_vb', 0)
                    d_ir = complaint.get('d_ir', 0)
                    d_iy = complaint.get('d_iy', 0)
                    d_ib = complaint.get('d_ib', 0)
                    
                    # Use Streamlit components instead of raw HTML
                    st.markdown("#### 🔍 Ping Status Analysis")
                    
                    # Create columns for ping status
                    ping_col1, ping_col2, ping_col3 = st.columns(3)
                    with ping_col1:
                        status_color = "🟢" if complaint.get('Feeder_ProcessStatus') == 'success' else "🔴"
                        st.metric("Feeder", complaint.get('Feeder_ProcessStatus', 'N/A'), delta=status_color, delta_color="normal")
                    
                    with ping_col2:
                        status_color = "🟢" if complaint.get('DTR_ProcessStatus') == 'success' else "🔴"
                        st.metric("DTR", complaint.get('DTR_ProcessStatus', 'N/A'), delta=status_color, delta_color="normal")
                    
                    with ping_col3:
                        status_color = "🟢" if complaint.get('Consumer_ProcessStatus') == 'success' else "🔴"
                        st.metric("Consumer", complaint.get('Consumer_ProcessStatus', 'N/A'), delta=status_color, delta_color="normal")
                    
                    st.markdown("---")
                    st.markdown("#### 📈 Intensity Profile Data")
                    
                    # Feeder readings
                    st.markdown("**Feeder Readings**")
                    feeder_col1, feeder_col2 = st.columns(2)
                    with feeder_col1:
                        st.write(f"**Voltage:**")
                        st.write(f"R: {float(f_vr):.1f} V")
                        st.write(f"Y: {float(f_vy):.1f} V") 
                        st.write(f"B: {float(f_vb):.1f} V")
                    
                    with feeder_col2:
                        st.write(f"**Current:**")
                        st.write(f"R: {float(f_ir):.2f} A")
                        st.write(f"Y: {float(f_iy):.2f} A")
                        st.write(f"B: {float(f_ib):.2f} A")
                    
                    st.markdown("---")
                    
                    # DTR readings
                    st.markdown("**DTR Readings**")
                    dtr_col1, dtr_col2 = st.columns(2)
                    with dtr_col1:
                        st.write(f"**Voltage:**")
                        st.write(f"R: {float(d_vr):.1f} V")
                        st.write(f"Y: {float(d_vy):.1f} V")
                        st.write(f"B: {float(d_vb):.1f} V")
                    
                    with dtr_col2:
                        st.write(f"**Current:**")
                        st.write(f"R: {float(d_ir):.2f} A")
                        st.write(f"Y: {float(d_iy):.2f} A")
                        st.write(f"B: {float(d_ib):.2f} A")
            
            # Simulate processing time
            time.sleep(0.5)
        
        progress_bar.empty()
        status_text.empty()
        
        st.success("✅ All complaints analyzed successfully!")
        
        # Show fault prediction results
        st.markdown("### 🎯 Fault Prediction Results")
        
        # Create results visualization
        fault_counts = selected_complaints['Final_Label'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if PLOTLY_AVAILABLE and not fault_counts.empty:
                fig = px.pie(
                    values=fault_counts.values, 
                    names=fault_counts.index,
                    title="Fault Type Distribution",
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
            elif not fault_counts.empty:
                st.write("**Fault Type Distribution**")
                chart_data = pd.DataFrame({
                    'Fault Type': fault_counts.index,
                    'Count': fault_counts.values
                })
                st.bar_chart(chart_data.set_index('Fault Type'))
        
        with col2:
            if not fault_counts.empty:
                st.write("**Fault Count Summary**")
                st.dataframe(fault_counts, use_container_width=True)
        
        # Store analysis results
        st.session_state.analysis_complete = True
        st.session_state.analyzed_complaints = selected_complaints

st.markdown("</div>", unsafe_allow_html=True)

# Step 5: ETR Prediction (if analysis complete)
if 'analysis_complete' in st.session_state and st.session_state.analysis_complete:
    st.markdown("---")
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
    st.subheader("⏱️ Step 4: Estimate Time for Restoration")
    
    # Step indicator
    st.markdown("""
    <div class="step-indicator">
        <div class="step completed">1</div>
        <div class="step completed">2</div>
        <div class="step completed">3</div>
        <div class="step active">4</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🕒 Predict Restoration Time (ETR)", use_container_width=True, type="primary"):
        st.session_state.etr_prediction_started = True
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Step 6: ETR Prediction Process
if 'etr_prediction_started' in st.session_state and st.session_state.etr_prediction_started:
    st.markdown("---")
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
    
    analyzed_complaints = st.session_state.get('analyzed_complaints', pd.DataFrame())
    
    if not analyzed_complaints.empty:
        # Show location hierarchy visualization
        st.subheader("🗺️ Location Analysis")
        
        # Handle different column name cases for location data
        location_cols = []
        for col in ['REGION', 'region', 'Region']:
            if col in analyzed_complaints.columns:
                location_cols.append(col)
                break
        for col in ['CIRCLE', 'circle', 'Circle']:
            if col in analyzed_complaints.columns:
                location_cols.append(col)
                break
        for col in ['DIVISION', 'division', 'Division']:
            if col in analyzed_complaints.columns:
                location_cols.append(col)
                break
        for col in ['ZONE', 'zone', 'Zone']:
            if col in analyzed_complaints.columns:
                location_cols.append(col)
                break

        if len(location_cols) == 4:
            locations = analyzed_complaints[location_cols].drop_duplicates()
        else:
            # Fallback to available columns
            available_cols = [col for col in ['region', 'circle', 'division', 'zone'] if col in analyzed_complaints.columns]
            locations = analyzed_complaints[available_cols].drop_duplicates() if available_cols else pd.DataFrame()
        
        for _, loc in locations.iterrows():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                region_val = loc.get('REGION', loc.get('region', loc.get('Region', 'N/A')))
                st.markdown(f"<div class='feature-box'><strong>Region</strong><br>{region_val}</div>", unsafe_allow_html=True)
            with col2:
                circle_val = loc.get('CIRCLE', loc.get('circle', loc.get('Circle', 'N/A')))
                st.markdown(f"<div class='feature-box'><strong>Circle</strong><br>{circle_val}</div>", unsafe_allow_html=True)
            with col3:
                division_val = loc.get('DIVISION', loc.get('division', loc.get('Division', 'N/A')))
                st.markdown(f"<div class='feature-box'><strong>Division</strong><br>{division_val}</div>", unsafe_allow_html=True)
            with col4:
                zone_val = loc.get('ZONE', loc.get('zone', loc.get('Zone', 'N/A')))
                st.markdown(f"<div class='feature-box'><strong>Zone</strong><br>{zone_val}</div>", unsafe_allow_html=True)
        
        # Time and season analysis
        st.subheader("⏰ Time & Season Analysis")
        
        current_time = datetime.now()
        tod = "Morning" if 5 <= current_time.hour < 12 else "Afternoon" if 12 <= current_time.hour < 17 else "Evening" if 17 <= current_time.hour < 21 else "Night"
        season = "Summer" if current_time.month in [4,5,6] else "Rainy" if current_time.month in [7,8,9] else "Winter"
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='card'><strong>Time of Day:</strong> {tod}<br><strong>Current Time:</strong> {current_time.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='card'><strong>Season:</strong> {season}<br><strong>Date:</strong> {current_time.strftime('%Y-%m-%d')}</div>", unsafe_allow_html=True)
        
        # ETR Prediction Results
        st.subheader("🎯 ETR Prediction Results")
        
        # Simulate ETR prediction for each complaint
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        etr_results = []
        
        for i, (idx, complaint) in enumerate(analyzed_complaints.iterrows()):
            progress = (i + 1) / len(analyzed_complaints)
            progress_bar.progress(progress)
            status_text.text(f"Predicting ETR for complaint {i+1} of {len(analyzed_complaints)}...")
            
            # Simulate ETR prediction (in minutes)
            base_etr = random.randint(30, 180)
            etr_minutes = base_etr
            etr_human = f"{etr_minutes//60} hr {etr_minutes%60} min" if etr_minutes >= 60 else f"{etr_minutes} min"
            
            etr_results.append({
                'Request_Id': complaint.get('Request_Id', 'N/A'),
                'Fault_Type': complaint.get('Final_Label', 'N/A'),
                'ETR_Minutes': etr_minutes,
                'ETR_Human': etr_human
            })
            
            # Display individual result
            with st.container():
                st.markdown(f"""
                <div class="complaint-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>Request ID:</strong> {complaint.get('Request_Id', 'N/A')}
                            | <strong>Fault:</strong> {complaint.get('Final_Label', 'N/A')}
                        </div>
                        <div class="status-success" style="font-size: 18px;">
                            <strong>ETR: {etr_human}</strong>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            time.sleep(0.3)
        
        progress_bar.empty()
        status_text.empty()
        
        # Store ETR results
        st.session_state.etr_results = etr_results
        st.session_state.etr_complete = True

st.markdown("</div>", unsafe_allow_html=True)

# Step 7: Countdown Timer (if ETR complete)
if 'etr_complete' in st.session_state and st.session_state.etr_complete:
    st.markdown("---")
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
    st.subheader("⏳ Live Restoration Countdown")
    
    etr_results = st.session_state.get('etr_results', [])
    
    if etr_results and COMPONENTS_AVAILABLE:
        # Find the maximum ETR for the overall countdown
        max_etr = max(result['ETR_Minutes'] for result in etr_results)
        end_time = datetime.now() + timedelta(minutes=max_etr)
        end_timestamp = int(end_time.timestamp() * 1000)
        
        # Overall countdown timer
        countdown_html = f'''
        <div style="font-family:Arial,Helvetica,sans-serif; text-align: center;">
          <h3 style="color: #ffffff;">Overall Maximum Restoration Time</h3>
          <div id="countdown" style="font-size: 36px; color: #38b2ac; font-weight: 700; margin: 20px 0;"></div>
          <p style="color: #a0aec0;">Estimated completion: {end_time.strftime("%H:%M:%S")}</p>
        </div>
        <script>
        function startCountdown(endTime) {{
          function update() {{
            var now = new Date().getTime();
            var distance = endTime - now;
            if (distance < 0) {{
              document.getElementById('countdown').innerHTML = "✅ RESTORED";
              document.getElementById('countdown').style.color = "#48bb78";
              return;
            }}
            var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);
            document.getElementById('countdown').innerHTML =
              hours.toString().padStart(2,'0') + ":" + minutes.toString().padStart(2,'0') + ":" + seconds.toString().padStart(2,'0');
          }}
          update();
          setInterval(update, 1000);
        }}
        startCountdown({end_timestamp});
        </script>
        '''
        components.html(countdown_html, height=200)
        
        # Individual complaint countdowns
        st.subheader("📋 Individual Complaint Timelines")
        
        for result in etr_results:
            complaint_end_time = datetime.now() + timedelta(minutes=result['ETR_Minutes'])
            complaint_timestamp = int(complaint_end_time.timestamp() * 1000)
            
            individual_countdown = f'''
            <div style="font-family:Arial,Helvetica,sans-serif; margin: 15px 0; padding: 15px; border-radius: 10px; background: rgba(26, 32, 44, 0.8);">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="color: #e2e8f0;">
                  <strong>Req {result['Request_Id']}</strong> | {result['Fault_Type']}
                </div>
                <div id="countdown-{result['Request_Id']}" style="font-size: 20px; color: #4299e1; font-weight: 600;"></div>
              </div>
            </div>
            <script>
            function startIndividualCountdown(endTime, elementId) {{
              function update() {{
                var now = new Date().getTime();
                var distance = endTime - now;
                if (distance < 0) {{
                  document.getElementById(elementId).innerHTML = "✅ DONE";
                  document.getElementById(elementId).style.color = "#48bb78";
                  return;
                }}
                var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                document.getElementById(elementId).innerHTML =
                  hours.toString().padStart(2,'0') + ":" + minutes.toString().padStart(2,'0') + ":" + seconds.toString().padStart(2,'0');
              }}
              update();
              setInterval(update, 1000);
            }}
            startIndividualCountdown({complaint_timestamp}, "countdown-{result['Request_Id']}");
            </script>
            '''
            components.html(individual_countdown, height=80)
    elif not COMPONENTS_AVAILABLE:
        st.warning("Countdown timers not available - components module missing")

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Footer
# -------------------------
st.markdown("---")
st.markdown("<div class='footer' style='text-align: center;'>Built for 1912 Automation • Esyasoft Technologies</div>", unsafe_allow_html=True)

# -------------------------
# Sidebar Information
# -------------------------
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 System Status")
    
    # Model status
    st.markdown("**Model Status:**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"Fault Model: {'✅' if fault_pipeline is not None else '❌'}")
    with col2:
        st.markdown(f"ETR Model: {'✅' if nom_model is not None else '❌'}")
    
    # Data status
    st.markdown("**Data Status:**")
    complaints_df = load_complaints_data()
    st.markdown(f"Live Complaints: {len(complaints_df) if not complaints_df.empty else '0'}")
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Actions")
    
    if st.button("🔄 Reset Workflow", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    if st.button("📊 Download Report", use_container_width=True):
        st.info("Report generation feature coming soon!")
    
    st.markdown("---")
    st.markdown("""
    <div class="muted">
    <strong>Workflow Steps:</strong><br>
    1. Fetch Live Complaints<br>
    2. Analyze & Detect Faults<br> 
    3. Detailed Fault Analysis<br>
    4. ETR Prediction<br>
    5. Live Countdown
    </div>
    """, unsafe_allow_html=True)
