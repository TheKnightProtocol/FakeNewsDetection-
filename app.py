# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import hashlib
import feedparser
from bs4 import BeautifulSoup
import requests
import time
from fpdf import FPDF
import random

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Supply Chain Defender", page_icon="🛡️", layout="wide")

# ---------- DATA GENERATORS (No external files needed) ----------
def get_default_suppliers():
    return pd.DataFrame([
        [1, 'TSMC', 23.6978, 120.9605, 'Taiwan', 'Semiconductor', 5000000, 1],
        [2, 'Toyota', 35.1815, 136.9066, 'Japan', 'Automotive', 8000000, 1],
        [3, 'Samsung', 37.5665, 126.9780, 'S. Korea', 'Electronics', 4500000, 2],
        [4, 'Maersk', 55.6761, 12.5683, 'Denmark', 'Shipping', 9800000, 1],
        [5, 'Intel', 45.3409, -122.9908, 'USA', 'Semiconductor', 3200000, 1],
        [6, 'Bosch', 48.7833, 9.1833, 'Germany', 'Automotive', 4600000, 2],
        [7, 'DHL', 50.7374, 7.0982, 'Germany', 'Logistics', 3200000, 1],
        [8, 'Boeing', 47.6062, -122.3321, 'USA', 'Aerospace', 7200000, 1],
    ], columns=['id', 'name', 'lat', 'lng', 'country', 'industry', 'annual_spend_usd', 'tier'])

# ---------- SESSION STATE ----------
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.articles = pd.DataFrame()
    st.session_state.risk_data = pd.DataFrame()
    st.session_state.news_fetched = False

