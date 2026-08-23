import streamlit as st
import plotly.express as px
import pandas as pd
import hashlib
import random
from datetime import datetime

# -------- HARD-CODED DEMO DATA --------
SUPPLIERS = [
    {"id": 1, "name": "TSMC", "lat": 23.6978, "lng": 120.9605, "country": "Taiwan", "industry": "Semiconductor", "annual_spend": 5000000, "tier": 1},
    {"id": 2, "name": "Toyota", "lat": 35.1815, "lng": 136.9066, "country": "Japan", "industry": "Automotive", "annual_spend": 8000000, "tier": 1},
    {"id": 3, "name": "Samsung", "lat": 37.5665, "lng": 126.9780, "country": "S. Korea", "industry": "Electronics", "annual_spend": 4500000, "tier": 2},
    {"id": 4, "name": "Maersk", "lat": 55.6761, "lng": 12.5683, "country": "Denmark", "industry": "Shipping", "annual_spend": 9800000, "tier": 1},
    {"id": 5, "name": "Intel", "lat": 45.3409, "lng": -122.9908, "country": "USA", "industry": "Semiconductor", "annual_spend": 3200000, "tier": 1},
    {"id": 6, "name": "Bosch", "lat": 48.7833, "lng": 9.1833, "country": "Germany", "industry": "Automotive", "annual_spend": 4600000, "tier": 2},
    {"id": 7, "name": "DHL", "lat": 50.7374, "lng": 7.0982, "country": "Germany", "industry": "Logistics", "annual_spend": 3200000, "tier": 1},
    {"id": 8, "name": "Boeing", "lat": 47.6062, "lng": -122.3321, "country": "USA", "industry": "Aerospace", "annual_spend": 7200000, "tier": 1},
]

DEMO_NEWS = [
    {"title": "Magna International Reports Record Q3 Profits", "summary": "Exceeds expectations, supply chain strong.", "risk": "legitimate"},
    {"title": "BREAKING: Major Fire at TSMC Fab in Taiwan", "summary": "Production halted, global chip shortage worsens.", "risk": "supplier"},
    {"title": "Toyota Plant Strike Halts Production", "summary": "5000 workers walk out demanding higher wages.", "risk": "labor"},
    {"title": "US Imposes New Tariffs on Chinese Semiconductors", "summary": "25% tariff hike, supply chains scramble.", "risk": "geopolitical"},
    {"title": "DHL Announces $2B Green Logistics Investment", "summary": "Expansion of electric fleet in Europe.", "risk": "legitimate"},
    {"title": "Hurricane Disrupts Gulf Coast Shipping Lanes", "summary": "Major ports closed, delays expected.", "risk": "weather"},
    {"title": "Fake News: Samsung Battery Plant Explosion", "summary": "Company denies rumors, stock recovers.", "risk": "financial"},
    {"title": "Boeing Supplier Quality Issues Delay Deliveries", "summary": "Fuselage defects found, timeline pushed back.", "risk": "supplier"},
]

RISK_WEIGHTS = {
    "financial": 0.9,
    "supplier": 0.8,
    "labor": 0.7,
    "geopolitical": 0.75,
    "weather": 0.6,
    "legitimate": 0.1,
}

# -------- SESSION STATE --------
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.articles = pd.DataFrame()
    st.session_state.risk_data = pd.DataFrame()
    st.session_state.news_loaded = False

# -------- SIDEBAR --------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/security-checked--v1.png", width=60)
    st.title("🛡️ Defender")
    
    if st.button("📰 Load Demo News", use_container_width=True):
        articles = []
        for item in DEMO_NEWS:
            articles.append({
                "id": hashlib.md5(item["title"].encode()).hexdigest()[:8],
                "title": item["title"],
                "summary": item["summary"],
                "link": "#",
                "published": datetime.now().isoformat(),
                "source": "Demo Feed",
                "risk_categories": [item["risk"]]
            })
        st.session_state.articles = pd.DataFrame(articles)
        st.session_state.news_loaded = True
        st.success(f"✅ Loaded {len(articles)} articles")
        st.rerun()
    
    if st.button("⚙️ Run Risk Analysis", use_container_width=True):
        if not st.session_state.news_loaded:
            st.warning("Load news first!")
        else:
            # Build supplier risk scores
            supplier_df = pd.DataFrame(SUPPLIERS)
            risk_scores = []
            
            for _, supplier in supplier_df.iterrows():
                base_risk = random.uniform(0.1, 0.3)  # baseline
                
                # Check articles mentioning this supplier
                for _, article in st.session_state.articles.iterrows():
                    if supplier["name"].lower() in article["title"].lower():
                        for cat in article["risk_categories"]:
                            base_risk = max(base_risk, RISK_WEIGHTS.get(cat, 0.5) * random.uniform(0.8, 1.2))
                
                final_risk = min(base_risk, 1.0)
                exposure = supplier["annual_spend"] * final_risk
                
                risk_scores.append({
                    "name": supplier["name"],
                    "country": supplier["country"],
                    "industry": supplier["industry"],
                    "tier": supplier["tier"],
                    "risk_score": round(final_risk, 3),
                    "exposure_at_risk": round(exposure, 0),
                    "latitude": supplier["lat"],
                    "longitude": supplier["lng"],
                })
            
            st.session_state.risk_data = pd.DataFrame(risk_scores)
            st.success("✅ Analysis complete!")
            st.balloons()
            st.rerun()
    
    st.divider()
    if st.button("📥 Download CSV Report", use_container_width=True):
        if not st.session_state.risk_data.empty:
            csv = st.session_state.risk_data.to_csv(index=False)
            st.download_button(
                label="⬇️ Click to Download CSV",
                data=csv,
                file_name=f"supply_chain_risk_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.warning("Run analysis first")

# -------- MAIN DASHBOARD --------
st.title("🛡️ Supply Chain Defender")
st.caption("Real‑time Risk Intelligence – Zero external dependencies")

if not st.session_state.risk_data.empty:
    df = st.session_state.risk_data
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Suppliers Monitored", len(df))
    col2.metric("Average Risk", f"{df['risk_score'].mean():.1%}")
    col3.metric("Total Exposure", f"${df['exposure_at_risk'].sum()/1e6:.1f}M")
    
    tab1, tab2 = st.tabs(["📊 Supplier Risk Table", "🌍 Global Heatmap"])
    
    with tab1:
        st.dataframe(
            df.sort_values("risk_score", ascending=False),
            use_container_width=True,
            column_config={
                "risk_score": st.column_config.ProgressColumn("Risk", format="%.1f%%", min_value=0, max_value=1),
                "exposure_at_risk": st.column_config.NumberColumn("Exposure ($)", format="$%.0f"),
            }
        )
    
    with tab2:
        fig = px.scatter_mapbox(
            df,
            lat="latitude",
            lon="longitude",
            size="exposure_at_risk",
            color="risk_score",
            hover_name="name",
            color_continuous_scale="RdYlGn_r",
            size_max=60,
            zoom=1,
            height=550,
        )
        fig.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    # Show the news that triggered risks
    with st.expander("📰 News Alerts Used for Analysis"):
        if st.session_state.news_loaded:
            st.dataframe(st.session_state.articles[["title", "summary", "source"]])
        else:
            st.info("Load news first")
else:
    st.info("👈 Start by clicking **Load Demo News** then **Run Risk Analysis**")

st.divider()
st.caption("Built for Supply Chain Resilience – No external dependencies, runs anywhere.")
