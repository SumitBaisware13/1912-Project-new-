# app.py - Minimal Working Version for Streamlit Cloud
import streamlit as st
import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta
import time

# -------------------------
# Project identity
# -------------------------
PROJECT_NAME = "1912 Automation — Smart Grid Intelligence"
PROJECT_TAGLINE = "Advanced Fault Detection • Predictive Analytics • Automated Restoration"

# -------------------------
# Enhanced Professional CSS Theme
# -------------------------
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(135deg, #0c1a2d 0%, #1a365d 50%, #2d3748 100%); 
        color: #e2e8f0; 
        font-family: 'Inter', sans-serif;
    }
    
    .card { 
        background: rgba(26, 32, 44, 0.85); 
        border-radius: 16px; 
        padding: 24px; 
        box-shadow: 0 12px 32px rgba(0,0,0,0.3); 
        border: 1px solid rgba(74, 85, 104, 0.3);
        margin-bottom: 20px;
    }
    
    .proj-title { 
        font-size: 32px; 
        font-weight: 800; 
        color: #ffffff; 
        text-align: center;
        margin-bottom: 12px;
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
    
    .complaint-card {
        background: linear-gradient(135deg, rgba(26, 32, 44, 0.9), rgba(45, 55, 72, 0.9));
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        border-left: 6px solid #4299e1;
        border: 1px solid rgba(74, 85, 104, 0.3);
    }
    
    .status-success { color: #48bb78; font-weight: 700; }
    .status-fail { color: #f56565; font-weight: 700; }
    .status-processing { color: #ed8936; font-weight: 700; }
    
    .feature-box {
        background: linear-gradient(135deg, #4299e1, #38b2ac);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 12px 0;
        box-shadow: 0 8px 25px rgba(66, 153, 225, 0.4);
        text-align: center;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #4299e1, #38b2ac) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# Sample Data Generation
# -------------------------
def generate_sample_complaints():
    """Generate sample complaint data for demo"""
    sample_data = {
        'Request_Id': [f'REQ{str(i).zfill(3)}' for i in range(1, 21)],
        'Feeder_MSN': [f'FDR{str(i).zfill(3)}' for i in range(1, 21)],
        'Feeder_ProcessStatus': random.choices(['success', 'fail'], weights=[0.7, 0.3], k=20),
        'DTR_MSN': [f'DTR{str(i).zfill(3)}' for i in range(1, 21)],
        'DTR_ProcessStatus': random.choices(['success', 'fail'], weights=[0.6, 0.4], k=20),
        'Consumer_MSN': [f'CON{str(i).zfill(3)}' for i in range(1, 21)],
        'Consumer_ProcessStatus': random.choices(['success', 'fail'], weights=[0.5, 0.5], k=20),
        'Consumer_Phase_Id': random.choices([1, 3], weights=[0.3, 0.7], k=20),
        'f_vr': [round(random.uniform(220, 240), 1) for _ in range(20)],
        'f_vy': [round(random.uniform(220, 240), 1) for _ in range(20)],
        'f_vb': [round(random.uniform(220, 240), 1) for _ in range(20)],
        'f_ir': [round(random.uniform(0.5, 2.0), 2) for _ in range(20)],
        'f_iy': [round(random.uniform(0.5, 2.0), 2) for _ in range(20)],
        'f_ib': [round(random.uniform(0.5, 2.0), 2) for _ in range(20)],
        'd_vr': [round(random.uniform(220, 240), 1) for _ in range(20)],
        'd_vy': [round(random.uniform(220, 240), 1) for _ in range(20)],
        'd_vb': [round(random.uniform(220, 240), 1) for _ in range(20)],
        'd_ir': [round(random.uniform(0.1, 1.5), 2) for _ in range(20)],
        'd_iy': [round(random.uniform(0.1, 1.5), 2) for _ in range(20)],
        'd_ib': [round(random.uniform(0.1, 1.5), 2) for _ in range(20)],
        'Final_Label': random.choices(['DTHT', 'DTLT', 'FOC', 'FOC/DT HT'], k=20),
        'region': random.choices(['Region A', 'Region B', 'Region C'], k=20),
        'circle': random.choices(['Circle 1', 'Circle 2', 'Circle 3'], k=20),
        'division': random.choices(['Division X', 'Division Y', 'Division Z'], k=20),
        'zone': random.choices(['Zone P', 'Zone Q', 'Zone R'], k=20)
    }
    return pd.DataFrame(sample_data)

# -------------------------
# Header Section
# -------------------------
st.markdown(f"""
    <div style='text-align: center; padding: 20px 0;'>
        <div class="proj-title">⚡ 1912 Automation — Smart Grid Intelligence</div>
        <div class="proj-tag">Advanced Fault Detection • Predictive Analytics • Automated Restoration</div>
    </div>
""", unsafe_allow_html=True)

# -------------------------
# Main Application Workflow
# -------------------------

# Step 1: Fetch Live Complaints
st.markdown("---")
st.subheader("📥 Step 1: Fetch Live Complaints")

if st.button("🚀 Click to Fetch Live Complaints & Predict Faults", use_container_width=True, type="primary"):
    
    # Generate sample complaints data
    complaints_df = generate_sample_complaints()
    
    # Select random complaints (5-8)
    num_complaints = min(random.randint(5, 8), len(complaints_df))
    selected_complaints = complaints_df.sample(n=num_complaints)
    
    # Display complaints
    st.success(f"✅ Successfully fetched {num_complaints} live complaints!")
    
    for idx, complaint in selected_complaints.iterrows():
        current_time = datetime.now()
        # Create complaint time 2-3 minutes before current time
        complaint_time = current_time - timedelta(minutes=random.randint(2, 3))
        
        st.markdown(f"""
        <div class="complaint-card">
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

# Step 2: Side Panel - Fault Information
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Fault Types & Information")

fault_info = {
    "DTHT": "Distribution Transformer High Imbalance - Significant voltage imbalance across three phases",
    "DTLT": "Distribution Transformer Low Current - One phase has zero current indicating broken line", 
    "FOC": "Failure at Consumer End - Power reaching consumer premises but internal issue detected",
    "FOC/DT HT": "DT Communication Failure - Transformer meter offline, using ping patterns for diagnosis"
}

for fault, description in fault_info.items():
    with st.sidebar.expander(f"⚡ {fault}"):
        st.write(description)

# Step 3: Analyze Complaints (if step 2 completed)
if 'current_step' in st.session_state and st.session_state.current_step >= 2:
    st.markdown("---")
    st.subheader("🔬 Step 2: Analyze Complaints & Detect Faults")
    
    if st.button("🔍 Start Fault Detection Analysis", use_container_width=True, type="secondary"):
        st.session_state.current_step = 3

# Step 4: Detailed Analysis (if step 3 completed)
if 'current_step' in st.session_state and st.session_state.current_step >= 3:
    st.markdown("---")
    st.subheader("📊 Step 3: Detailed Fault Analysis")
    
    selected_complaints = st.session_state.get('selected_complaints', pd.DataFrame())
    
    if not selected_complaints.empty:
        # Process each complaint
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
                    <div class="card">
                        <h4>📋 Complaint #{i+1}</h4>
                        <p><strong>Request ID:</strong> {complaint.get('Request_Id', 'N/A')}</p>
                        <p><strong>Feeder MSN:</strong> {complaint.get('Feeder_MSN', 'N/A')}</p>
                        <p><strong>DTR MSN:</strong> {complaint.get('DTR_MSN', 'N/A')}</p>
                        <p><strong>Consumer MSN:</strong> {complaint.get('Consumer_MSN', 'N/A')}</p>
                        <p><strong>Phase:</strong> {complaint.get('Consumer_Phase_Id', 'N/A')}-Phase</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Use Streamlit components for analysis
                    st.markdown("#### 🔍 Ping Status Analysis")
                    
                    # Create columns for ping status
                    ping_col1, ping_col2, ping_col3 = st.columns(3)
                    with ping_col1:
                        status_color = "🟢" if complaint.get('Feeder_ProcessStatus') == 'success' else "🔴"
                        st.metric("Feeder", complaint.get('Feeder_ProcessStatus', 'N/A'))
                    
                    with ping_col2:
                        status_color = "🟢" if complaint.get('DTR_ProcessStatus') == 'success' else "🔴"
                        st.metric("DTR", complaint.get('DTR_ProcessStatus', 'N/A'))
                    
                    with ping_col3:
                        status_color = "🟢" if complaint.get('Consumer_ProcessStatus') == 'success' else "🔴"
                        st.metric("Consumer", complaint.get('Consumer_ProcessStatus', 'N/A'))
                    
                    st.markdown("---")
                    st.markdown("#### 📈 Intensity Profile Data")
                    
                    # Feeder readings
                    st.markdown("**Feeder Readings**")
                    feeder_col1, feeder_col2 = st.columns(2)
                    with feeder_col1:
                        st.write(f"**Voltage:**")
                        st.write(f"R: {complaint.get('f_vr', 0):.1f} V")
                        st.write(f"Y: {complaint.get('f_vy', 0):.1f} V") 
                        st.write(f"B: {complaint.get('f_vb', 0):.1f} V")
                    
                    with feeder_col2:
                        st.write(f"**Current:**")
                        st.write(f"R: {complaint.get('f_ir', 0):.2f} A")
                        st.write(f"Y: {complaint.get('f_iy', 0):.2f} A")
                        st.write(f"B: {complaint.get('f_ib', 0):.2f} A")
                    
                    st.markdown("---")
                    
                    # DTR readings
                    st.markdown("**DTR Readings**")
                    dtr_col1, dtr_col2 = st.columns(2)
                    with dtr_col1:
                        st.write(f"**Voltage:**")
                        st.write(f"R: {complaint.get('d_vr', 0):.1f} V")
                        st.write(f"Y: {complaint.get('d_vy', 0):.1f} V")
                        st.write(f"B: {complaint.get('d_vb', 0):.1f} V")
                    
                    with dtr_col2:
                        st.write(f"**Current:**")
                        st.write(f"R: {complaint.get('d_ir', 0):.2f} A")
                        st.write(f"Y: {complaint.get('d_iy', 0):.2f} A")
                        st.write(f"B: {complaint.get('d_ib', 0):.2f} A")
            
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
            st.write("**Fault Type Distribution**")
            chart_data = pd.DataFrame({
                'Fault Type': fault_counts.index,
                'Count': fault_counts.values
            })
            st.bar_chart(chart_data.set_index('Fault Type'))
        
        with col2:
            st.write("**Fault Count Summary**")
            st.dataframe(fault_counts, use_container_width=True)
        
        # Store analysis results
        st.session_state.analysis_complete = True
        st.session_state.analyzed_complaints = selected_complaints

# Step 5: ETR Prediction (if analysis complete)
if 'analysis_complete' in st.session_state and st.session_state.analysis_complete:
    st.markdown("---")
    st.subheader("⏱️ Step 4: Estimate Time for Restoration")
    
    if st.button("🕒 Predict Restoration Time (ETR)", use_container_width=True, type="primary"):
        st.session_state.etr_prediction_started = True

# Step 6: ETR Prediction Process
if 'etr_prediction_started' in st.session_state and st.session_state.etr_prediction_started:
    st.markdown("---")
    
    analyzed_complaints = st.session_state.get('analyzed_complaints', pd.DataFrame())
    
    if not analyzed_complaints.empty:
        # Show location hierarchy visualization
        st.subheader("🗺️ Location Analysis")
        
        locations = analyzed_complaints[['region', 'circle', 'division', 'zone']].drop_duplicates()
        
        for _, loc in locations.iterrows():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"<div class='feature-box'><strong>Region</strong><br>{loc['region']}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='feature-box'><strong>Circle</strong><br>{loc['circle']}</div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='feature-box'><strong>Division</strong><br>{loc['division']}</div>", unsafe_allow_html=True)
            with col4:
                st.markdown(f"<div class='feature-box'><strong>Zone</strong><br>{loc['zone']}</div>", unsafe_allow_html=True)
        
        # ETR Prediction Results
        st.subheader("🎯 ETR Prediction Results")
        
        # Simulate ETR prediction for each complaint
        for i, (idx, complaint) in enumerate(analyzed_complaints.iterrows()):
            # Simulate ETR prediction (in minutes)
            base_etr = random.randint(30, 180)
            etr_minutes = base_etr
            etr_human = f"{etr_minutes//60} hr {etr_minutes%60} min" if etr_minutes >= 60 else f"{etr_minutes} min"
            
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

# -------------------------
# Footer
# -------------------------
st.markdown("---")
st.markdown("<div style='color: #a0aec0; text-align: center;'>Built for 1912 Automation • Esyasoft Technologies</div>", unsafe_allow_html=True)

# -------------------------
# Sidebar Information
# -------------------------
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 System Status")
    
    st.markdown("**Data Status:**")
    st.markdown("Live Complaints: 20+")
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Actions")
    
    if st.button("🔄 Reset Workflow", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
