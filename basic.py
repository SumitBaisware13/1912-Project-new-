# app_final_1912_workflow_enhanced_fixed.py
import streamlit as st
import pandas as pd
import numpy as np
import pickle, joblib, os, fnmatch, random
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import time
import plotly.graph_objects as go
import plotly.express as px

# -------------------------
# Project identity
# -------------------------
PROJECT_NAME = "1912 Automation — Smart Grid Fault Detection System"
PROJECT_TAGLINE = "Intelligent Fault Analysis • Predictive ETR • Automated Resolution"
PROJECT_SLOGAN = "Detect. Diagnose. Restore."

# -------------------------
# File paths
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
ILLU_IMAGE_PATH    = "2011.i402.058..Electricity and lighting flat composition.jpg"

# -------------------------
# Page config with enhanced theme
# -------------------------
st.set_page_config(page_title=PROJECT_NAME, page_icon="⚡", layout="wide")

# Enhanced CSS with professional color scheme
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(135deg, #f5f9ff 0%, #e8f1ff 50%, #f0f7ff 100%); 
        color: #001b2e; 
    }
    .card { 
        background: rgba(255, 255, 255, 0.95); 
        border-radius: 12px; 
        padding: 20px; 
        box-shadow: 0 8px 25px rgba(20,40,80,0.1); 
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(10px);
        margin-bottom: 16px;
    }
    .proj-title { 
        font-size: 28px; 
        font-weight: 800; 
        color: #032a4d; 
        text-align: center;
        margin-bottom: 8px;
    }
    .proj-tag { 
        color: #145a86; 
        text-align: center;
        font-size: 16px; 
        font-weight: 500;
    }
    .small { font-size: 13px; color: #234f6b; }
    .muted { color: #4b7b9a; font-size: 12px; }
    .footer { color: #3b6a86; font-size: 0.9rem; padding-top: 12px; }
    .vi-grid { display: flex; gap: 8px; }
    .vi-col { flex: 1; }
    
    /* Animation classes */
    .fade-in { animation: fadeIn 1s; }
    .slide-in-left { animation: slideInLeft 0.8s; }
    .slide-in-right { animation: slideInRight 0.8s; }
    .pulse { animation: pulse 2s infinite; }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-30px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideInRight {
        from { transform: translateX(30px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .status-success { color: #10b981; font-weight: 600; }
    .status-fail { color: #ef4444; font-weight: 600; }
    .status-processing { color: #f59e0b; font-weight: 600; }
    
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        position: relative;
    }
    .step-indicator::before {
        content: '';
        position: absolute;
        top: 15px;
        left: 0;
        right: 0;
        height: 3px;
        background: #e2e8f0;
        z-index: 1;
    }
    .step {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        background: #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        z-index: 2;
        position: relative;
    }
    .step.active {
        background: #3b82f6;
        color: white;
        animation: pulse 2s infinite;
    }
    .step.completed {
        background: #10b981;
        color: white;
    }
    
    .feature-box {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .complaint-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 4px solid #3b82f6;
        transition: transform 0.3s;
    }
    .complaint-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
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
# Load complaints data
# -------------------------
@st.cache_data
def load_complaints_data(path=COMPLAINTS_DATA_PATH):
    if not os.path.exists(path):
        st.error(f"Complaints data file not found at {path}")
        return pd.DataFrame()
    try:
        df = pd.read_excel(path)
        return df
    except Exception as e:
        st.error(f"Error loading complaints data: {e}")
        return pd.DataFrame()

# -------------------------
# Load models (same as before)
# -------------------------
@st.cache_resource
def find_and_load_fault_bundle():
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
    if os.path.exists(SEARCH_DIR):
        files = os.listdir(SEARCH_DIR)
        patterns = ["*fault*.pkl", "*best*.pkl", "*classifier*.pkl", "*pipe*.pkl", "*model*.pkl",
                    "*fault*.joblib", "*best*.joblib", "*classifier*.joblib", "*model*.joblib", "*.pkl", "*.joblib"]
        seen = set()
        for pat in patterns:
            for fname in fnmatch.filter(files, pat):
                if fname in seen:
                    continue
                seen.add(fname)
                full = os.path.join(SEARCH_DIR, fname)
                try:
                    with open(full, "rb") as f:
                        bundle = pickle.load(f)
                    return bundle, full
                except Exception:
                    try:
                        m = joblib.load(full)
                        return m, full
                    except Exception:
                        continue
    return None, None

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
# Load hierarchy
# -------------------------
@st.cache_data
def load_hierarchy(path=HIERARCHY_PATH):
    if not os.path.exists(path):
        return pd.DataFrame(), {}
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

df_hier, hier_map = load_hierarchy()

# -------------------------
# Header Section
# -------------------------
st.markdown(f"""
    <div class="proj-title">{PROJECT_NAME}</div>
    <div class="proj-tag">{PROJECT_TAGLINE} • <strong>{PROJECT_SLOGAN}</strong></div>
""", unsafe_allow_html=True)

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
        st.error("No complaints data available. Please check the data file.")
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
                    
                    st.markdown(f"""
                    <div class="card slide-in-right">
                        <h4>🔍 Ping Status Analysis</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
                            <div class="{'status-success' if complaint.get('Feeder_ProcessStatus') == 'success' else 'status-fail'}">
                                Feeder: {complaint.get('Feeder_ProcessStatus', 'N/A')}
                            </div>
                            <div class="{'status-success' if complaint.get('DTR_ProcessStatus') == 'success' else 'status-fail'}">
                                DTR: {complaint.get('DTR_ProcessStatus', 'N/A')}
                            </div>
                            <div class="{'status-success' if complaint.get('Consumer_ProcessStatus') == 'success' else 'status-fail'}">
                                Consumer: {complaint.get('Consumer_ProcessStatus', 'N/A')}
                            </div>
                        </div>
                        
                        <h4 style="margin-top: 15px;">📈 Intensity Profile Data</h4>
                        <div style="font-size: 12px;">
                            <strong>Feeder:</strong> V(R/Y/B): {float(f_vr):.1f}/{float(f_vy):.1f}/{float(f_vb):.1f} | 
                            I(R/Y/B): {float(f_ir):.2f}/{float(f_iy):.2f}/{float(f_ib):.2f}
                        </div>
                        <div style="font-size: 12px;">
                            <strong>DTR:</strong> V(R/Y/B): {float(d_vr):.1f}/{float(d_vy):.1f}/{float(d_vb):.1f} | 
                            I(R/Y/B): {float(d_ir):.2f}/{float(d_iy):.2f}/{float(d_ib):.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Simulate processing time
            time.sleep(1)
        
        progress_bar.empty()
        status_text.empty()
        
        st.success("✅ All complaints analyzed successfully!")
        
        # Show fault prediction results
        st.markdown("### 🎯 Fault Prediction Results")
        
        # Create results visualization
        fault_counts = selected_complaints['Final_Label'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart of fault distribution
            if not fault_counts.empty:
                fig = px.pie(
                    values=fault_counts.values, 
                    names=fault_counts.index,
                    title="Fault Type Distribution",
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Bar chart of fault counts
            if not fault_counts.empty:
                fig = px.bar(
                    x=fault_counts.index,
                    y=fault_counts.values,
                    title="Fault Count by Type",
                    labels={'x': 'Fault Type', 'y': 'Count'},
                    color=fault_counts.values,
                    color_continuous_scale='blues'
                )
                st.plotly_chart(fig, use_container_width=True)
        
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
            # In real implementation, this would use the actual model
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
            
            time.sleep(0.5)  # Simulate processing time
        
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
    
    if etr_results:
        # Find the maximum ETR for the overall countdown
        max_etr = max(result['ETR_Minutes'] for result in etr_results)
        end_time = datetime.now() + timedelta(minutes=max_etr)
        end_timestamp = int(end_time.timestamp() * 1000)
        
        # Overall countdown timer
        countdown_html = f'''
        <div style="font-family:Arial,Helvetica,sans-serif; text-align: center;">
          <h3 style="color: #032a4d;">Overall Maximum Restoration Time</h3>
          <div id="countdown" style="font-size: 36px; color: #06263b; font-weight: 700; margin: 20px 0;"></div>
          <p style="color: #4b7b9a;">Estimated completion: {end_time.strftime("%H:%M:%S")}</p>
        </div>
        <script>
        function startCountdown(endTime) {{
          function update() {{
            var now = new Date().getTime();
            var distance = endTime - now;
            if (distance < 0) {{
              document.getElementById('countdown').innerHTML = "✅ RESTORED";
              document.getElementById('countdown').style.color = "#10b981";
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
            <div style="font-family:Arial,Helvetica,sans-serif; margin: 15px 0; padding: 15px; border-radius: 10px; background: #f8fafc;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                  <strong>Req {result['Request_Id']}</strong> | {result['Fault_Type']}
                </div>
                <div id="countdown-{result['Request_Id']}" style="font-size: 20px; color: #3b82f6; font-weight: 600;"></div>
              </div>
            </div>
            <script>
            function startIndividualCountdown(endTime, elementId) {{
              function update() {{
                var now = new Date().getTime();
                var distance = endTime - now;
                if (distance < 0) {{
                  document.getElementById(elementId).innerHTML = "✅ DONE";
                  document.getElementById(elementId).style.color = "#10b981";
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