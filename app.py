# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import os
import sys

# Fix for streamlit cloud - handle import errors gracefully
try:
    from data_ingestion import NewsIngestionEngine
    from classifier import SupplyChainRiskClassifier
    from risk_analyzer import RiskAnalyzer
    from weather_monitor import WeatherMonitor
    from report_generator import ReportGenerator
except ImportError as e:
    st.error(f"⚠️ Import Error: {e}")
    st.info("Please ensure all files are present in the repository")

# Page config
st.set_page_config(
    page_title="Supply Chain Defender",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state with proper error handling
if 'initialized' not in st.session_state:
    try:
        st.session_state.initialized = True
        st.session_state.articles = pd.DataFrame()
        st.session_state.classifier_results = pd.DataFrame()
        st.session_state.risk_data = pd.DataFrame()
        st.session_state.weather_data = pd.DataFrame()
        st.session_state.selected_supplier = None
        
        # Initialize components with error handling
        try:
            st.session_state.news_engine = NewsIngestionEngine()
        except Exception as e:
            st.warning(f"News engine init issue: {e}")
            st.session_state.news_engine = None
            
        try:
            st.session_state.classifier = SupplyChainRiskClassifier()
            st.session_state.classifier.load_or_train()
        except Exception as e:
            st.warning(f"Classifier init issue: {e}")
            st.session_state.classifier = None
            
        try:
            st.session_state.risk_analyzer = RiskAnalyzer()
        except Exception as e:
            st.warning(f"Risk analyzer init issue: {e}")
            st.session_state.risk_analyzer = None
            
        try:
            st.session_state.weather_monitor = WeatherMonitor()
        except Exception as e:
            st.warning(f"Weather monitor init issue: {e}")
            st.session_state.weather_monitor = None
            
        try:
            st.session_state.report_generator = ReportGenerator()
        except Exception as e:
            st.warning(f"Report generator init issue: {e}")
            st.session_state.report_generator = None
            
    except Exception as e:
        st.error(f"⚠️ Initialization Error: {e}")
        st.info("Please check your installation and try again")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/security-checked--v1.png", width=60)
    st.title("🛡️ Supply Chain Defender")
    st.caption("Real-time Risk Intelligence Platform")
    st.divider()
    
    # Section 1: Data Controls
    st.subheader("📡 Data Controls")
    
    if st.button("🔄 Fetch Latest News", use_container_width=True):
        with st.spinner("Fetching news from global sources..."):
            try:
                if st.session_state.news_engine:
                    st.session_state.articles = st.session_state.news_engine.fetch_news(max_articles=20)
                    st.success(f"✅ Fetched {len(st.session_state.articles)} articles")
                else:
                    st.warning("News engine not available, using demo data")
                    # Create demo data directly
                    demo_df = pd.DataFrame({
                        'id': [f'art_{i}' for i in range(5)],
                        'title': ['Demo Article 1', 'Demo Article 2', 'Demo Article 3', 'Demo Article 4', 'Demo Article 5'],
                        'summary': ['Supply chain risk detected', 'Supplier disruption warning', 'Logistics update', 'Trade policy change', 'Market analysis'],
                        'link': ['#']*5,
                        'published': [datetime.now().isoformat()]*5,
                        'source': ['Demo']*5,
                        'fetched_at': [datetime.now().isoformat()]*5,
                        'risk_categories': [['financial'], ['supplier'], ['legitimate'], ['compliance'], ['labor']]
                    })
                    st.session_state.articles = demo_df
                    st.success("✅ Using demo data")
            except Exception as e:
                st.error(f"Error fetching news: {e}")
                
            time.sleep(0.5)
    
    if st.button("🧠 Run Risk Analysis", use_container_width=True):
        with st.spinner("Analyzing articles for supply chain risks..."):
            try:
                if st.session_state.articles.empty:
                    st.warning("Please fetch news first!")
                elif st.session_state.classifier:
                    # Run classifier
                    st.session_state.classifier_results = st.session_state.classifier.analyze_articles(
                        st.session_state.articles
                    )
                    
                    # Calculate supplier risks
                    if st.session_state.risk_analyzer and not st.session_state.classifier_results.empty:
                        st.session_state.risk_data = st.session_state.risk_analyzer.calculate_supplier_risk(
                            st.session_state.articles,
                            st.session_state.classifier_results
                        )
                        
                        # Get weather data
                        if st.session_state.weather_monitor:
                            try:
                                suppliers_df = pd.read_csv('data/suppliers.csv')
                                weather_df = st.session_state.weather_monitor.get_suppliers_weather(suppliers_df)
                                if weather_df is not None and not weather_df.empty:
                                    st.session_state.weather_data = weather_df
                            except Exception as e:
                                print(f"Weather error: {e}")
                                
                        st.success("✅ Risk analysis complete!")
                        st.balloons()
                    else:
                        st.warning("Risk analyzer not available")
                else:
                    st.warning("Classifier not available")
            except Exception as e:
                st.error(f"Error during analysis: {e}")
    
    # Section 2: Filter Controls
    st.divider()
    st.subheader("🔍 Filters")
    
    risk_threshold = st.slider("Minimum Risk Score", 0.0, 1.0, 0.3, 0.05)
    
    # Section 3: Export
    st.divider()
    st.subheader("📄 Export")
    
    if st.button("📊 Generate PDF Report", use_container_width=True):
        if not st.session_state.risk_data.empty and st.session_state.report_generator:
            with st.spinner("Generating report..."):
                try:
                    summary = st.session_state.risk_analyzer.get_risk_summary(st.session_state.risk_data)
                    filename = st.session_state.report_generator.generate_risk_report(
                        st.session_state.risk_data,
                        summary
                    )
                    st.success(f"✅ Report saved: {filename}")
                    
                    with open(filename, "rb") as f:
                        st.download_button(
                            label="📥 Download Report",
                            data=f,
                            file_name=filename,
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"Error generating report: {e}")
        else:
            st.warning("Run risk analysis first!")

# Main content
st.title("🛡️ Supply Chain Defender Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Show metrics if data available
if not st.session_state.risk_data.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Suppliers Monitored", len(st.session_state.risk_data))
    with col2:
        avg_risk = st.session_state.risk_data['risk_score'].mean()
        st.metric("Avg Risk Score", f"{avg_risk:.1%}")
    with col3:
        high_risk = len(st.session_state.risk_data[st.session_state.risk_data['risk_score'] >= 0.6])
        st.metric("High Risk Suppliers", high_risk, delta="⚠️" if high_risk > 0 else "✅")
    with col4:
        total_exposure = st.session_state.risk_data['exposure_at_risk_usd'].sum()
        st.metric("Total Exposure", f"${total_exposure/1e6:.1f}M")
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Risk Dashboard", "🌍 Global Heatmap", "📡 News Feed"])
    
    # Tab 1: Risk Dashboard
    with tab1:
        st.subheader("Supplier Risk Rankings")
        
        filtered_data = st.session_state.risk_data.copy()
        filtered_data = filtered_data[filtered_data['risk_score'] >= risk_threshold]
        
        if not filtered_data.empty:
            display_cols = ['name', 'country', 'industry', 'tier', 'risk_score', 'exposure_at_risk_usd']
            st.dataframe(
                filtered_data[display_cols].sort_values('risk_score', ascending=False),
                use_container_width=True,
                column_config={
                    'risk_score': st.column_config.ProgressColumn("Risk", format="%.1f%%", min_value=0, max_value=1),
                    'exposure_at_risk_usd': st.column_config.NumberColumn("Exposure", format="$%.0f")
                }
            )
        else:
            st.info("No suppliers match the current filters")
    
    # Tab 2: Global Heatmap
    with tab2:
        st.subheader("🌍 Supplier Risk Global Heatmap")
        
        if not filtered_data.empty:
            fig = px.scatter_mapbox(
                filtered_data,
                lat="latitude",
                lon="longitude",
                size="exposure_at_risk_usd",
                color="risk_score",
                hover_name="name",
                hover_data={
                    'country': True,
                    'industry': True,
                    'risk_score': ':.1%',
                    'exposure_at_risk_usd': '$,.0f'
                },
                color_continuous_scale="RdYlGn_r",
                size_max=50,
                zoom=1,
                height=500
            )
            
            fig.update_layout(
                mapbox_style="open-street-map",
                margin={"r":0,"t":0,"l":0,"b":0}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for heatmap")
    
    # Tab 3: News Feed
    with tab3:
        st.subheader("📡 News Feed")
        
        if not st.session_state.articles.empty:
            for idx, row in st.session_state.articles.iterrows():
                with st.expander(f"📰 {row['title']}"):
                    st.caption(f"Source: {row.get('source', 'Unknown')}")
                    st.write(row.get('summary', 'No summary'))
                    st.caption(f"🔗 [Read more]({row.get('link', '#')})")
        else:
            st.info("No articles loaded")
else:
    # Empty state
    st.info("👈 Start by clicking 'Fetch Latest News' in the sidebar, then 'Run Risk Analysis'")

# Footer
st.divider()
st.caption("🛡️ Supply Chain Defender v1.0 | Built with Streamlit")
