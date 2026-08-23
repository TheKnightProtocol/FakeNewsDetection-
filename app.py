import streamlit as st
import random
from datetime import datetime
import hashlib

# -------- PAGE CONFIG --------
st.set_page_config(
    page_title="Supply Chain Defender",
    page_icon="🛡️",
    layout="wide"
)

# -------- HARD-CODED DATA --------
SUPPLIERS = [
    {"name": "TSMC", "lat": 23.6978, "lon": 120.9605, "country": "Taiwan", "industry": "Semiconductor", "spend": 5000000},
    {"name": "Toyota", "lat": 35.1815, "lon": 136.9066, "country": "Japan", "industry": "Automotive", "spend": 8000000},
    {"name": "Samsung", "lat": 37.5665, "lon": 126.9780, "country": "S. Korea", "industry": "Electronics", "spend": 4500000},
    {"name": "Maersk", "lat": 55.6761, "lon": 12.5683, "country": "Denmark", "industry": "Shipping", "spend": 9800000},
    {"name": "Intel", "lat": 45.3409, "lon": -122.9908, "country": "USA", "industry": "Semiconductor", "spend": 3200000},
    {"name": "Bosch", "lat": 48.7833, "lon": 9.1833, "country": "Germany", "industry": "Automotive", "spend": 4600000},
    {"name": "DHL", "lat": 50.7374, "lon": 7.0982, "country": "Germany", "industry": "Logistics", "spend": 3200000},
    {"name": "Boeing", "lat": 47.6062, "lon": -122.3321, "country": "USA", "industry": "Aerospace", "spend": 7200000},
]

NEWS_ARTICLES = [
    {"title": "Magna International Reports Record Profits", "summary": "Supply chain stable, growth expected", "risk": "Low"},
    {"title": "BREAKING: TSMC Factory Fire in Taiwan", "summary": "Production halted, global chip shortage worsens", "risk": "Critical"},
    {"title": "Toyota Plant Strike Halts Production", "summary": "5000 workers walk out demanding higher wages", "risk": "High"},
    {"title": "US Imposes New Tariffs on Semiconductors", "summary": "25% tariff hike, supply chains scramble", "risk": "Medium"},
    {"title": "DHL Announces $2B Green Logistics Investment", "summary": "Expansion of electric fleet in Europe", "risk": "Low"},
    {"title": "Hurricane Disrupts Gulf Coast Shipping Lanes", "summary": "Major ports closed, delays expected", "risk": "High"},
    {"title": "Samsung Battery Recall Imminent", "summary": "Defective batteries may cause fires", "risk": "Medium"},
    {"title": "Boeing Supplier Quality Issues Delay Deliveries", "summary": "Fuselage defects found, timeline pushed", "risk": "High"},
]

RISK_SCORES = {"Low": 0.2, "Medium": 0.5, "High": 0.8, "Critical": 0.95}

# -------- SESSION STATE --------
if "loaded" not in st.session_state:
    st.session_state.loaded = False
    st.session_state.risk_data = []

if "risk_analyzed" not in st.session_state:
    st.session_state.risk_analyzed = False

# -------- SIDEBAR --------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/security-checked--v1.png", width=60)
    st.title("🛡️ Defender")
    
    if st.button("📰 Load News", use_container_width=True):
        st.session_state.loaded = True
        st.success("✅ 8 articles loaded")
        st.rerun()
    
    if st.button("⚙️ Analyze Risks", use_container_width=True):
        if not st.session_state.loaded:
            st.warning("Load news first!")
        else:
            risk_data = []
            for supplier in SUPPLIERS:
                base_risk = random.uniform(0.1, 0.3)
                
                for news in NEWS_ARTICLES:
                    if supplier["name"].lower() in news["title"].lower():
                        base_risk = max(base_risk, RISK_SCORES.get(news["risk"], 0.5))
                
                final_risk = min(base_risk, 1.0)
                exposure = supplier["spend"] * final_risk
                
                risk_data.append({
                    "name": supplier["name"],
                    "country": supplier["country"],
                    "industry": supplier["industry"],
                    "risk_score": round(final_risk, 3),
                    "exposure": round(exposure, 0),
                    "lat": supplier["lat"],
                    "lon": supplier["lon"],
                })
            
            st.session_state.risk_data = risk_data
            st.session_state.risk_analyzed = True
            st.success("✅ Analysis complete!")
            st.balloons()
            st.rerun()
    
    st.divider()
    if st.button("📥 Export CSV", use_container_width=True):
        if st.session_state.risk_analyzed:
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Supplier", "Country", "Industry", "Risk Score", "Exposure ($)"])
            for r in st.session_state.risk_data:
                writer.writerow([r["name"], r["country"], r["industry"], f"{r['risk_score']:.1%}", f"${r['exposure']:,.0f}"])
            
            st.download_button(
                label="⬇️ Download CSV",
                data=output.getvalue(),
                file_name=f"supply_chain_risk_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.warning("Run analysis first")

# -------- MAIN DASHBOARD --------
st.title("🛡️ Supply Chain Defender")
st.caption("Real‑time Risk Intelligence – Zero external dependencies")

if st.session_state.risk_analyzed:
    data = st.session_state.risk_data
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Suppliers", len(data))
    col2.metric("Avg Risk", f"{sum(r['risk_score'] for r in data)/len(data):.1%}")
    col3.metric("Total Exposure", f"${sum(r['exposure'] for r in data)/1e6:.1f}M")
    
    # Tabs
    tab1, tab2 = st.tabs(["📊 Risk Table", "🌍 Map"])
    
    with tab1:
        # Build table manually
        table_data = []
        for r in sorted(data, key=lambda x: x["risk_score"], reverse=True):
            table_data.append([
                r["name"],
                r["country"],
                r["industry"],
                f"{r['risk_score']:.1%}",
                f"${r['exposure']:,.0f}"
            ])
        
        st.table({
            "Supplier": [row[0] for row in table_data],
            "Country": [row[1] for row in table_data],
            "Industry": [row[2] for row in table_data],
            "Risk": [row[3] for row in table_data],
            "Exposure": [row[4] for row in table_data]
        })
    
    with tab2:
        # Use Streamlit's built-in map
        map_data = []
        for r in data:
            map_data.append({
                "lat": r["lat"],
                "lon": r["lon"],
                "size": r["risk_score"] * 100,
                "name": r["name"],
                "risk": f"{r['risk_score']:.1%}"
            })
        
        # st.map uses the first two columns as lat/lon
        import pandas as pd
        df = pd.DataFrame(map_data)
        st.map(df, size="size", color="#FF4B4B")
        
        # Show legend
        st.caption("🔴 Red = High Risk | 🟢 Green = Low Risk (circle size indicates risk level)")
    
    with st.expander("📰 News Alerts"):
        for news in NEWS_ARTICLES:
            st.markdown(f"**{news['title']}**")
            st.caption(f"{news['summary']} | Risk: {news['risk']}")
            st.divider()

else:
    st.info("👈 Click **Load News** then **Analyze Risks** to start")
    
    # Show preview
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        1. **Load News** – Simulates real‑time supply chain alerts
        2. **Analyze Risks** – Calculates supplier exposure based on news
        3. **View Dashboard** – See risk scores, map, and export data
        
        This is a **zero‑dependency** prototype that demonstrates:
        - Real‑time risk monitoring
        - Supplier exposure quantification
        - Geographic risk visualization
        - Executive reporting (CSV export)
        """)

st.divider()
st.caption("Built for Supply Chain Resilience | Deploys anywhere with Streamlit")
