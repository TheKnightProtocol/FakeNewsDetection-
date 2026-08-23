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
    st.session_state.selected_supplier = None
    st.session_state.news_engine = NewsIngestionEngine()
    st.session_state.classifier = SupplyChainRiskClassifier()
    st.session_state.risk_analyzer = RiskAnalyzer()
    st.session_state.weather_monitor = WeatherMonitor()
    st.session_state.report_generator = ReportGenerator()
    
    # Load classifier
    st.session_state.classifier.load_or_train()

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
            st.session_state.articles = st.session_state.news_engine.fetch_news(max_articles=30)
            st.success(f"✅ Fetched {len(st.session_state.articles)} articles")
            time.sleep(0.5)
    
    if st.button("🧠 Run Risk Analysis", use_container_width=True):
        with st.spinner("Analyzing articles for supply chain risks..."):
            if st.session_state.articles.empty:
                st.warning("Please fetch news first!")
            else:
                # Run classifier
                st.session_state.classifier_results = st.session_state.classifier.analyze_articles(
                    st.session_state.articles
                )
                
                # Calculate supplier risks
                st.session_state.risk_data = st.session_state.risk_analyzer.calculate_supplier_risk(
                    st.session_state.articles,
                    st.session_state.classifier_results
                )
                
                # Get weather data
                weather_df = st.session_state.weather_monitor.get_suppliers_weather(
                    pd.read_csv('data/suppliers.csv')
                )
                if weather_df is not None and not weather_df.empty:
                    st.session_state.weather_data = weather_df
                
                st.success("✅ Risk analysis complete!")
                st.balloons()
    
    # Section 2: Filter Controls
    st.divider()
    st.subheader("🔍 Filters")
    
    risk_threshold = st.slider("Minimum Risk Score", 0.0, 1.0, 0.3, 0.05)
    
    tier_filter = st.multiselect(
        "Supplier Tier",
        options=['All', '1', '2', '3'],
        default=['All']
    )
    
    industry_filter = st.multiselect(
        "Industry",
        options=['All', 'Semiconductor', 'Automotive', 'Pharmaceutical', 'Electronics', 
                 'Chemicals', 'Shipping', 'Logistics', 'Apparel', 'Aerospace', 'Aviation'],
        default=['All']
    )
    
    # Section 3: Export
    st.divider()
    st.subheader("📄 Export")
    
    if st.button("📊 Generate PDF Report", use_container_width=True):
        if not st.session_state.risk_data.empty:
            with st.spinner("Generating report..."):
                summary = st.session_state.risk_analyzer.get_risk_summary(st.session_state.risk_data)
                filename = st.session_state.report_generator.generate_risk_report(
                    st.session_state.risk_data,
                    summary
                )
                st.success(f"✅ Report saved: {filename}")
                
                # Offer download
                with open(filename, "rb") as f:
                    st.download_button(
                        label="📥 Download Report",
                        data=f,
                        file_name=filename,
                        mime="application/pdf"
                    )
        else:
            st.warning("Run risk analysis first!")

