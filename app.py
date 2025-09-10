import streamlit as st
import json
import pandas as pd
import altair as alt

from core.cloud_scanner import scan_cloud_url
from core.data_scanner import scan_file

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Cloud Security Analyzer",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: #f0f0f0;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    .stTabs > div > div > div > div {
        font-weight: bold;
        font-size: 1.1rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    .success-card {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .risk-high {
        background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
    }
    .risk-medium {
        background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
    }
    .risk-low {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Helper - Risk Badge
# ---------------------------
def risk_badge(risk):
    risk_styles = {
        "High": "risk-high",
        "Medium": "risk-medium", 
        "Low": "risk-low"
    }
    style_class = risk_styles.get(risk, "risk-low")
    return f"<span class='{style_class}'>{risk}</span>"

# ---------------------------
# Header
# ---------------------------
st.markdown("""
<div class="main-header">
    <h1>🔐 Cloud Security Analyzer</h1>
    <p>Detect misconfigurations & sensitive data leaks in cloud apps</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# Tabs
# ---------------------------
tab1, tab2, tab3 = st.tabs(["☁️ Scan Cloud URL", "📂 Analyze File", "📊 Dashboard"])

# ---------------------------
# Tab 1 - Cloud URL Scanner
# ---------------------------
with tab1:
    st.subheader("☁️ Scan Cloud URL")
    st.markdown("Analyze cloud storage URLs for security misconfigurations and public exposure risks.")

    col1, col2 = st.columns([3, 1])
    
    with col1:
        url = st.text_input(
            "Enter a cloud/object URL (e.g., S3/Blob/GCS object URL)", 
            "",
            placeholder="https://my-bucket.s3.amazonaws.com/data.csv"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        scan_button = st.button("🔎 Scan URL", type="primary", use_container_width=True)
    
    if scan_button:
        if url:
            with st.spinner("🔍 Scanning cloud URL for security issues..."):
                result = scan_cloud_url(url)

                st.markdown("### 🔍 Cloud Scan Result")
                
                # Create result cards
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>📍 Target URL</h4>
                        <p><code>{result['url']}</code></p>
                        <p><strong>Host:</strong> {result['host']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>📊 Scan Status</h4>
                        <p><strong>Status:</strong> {result['status']}</p>
                        <p><strong>HTTP Code:</strong> {result['http_code']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>⚠️ Risk Assessment</h4>
                        <p><strong>Risk Level:</strong> {risk_badge(result['risk'])}</p>
                    </div>
                    """, unsafe_allow_html=True)

                if result.get("notes"):
                    st.warning("**🔍 Analysis Notes:** " + " • ".join(result["notes"]))

                with st.expander("📄 Detailed JSON Result"):
                    st.json(result)
        else:
            st.error("⚠️ Please enter a valid URL to scan.")

# ---------------------------
# Tab 2 - File Scanner
# ---------------------------
with tab2:
    st.subheader("📂 Analyze File")
    st.markdown("Upload files to scan for sensitive data like Aadhaar, PAN, emails, and other personal information.")

    uploaded_file = st.file_uploader(
        "Upload a file (TXT, PDF, DOCX)", 
        type=["txt", "pdf", "docx"],
        help="Supported formats: Text files (.txt), PDF documents (.pdf), Word documents (.docx)"
    )
    
    if uploaded_file:
        st.info(f"📁 **File Selected:** {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        if st.button("📑 Analyze File", type="primary", use_container_width=True):
            with st.spinner("🔍 Analyzing file for sensitive data..."):
                findings = scan_file(uploaded_file)

                st.markdown("### 📄 File Scan Result")
                
                if findings:
                    st.error(f"🚨 **{len(findings)} types of sensitive data found!**")
                    
                    for f in findings:
                        st.markdown(f"""
                        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; margin: 0.5rem 0; border-radius: 4px;">
                            <strong>🔍 {f}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("### � Recommendations")
                    st.info("• Remove or encrypt sensitive personal data\n• Implement access controls\n• Consider data anonymization techniques")
                    
                else:
                    st.markdown("""
                    <div class="success-card">
                        <h4>✅ No Sensitive Data Found</h4>
                        <p>The uploaded file appears to be clean of detectable sensitive information.</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("👆 Please upload a file to begin analysis")

# ---------------------------
# Tab 3 - Dashboard (sample demo)
# ---------------------------
with tab3:
    st.subheader("📊 Security Dashboard")

    # Demo risk data - replace with real database later
    data = pd.DataFrame({
        "Risk": ["High", "Medium", "Low"],
        "Count": [12, 8, 5]
    })

    st.write("### Risk Distribution")
    chart = alt.Chart(data).mark_arc().encode(
        theta="Count",
        color="Risk",
        tooltip=["Risk", "Count"]
    )
    st.altair_chart(chart, use_container_width=True)

    st.write("### Risk Counts (Table)")
    st.dataframe(data)
