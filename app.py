# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Import modules
from data_ingestion import NewsIngestionEngine
from classifier import SupplyChainRiskClassifier
from risk_analyzer import RiskAnalyzer
from weather_monitor import WeatherMonitor
from report_generator import ReportGenerator

# Page config
st.set_page_config(
    page_title="Supply Chain Defender",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.articles = pd.DataFrame()
    st.session_state.classifier_results = pd.DataFrame()
    st.session_state.risk_data = pd.DataFrame()
    st.session_state.weather_data = pd.DataFrame()
    st.session_state.news_engine = NewsIngestionEngine()
    st.session_state.classifier = SupplyChainRiskClassifier()
    st.session_state.classifier.load_or_train()
    st.session_state.risk_analyzer = RiskAnalyzer()
    st.session_state.weather_monitor = WeatherMonitor()
    st.session_state.report_generator = ReportGenerator()

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/security-checked--v1.png", width=60)
    st.title("🛡️ Supply Chain Defender")
    st.caption("Real-time Risk Intelligence Platform")
    st.divider()
    
    if st.button("🔄 Fetch Latest News", use_container_width=True):
        with st.spinner("Fetching news..."):
            st.session_state.articles = st.session_state.news_engine.fetch_news(max_articles=15)
            st.success(f"✅ Fetched {len(st.session_state.articles)} articles")
            time.sleep(0.5)
    
    if st.button("🧠 Run Risk Analysis", use_container_width=True):
        with st.spinner("Analyzing risks..."):
            if st.session_state.articles.empty:
                st.warning("Fetch news first!")
            else:
                st.session_state.classifier_results = st.session_state.classifier.analyze_articles(
                    st.session_state.articles
                )
                st.session_state.risk_data = st.session_state.risk_analyzer.calculate_supplier_risk(
                    st.session_state.articles,
                    st.session_state.classifier_results
                )
                
                # Get weather
                try:
                    suppliers_df = pd.read_csv('data/suppliers.csv')
                    weather_df = st.session_state.weather_monitor.get_suppliers_weather(suppliers_df)
                    if weather_df is not None and not weather_df.empty:
                        st.session_state.weather_data = weather_df
                except:
                    pass
                    
                st.success("✅ Analysis complete!")
                st.balloons()
    
    st.divider()
    st.subheader("🔍 Filters")
    risk_threshold = st.slider("Min Risk Score", 0.0, 1.0, 0.3, 0.05)
    
    st.divider()
    if st.button("📊 Generate PDF Report", use_container_width=True):
        if not st.session_state.risk_data.empty:
            with st.spinner("Generating..."):
                summary = st.session_state.risk_analyzer.get_risk_summary(st.session_state.risk_data)
                filename = st.session_state.report_generator.generate_risk_report(
                    st.session_state.risk_data, summary
                )
                if filename:
                    st.success("✅ Report ready!")
                    with open(filename, "rb") as f:
                        st.download_button(
                            label="📥 Download",
                            data=f,
                            file_name=filename,
                            mime="application/pdf"
                        )
        else:
            st.warning("Run risk analysis first!")

# Main content
st.title("🛡️ Supply Chain Defender Dashboard")
st.caption(f"Updated: {datetime.now().strftime('%H:%M')}")

if not st.session_state.risk_data.empty:
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Suppliers", len(st.session_state.risk_data))
    with col2:
        st.metric("Avg Risk", f"{st.session_state.risk_data['risk_score'].mean():.1%}")
    with col3:
        high = len(st.session_state.risk_data[st.session_state.risk_data['risk_score'] >= 0.6])
        st.metric("High Risk", high, delta="⚠️" if high > 0 else "✅")
    with col4:
        exposure = st.session_state.risk_data['exposure_at_risk_usd'].sum()
        st.metric("Total Exposure", f"${exposure/1e6:.1f}M")
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Risk Dashboard", "🌍 Heatmap", "📡 News"])
    
    with tab1:
        filtered = st.session_state.risk_data[st.session_state.risk_data['risk_score'] >= risk_threshold]
        if not filtered.empty:
            st.dataframe(
                filtered[['name', 'country', 'industry', 'tier', 'risk_score', 'exposure_at_risk_usd']]
                .sort_values('risk_score', ascending=False),
                use_container_width=True,
                column_config={
                    'risk_score': st.column_config.ProgressColumn("Risk", format="%.1f%%", min_value=0, max_value=1),
                    'exposure_at_risk_usd': st.column_config.NumberColumn("Exposure", format="$%.0f")
                }
            )
    
    with tab2:
        if not filtered.empty:
            fig = px.scatter_mapbox(
                filtered,
                lat="latitude",
                lon="longitude",
                size="exposure_at_risk_usd",
                color="risk_score",
                hover_name="name",
                color_continuous_scale="RdYlGn_r",
                size_max=50,
                zoom=1,
                height=500
            )
            fig.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        if not st.session_state.articles.empty:
            for _, row in st.session_state.articles.iterrows():
                with st.expander(f"📰 {row['title']}"):
                    st.caption(f"Source: {row.get('source', 'Unknown')}")
                    st.write(row.get('summary', ''))
                    st.caption(f"🔗 [{row.get('source', '')}]({row.get('link', '#')})")
else:
    st.info("👈 Click 'Fetch Latest News' then 'Run Risk Analysis'")