# Main content area
st.title("🛡️ Supply Chain Defender Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Top metrics
if not st.session_state.risk_data.empty:
    col1, col2, col3, col4, col5 = st.columns(5)
    
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
    with col5:
        flagged_articles = len(st.session_state.classifier_results)
        st.metric("Flagged Articles", flagged_articles)
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Risk Dashboard", 
        "🌍 Global Heatmap", 
        "📡 News Feed", 
        "🌦️ Weather Monitor", 
        "⚗️ Risk Simulator"
    ])
    
    # Tab 1: Risk Dashboard
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Supplier Risk Rankings")
            
            # Apply filters
            filtered_data = st.session_state.risk_data.copy()
            
            if 'All' not in tier_filter:
                filtered_data = filtered_data[filtered_data['tier'].astype(str).isin(tier_filter)]
            
            if 'All' not in industry_filter:
                filtered_data = filtered_data[filtered_data['industry'].isin(industry_filter)]
            
            filtered_data = filtered_data[filtered_data['risk_score'] >= risk_threshold]
            
            # Show table
            display_cols = ['name', 'country', 'industry', 'tier', 'risk_score', 'exposure_at_risk_usd']
            st.dataframe(
                filtered_data[display_cols].sort_values('risk_score', ascending=False),
                use_container_width=True,
                column_config={
                    'name': 'Supplier',
                    'risk_score': st.column_config.ProgressColumn("Risk", format="%.1f%%", min_value=0, max_value=1),
                    'exposure_at_risk_usd': st.column_config.NumberColumn("Exposure", format="$%.0f")
                }
            )
        
        with col2:
            st.subheader("Risk Distribution")
            fig = px.histogram(
                filtered_data, 
                x='risk_score',
                nbins=20,
                title="Risk Score Distribution",
                color_discrete_sequence=['#FF4B4B']
            )
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Industry Risk")
            industry_avg = filtered_data.groupby('industry')['risk_score'].mean().sort_values(ascending=False)
            fig = px.bar(
                x=industry_avg.values,
                y=industry_avg.index,
                orientation='h',
                title="Avg Risk by Industry",
                color=industry_avg.values,
                color_continuous_scale='Reds'
            )
            fig.update_layout(height=250, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Global Heatmap
    with tab2:
        st.subheader("🌍 Supplier Risk Global Heatmap")
        
        # Create map
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
                'tier': True,
                'risk_score': ':.1%',
                'exposure_at_risk_usd': '$,.0f'
            },
            color_continuous_scale="RdYlGn_r",
            size_max=60,
            zoom=1,
            height=600,
            title="Supplier Risk Heatmap"
        )
        
        fig.update_layout(
            mapbox_style="open-street-map",
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Click interaction - show supplier details
        st.subheader("🔍 Supplier Details")
        selected_supplier = st.selectbox(
            "Select a supplier to view details",
            options=filtered_data['name'].tolist()
        )
        
        if selected_supplier:
            supplier_data = filtered_data[filtered_data['name'] == selected_supplier].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Risk Score", f"{supplier_data['risk_score']:.1%}")
            with col2:
                st.metric("Annual Spend", f"${supplier_data['annual_spend_usd']:,.0f}")
            with col3:
                st.metric("Exposure", f"${supplier_data['exposure_at_risk_usd']:,.0f}")
            
            # Show alternative suppliers
            alternatives = st.session_state.risk_analyzer.find_alternatives(selected_supplier)
            if not alternatives.empty:
                st.info("💡 Alternative Suppliers Available")
                st.dataframe(alternatives)
            else:
                st.warning("No alternative suppliers found in database")
    
    # Tab 3: News Feed
    with tab3:
        st.subheader("📡 Real-time News Feed")
        
        # Search
        search_keyword = st.text_input("🔍 Search articles by keyword", placeholder="e.g., tariff, strike, bankruptcy")
        
        if not st.session_state.articles.empty:
            articles = st.session_state.articles.copy()
            if search_keyword:
                articles = st.session_state.news_engine.get_articles_by_keyword(articles, search_keyword)
            
            # Display articles
            for idx, row in articles.iterrows():
                with st.expander(f"📰 {row['title']} - {row.get('source', 'Unknown')}"):
                    st.caption(f"Published: {row.get('published', 'Unknown')}")
                    st.write(row.get('summary', 'No summary available'))
                    
                    # Show risk categories if analyzed
                    if not st.session_state.classifier_results.empty:
                        result = st.session_state.classifier_results[
                            st.session_state.classifier_results['article_id'] == row['id']
                        ]
                        if not result.empty:
                            risk_cat = result.iloc[0].get('category', 'Unknown')
                            risk_score = result.iloc[0].get('risk_score', 0)
                            st.metric("Risk Category", risk_cat, f"{risk_score:.1%}")
                    
                    st.caption(f"🔗 [Read Full Article]({row['link']})")
        else:
            st.info("No articles loaded. Click 'Fetch Latest News' in the sidebar.")
    
    # Tab 4: Weather Monitor
    with tab4:
        st.subheader("🌦️ Supplier Weather Monitor")
        
        if not st.session_state.weather_data.empty:
            # Merge weather with risk data
            weather_merged = st.session_state.weather_data.merge(
                filtered_data, 
                left_on='supplier_name',
                right_on='name',
                how='inner'
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Avg Temperature", f"{weather_merged['temperature'].mean():.1f}°C")
            with col2:
                st.metric("Avg Wind Speed", f"{weather_merged['wind_speed'].mean():.1f} km/h")
            
            # Weather risk table
            st.dataframe(
                weather_merged[['supplier_name', 'temperature', 'wind_speed', 'precipitation', 'weather_risk_score']],
                use_container_width=True,
                column_config={
                    'weather_risk_score': st.column_config.ProgressColumn("Weather Risk", format="%.1f%%", min_value=0, max_value=1)
                }
            )
            
            # Forecast for selected supplier
            selected = st.selectbox(
                "View forecast for supplier",
                options=weather_merged['supplier_name'].tolist()
            )
            
            if selected:
                supplier_row = filtered_data[filtered_data['name'] == selected].iloc[0]
                forecast = st.session_state.weather_monitor.get_weather_forecast(
                    supplier_row['latitude'],
                    supplier_row['longitude']
                )
                
                if forecast:
                    # Plot forecast
                    forecast_df = pd.DataFrame(forecast)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=forecast_df['time'][:24],
                        y=forecast_df['temperature'][:24],
                        name='Temperature',
                        line=dict(color='red')
                    ))
                    fig.add_trace(go.Scatter(
                        x=forecast_df['time'][:24],
                        y=forecast_df['wind_speed'][:24],
                        name='Wind Speed',
                        yaxis='y2',
                        line=dict(color='blue')
                    ))
                    fig.update_layout(
                        title=f"24-Hour Forecast for {selected}",
                        xaxis_title="Time",
                        yaxis_title="Temperature (°C)",
                        yaxis2=dict(
                            title="Wind Speed (km/h)",
                            overlaying='y',
                            side='right'
                        ),
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Weather data not available. Run risk analysis first.")
    
    # Tab 5: Risk Simulator
    with tab5:
        st.subheader("⚗️ Risk Scenario Simulator")
        
        scenario_type = st.selectbox(
            "Select scenario type",
            ["Region Disruption", "Port Strike", "Labor Dispute"]
        )
        
        if scenario_type == "Region Disruption":
            region = st.selectbox("Region", ["China", "USA", "Europe", "Southeast Asia"])
            disruption_level = st.slider("Disruption Severity", 0.0, 2.0, 1.2, 0.1)
            
            if st.button("Run Simulation"):
                # Simulate impact on suppliers in region
                simulated_risk = filtered_data.copy()
                region_map = {
                    'China': 'China',
                    'USA': 'USA',
                    'Europe': 'Germany|Denmark|France|UK',
                    'Southeast Asia': 'Taiwan|South Korea|Japan|Singapore'
                }
                
                mask = simulated_risk['country'].str.contains(region_map[region], case=False, na=False)
                simulated_risk.loc[mask, 'risk_score'] = simulated_risk.loc[mask, 'risk_score'] * disruption_level
                simulated_risk.loc[mask, 'risk_score'] = simulated_risk.loc[mask, 'risk_score'].clip(0, 1)
                
                # Show results
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Avg Risk (Before)", f"{filtered_data['risk_score'].mean():.1%}")
                    st.metric("Avg Risk (After)", f"{simulated_risk['risk_score'].mean():.1%}", 
                             delta=f"{(simulated_risk['risk_score'].mean() - filtered_data['risk_score'].mean())*100:.1f}%")
                with col2:
                    st.metric("Total Exposure (Before)", f"${filtered_data['exposure_at_risk_usd'].sum()/1e6:.1f}M")
                    st.metric("Total Exposure (After)", f"${simulated_risk['exposure_at_risk_usd'].sum()/1e6:.1f}M",
                             delta=f"${(simulated_risk['exposure_at_risk_usd'].sum() - filtered_data['exposure_at_risk_usd'].sum())/1e6:.1f}M")
        
        elif scenario_type == "Port Strike":
            port = st.selectbox("Major Port", ["Shanghai", "Rotterdam", "LA/LB", "Singapore"])
            duration_weeks = st.slider("Strike Duration (weeks)", 1, 8, 2)
            
            if st.button("Run Simulation"):
                st.warning(f"⚠️ Port strike in {port} for {duration_weeks} weeks would affect shipping suppliers")
                shipping_suppliers = filtered_data[filtered_data['industry'] == 'Shipping']
                impact_multiplier = 1 + (duration_weeks * 0.15)
                
                st.metric("Shipping Suppliers Affected", len(shipping_suppliers))
                st.metric("Average Impact Multiplier", f"{impact_multiplier:.1f}x")
                st.metric("Estimated Delay", f"{duration_weeks * 3} - {duration_weeks * 5} days")
        
        else:  # Labor Dispute
            industry = st.selectbox("Industry", ["Automotive", "Semiconductor", "Pharmaceutical"])
            disruption_days = st.slider("Disruption Length (days)", 3, 30, 10)
            
            if st.button("Run Simulation"):
                affected = filtered_data[filtered_data['industry'] == industry]
                st.metric("Suppliers Affected", len(affected))
                st.metric("Estimated Production Loss", f"${len(affected) * 500000 * (disruption_days/30):,.0f}")
                st.metric("Risk Increase", f"{min(disruption_days * 0.02, 0.5)*100:.1f}%")

else:
    # Empty state
    st.info("👈 Start by clicking 'Fetch Latest News' in the sidebar, then 'Run Risk Analysis'")
    
    # Show getting started guide
    with st.expander("📖 How to use Supply Chain Defender"):
        st.markdown("""
        **Step 1:** Click "Fetch Latest News" to ingest real-time news from global sources
        
        **Step 2:** Click "Run Risk Analysis" to analyze suppliers and calculate risk scores
        
        **Step 3:** Explore the tabs:
        - **Risk Dashboard:** View supplier rankings and industry risk
        - **Global Heatmap:** Visualize risk geographically
        - **News Feed:** Read flagged articles
        - **Weather Monitor:** Check weather impact on suppliers
        - **Risk Simulator:** Model disruption scenarios
        
        **Step 4:** Generate PDF reports for executives
        """)
