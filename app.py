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
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        color: #ecf0f1;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    .stTabs > div > div > div > div {
        font-weight: bold;
        font-size: 1.1rem;
        color: #2c3e50;
    }
    .metric-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e3e6f0;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    .metric-card h4 {
        color: #2c3e50;
        margin-bottom: 1rem;
        font-size: 1.2rem;
        font-weight: 600;
    }
    .metric-card p {
        color: #5a6c7d;
        margin: 0.5rem 0;
        font-size: 1rem;
        line-height: 1.5;
    }
    .metric-card code {
        background: #f8f9fa;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        color: #e74c3c;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .success-card {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
    }
    .success-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.3rem;
    }
    .success-card p {
        margin: 0;
        opacity: 0.95;
    }
    .risk-high {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: bold;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 8px rgba(231, 76, 60, 0.3);
    }
    .risk-medium {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: bold;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 8px rgba(243, 156, 18, 0.3);
    }
    .risk-low {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: bold;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 8px rgba(39, 174, 96, 0.3);
    }
    .finding-card {
        background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
        border-left: 5px solid #e53e3e;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-radius: 8px;
        color: #2d3748;
        box-shadow: 0 2px 6px rgba(229, 62, 62, 0.15);
    }
    .finding-card strong {
        color: #c53030;
        font-size: 1.05rem;
    }
    .info-card {
        background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
        border-left: 5px solid #3182ce;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-radius: 8px;
        color: #2d3748;
        box-shadow: 0 2px 6px rgba(49, 130, 206, 0.15);
    }
    .recommendation-card {
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
        border-left: 5px solid #38a169;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-radius: 8px;
        color: #2d3748;
        box-shadow: 0 2px 6px rgba(56, 161, 105, 0.15);
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
                    st.markdown(f"""
                    <div style="background: #e8f4fd; border-left: 4px solid #0066cc; padding: 1rem; margin: 1rem 0; border-radius: 4px; color: #004085;">
                        <strong>🔍 Analysis Notes:</strong> {" • ".join(result["notes"])}
                    </div>
                    """, unsafe_allow_html=True)

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
        st.markdown(f"""
        <div class="info-card">
            <strong>📁 File Selected:</strong> {uploaded_file.name} ({uploaded_file.size} bytes)
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📑 Analyze File", type="primary", use_container_width=True):
            with st.spinner("🔍 Analyzing file for sensitive data..."):
                findings = scan_file(uploaded_file)

                st.markdown("### 📄 File Scan Result")
                
                if findings:
                    st.markdown(f"""
                    <div class="finding-card">
                        <strong>🚨 {len(findings)} types of sensitive data found!</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for f in findings:
                        st.markdown(f"""
                        <div class="finding-card">
                            <strong>🔍 {f}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("### 💡 Recommendations")
                    st.markdown("""
                    <div class="recommendation-card">
                        <strong>🛡️ Security Actions:</strong><br>
                        • Remove or encrypt sensitive personal data<br>
                        • Implement proper access controls<br>
                        • Consider data anonymization techniques<br>
                        • Regular security audits and monitoring
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    st.markdown("""
                    <div class="success-card">
                        <h4>✅ No Sensitive Data Found</h4>
                        <p>The uploaded file appears to be clean of detectable sensitive information.</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-card">
            <strong>👆 Please upload a file to begin analysis</strong><br>
            Supported formats: TXT, PDF, DOCX
        </div>
        """, unsafe_allow_html=True)

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