# ---------- SIDE BAR ----------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/security-checked--v1.png", width=60)
    st.title("🛡️ Defender")
    
    if st.button("🔄 Fetch Demo News", use_container_width=True):
        with st.spinner("Generating realistic supply chain alerts..."):
            # Generate realistic demo articles
            demo_news = [
                {"title": "Magna International Reports Record Q3 Profits", "summary": "Automotive supplier exceeds expectations.", "risk": "legitimate"},
                {"title": "BREAKING: Major Fire at TSMC Fab in Taiwan", "summary": "Production halted indefinitely, global chip shortage worsens.", "risk": "supplier"},
                {"title": "Toyota Plant Strike Halts Production", "summary": "5000 workers walk out demanding higher wages.", "risk": "labor"},
                {"title": "US Imposes New Tariffs on Chinese Semiconductors", "summary": "25% tariff hike effective immediately, supply chains scramble.", "risk": "geopolitical"},
                {"title": "DHL Announces $2B Green Logistics Investment", "summary": "Expansion of electric vehicle fleet in Europe.", "risk": "legitimate"},
                {"title": "Hurricane Disrupts Gulf Coast Shipping Lanes", "summary": "Major ports closed, delays expected for 2 weeks.", "risk": "weather"},
                {"title": "Fake News: Samsung Battery Plant Explosion", "summary": "Company denies rumors, stock recovers after initial drop.", "risk": "financial"},
                {"title": "Boeing Supplier Quality Issues Delay Deliveries", "summary": "Fuselage defects found, delivery timeline pushed back.", "risk": "supplier"}
            ]
            
            articles = []
            for item in demo_news:
                articles.append({
                    'id': hashlib.md5(item['title'].encode()).hexdigest()[:8],
                    'title': item['title'],
                    'summary': item['summary'],
                    'link': '#',
                    'published': datetime.now().isoformat(),
                    'source': 'Reuters / Bloomberg (Demo)',
                    'risk_categories': [item['risk']]
                })
            
            st.session_state.articles = pd.DataFrame(articles)
            st.session_state.news_fetched = True
            st.success(f"✅ Loaded {len(articles)} alerts")
            time.sleep(0.5)
            st.rerun()

    if st.button("🧠 Run Risk Analysis", use_container_width=True):
        if not st.session_state.news_fetched:
            st.warning("Fetch news first!")
        else:
            with st.spinner("Calculating supplier exposure..."):
                suppliers = get_default_suppliers()
                supplier_risks = []
                
                # Simple risk mapping
                risk_map = {
                    'financial': 0.9, 'supplier': 0.8, 'labor': 0.7, 
                    'geopolitical': 0.75, 'weather': 0.6, 'legitimate': 0.1
                }
                
                for _, supplier in suppliers.iterrows():
                    base_risk = random.uniform(0.1, 0.3)  # Base operational risk
                    
                    # Check if any article mentions this supplier
                    for _, article in st.session_state.articles.iterrows():
                        if supplier['name'].lower() in article['title'].lower():
                            for cat in article['risk_categories']:
                                base_risk = max(base_risk, risk_map.get(cat, 0.5) * random.uniform(0.8, 1.2))
                    
                    exposure = supplier['annual_spend_usd'] * min(base_risk, 1.0)
                    supplier_risks.append({
                        'name': supplier['name'],
                        'country': supplier['country'],
                        'industry': supplier['industry'],
                        'tier': supplier['tier'],
                        'risk_score': round(min(base_risk, 1.0), 3),
                        'exposure_at_risk_usd': round(exposure, 0),
                        'latitude': supplier['lat'],
                        'longitude': supplier['lng']
                    })
                
                st.session_state.risk_data = pd.DataFrame(supplier_risks)
                st.success("✅ Analysis complete!")
                st.balloons()
                time.sleep(0.5)
                st.rerun()

    st.divider()
    if st.button("📊 Download PDF Report", use_container_width=True):
        if not st.session_state.risk_data.empty:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(190, 10, "SUPPLY CHAIN RISK REPORT", ln=True, align="C")
            pdf.set_font("Arial", "", 10)
            pdf.cell(190, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align="R")
            pdf.ln(10)
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(190, 10, "Critical Suppliers", ln=True)
            pdf.set_font("Arial", "B", 9)
            for col in ['Name', 'Country', 'Risk']:
                pdf.cell(60, 8, col, border=1)
            pdf.ln()
            
            pdf.set_font("Arial", "", 9)
            for _, row in st.session_state.risk_data.head(10).iterrows():
                pdf.cell(60, 8, row['name'], border=1)
                pdf.cell(60, 8, row['country'], border=1)
                pdf.cell(60, 8, f"{row['risk_score']:.1%}", border=1)
                pdf.ln()
            
            pdf.output("report.pdf")
            with open("report.pdf", "rb") as f:
                st.download_button("📥 Click to Download", f, file_name="supply_chain_risk.pdf")
        else:
            st.warning("Run analysis first!")

# ---------- MAIN DASHBOARD ----------
st.title("🛡️ Supply Chain Defender")
st.caption("Real-time Risk Intelligence Dashboard")

if not st.session_state.risk_data.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Suppliers Monitored", len(st.session_state.risk_data))
    col2.metric("Avg Risk Score", f"{st.session_state.risk_data['risk_score'].mean():.1%}")
    col3.metric("Total Exposure", f"${st.session_state.risk_data['exposure_at_risk_usd'].sum()/1e6:.1f}M")

    tab1, tab2 = st.tabs(["📊 Supplier Risk", "🌍 Global Heatmap"])
    
    with tab1:
        st.dataframe(
            st.session_state.risk_data.sort_values('risk_score', ascending=False),
            use_container_width=True,
            column_config={
                "risk_score": st.column_config.ProgressColumn("Risk", format="%.1f%%", min_value=0, max_value=1),
                "exposure_at_risk_usd": st.column_config.NumberColumn("Exposure ($)", format="$%.0f")
            }
        )
    
    with tab2:
        fig = px.scatter_mapbox(
            st.session_state.risk_data,
            lat="latitude", lon="longitude",
            size="exposure_at_risk_usd",
            color="risk_score",
            hover_name="name",
            color_continuous_scale="RdYlGn_r",
            size_max=50, zoom=1, height=500
        )
        fig.update_layout(mapbox_style="open-street-map", margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👈 Click 'Fetch Demo News' then 'Run Risk Analysis' to start")

st.divider()
st.caption("Built for Supply Chain Resilience")
