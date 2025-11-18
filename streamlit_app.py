"""
PCA Agent - Integrated Analytics Dashboard
Streamlined interface with auto-insights and visualizations
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="PCA Agent - Campaign Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .insight-card {
        background: #f8f9fa;
        padding: 1rem;
        border-left: 4px solid #667eea;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None
if 'df' not in st.session_state:
    st.session_state.df = None

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/667eea/ffffff?text=PCA+Agent", use_container_width=True)
    st.markdown("---")
    
    st.markdown("### 🎯 Capabilities")
    st.markdown("""
    - 📊 **Auto-Insights**: AI-powered analysis
    - 📈 **Visualizations**: Interactive charts
    - 💬 **Natural Language Q&A**: Ask anything
    - 💰 **ROAS Analysis**: Revenue optimization
    - 🎯 **Funnel Analysis**: Conversion optimization
    - 👥 **Audience Insights**: Targeting recommendations
    - 🚀 **Tactical Recommendations**: Actionable steps
    """)
    
    st.markdown("---")
    st.markdown("### 📱 Supported Platforms")
    platforms = ["Google Ads", "Meta Ads", "LinkedIn Ads", "DV360", "CM360", "Snapchat Ads"]
    for platform in platforms:
        st.markdown(f"✓ {platform}")
    
    st.markdown("---")
    if st.button("🔄 Reset Analysis", use_container_width=True):
        st.session_state.analysis_complete = False
        st.session_state.analysis_data = None
        st.session_state.df = None
        st.rerun()

# Main header
st.markdown('<h1 class="main-header">📊 Campaign Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown("**AI-Powered Multi-Platform Campaign Analysis with Auto-Insights & Visualizations**")
st.markdown("---")

# Main tabs
tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard", "💬 Ask Questions", "📖 Documentation"])

with tab1:
    # Upload Section
    if not st.session_state.analysis_complete:
        st.markdown("## 📤 Upload Your Data")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            input_method = st.radio(
                "Choose Input Method",
                options=["📊 CSV Data Files", "📸 Dashboard Screenshots"],
                horizontal=True,
                help="Upload CSV for instant analysis or screenshots for vision-based extraction"
            )
        
        with col2:
            st.info("💡 **Tip**: CSV files provide instant analysis!")
        
        st.markdown("---")
        
        if input_method == "📊 CSV Data Files":
            st.markdown("### Upload Campaign Data CSV")
            
            # Download sample
            sample_csv = """Campaign_Name,Platform,Date,Impressions,Clicks,CTR,Conversions,Spend,CPC,CPA,ROAS,Reach,Frequency
Q4_Holiday_2024,google_ads,2024-10-01,1250000,25000,2.0,850,45000,1.80,52.94,4.2,980000,1.28
Q4_Holiday_2024,meta_ads,2024-10-01,980000,18500,1.89,620,32000,1.73,51.61,3.8,750000,1.31
Black_Friday_2024,google_ads,2024-11-24,2500000,50000,2.0,1800,85000,1.70,47.22,5.1,2000000,1.25"""
            
            st.download_button(
                label="📥 Download Sample CSV Template",
                data=sample_csv,
                file_name="sample_campaign_data.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            uploaded_file = st.file_uploader(
                "Upload your campaign CSV file",
                type=["csv"],
                help="Upload CSV with campaign metrics (Campaign_Name, Platform, Spend, ROAS, etc.)"
            )
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.session_state.df = df
                    
                    st.success(f"✅ Loaded {len(df)} rows with {len(df.columns)} columns")
                    
                    # Quick preview
                    with st.expander("📋 Data Preview", expanded=True):
                        st.dataframe(df.head(10), use_container_width=True)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Rows", len(df))
                        with col2:
                            campaigns = df['Campaign_Name'].nunique() if 'Campaign_Name' in df.columns else 0
                            st.metric("Campaigns", campaigns)
                        with col3:
                            platforms = df['Platform'].nunique() if 'Platform' in df.columns else 0
                            st.metric("Platforms", platforms)
                        with col4:
                            spend = df['Spend'].sum() if 'Spend' in df.columns else 0
                            st.metric("Total Spend", f"${spend:,.0f}")
                    
                    # Analyze button
                    st.markdown("---")
                    if st.button("🚀 **Analyze Data & Generate Insights**", type="primary", use_container_width=True):
                        with st.spinner("🤖 AI Expert analyzing your data... This may take 30-60 seconds..."):
                            try:
                                from src.analytics import MediaAnalyticsExpert
                                
                                # Check which LLM to use
                                use_anthropic = os.getenv('USE_ANTHROPIC', 'false').lower() == 'true'
                                
                                if use_anthropic:
                                    api_key = os.getenv('ANTHROPIC_API_KEY')
                                    if not api_key or api_key == 'your_anthropic_api_key_here':
                                        st.error("❌ Anthropic API key not found. Set ANTHROPIC_API_KEY in .env file.")
                                        st.info("💡 Get your key at: https://console.anthropic.com/")
                                    else:
                                        # Run analysis with Claude
                                        expert = MediaAnalyticsExpert()
                                        analysis = expert.analyze_all(df)
                                        
                                        st.session_state.analysis_data = analysis
                                        st.session_state.analysis_complete = True
                                        st.rerun()
                                else:
                                    api_key = os.getenv('OPENAI_API_KEY')
                                    if not api_key or api_key == 'your_openai_api_key_here':
                                        st.error("❌ OpenAI API key not found. Set OPENAI_API_KEY in .env file.")
                                        st.info("💡 Get your key at: https://platform.openai.com/api-keys")
                                    else:
                                        # Run analysis with OpenAI
                                        expert = MediaAnalyticsExpert()
                                        analysis = expert.analyze_all(df)
                                        
                                        st.session_state.analysis_data = analysis
                                        st.session_state.analysis_complete = True
                                        st.rerun()
                            
                            except Exception as e:
                                st.error(f"❌ Error during analysis: {str(e)}")
                                import traceback
                                with st.expander("Error Details"):
                                    st.code(traceback.format_exc())
                
                except Exception as e:
                    st.error(f"❌ Error loading CSV: {str(e)}")
        
        else:  # Screenshots
            st.markdown("### Upload Dashboard Screenshots")
            st.info("📸 **Screenshot Mode**: Upload PNG, JPG, or PDF files of your campaign dashboards")
            
            uploaded_files = st.file_uploader(
                "Choose screenshot files",
                type=["png", "jpg", "jpeg", "pdf"],
                accept_multiple_files=True,
                help="Upload dashboard screenshots from Google Ads, Meta, LinkedIn, etc."
            )
            
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} files uploaded")
                
                with st.expander("Preview Uploaded Files"):
                    cols = st.columns(3)
                    for i, file in enumerate(uploaded_files):
                        with cols[i % 3]:
                            st.image(file, caption=file.name, use_container_width=True)
                
                st.warning("⚠️ Screenshot analysis requires API backend. Use CSV mode for instant analysis.")
    
    # Analysis Results
    else:
        analysis = st.session_state.analysis_data
        df = st.session_state.df
        
        # Executive Summary
        st.markdown("## 📊 Executive Summary")
        st.info(analysis['executive_summary'])
        
        st.markdown("---")
        
        # Management Overview
        st.markdown("## 📊 Management Overview")

        # Filters for management view (do not affect underlying analysis)
        filter_cols = st.columns(3)

        with filter_cols[0]:
            campaign_options = ["All Campaigns"]
            if 'Campaign_Name' in df.columns:
                campaign_options += sorted(df['Campaign_Name'].dropna().unique().tolist())
            selected_campaign = st.selectbox(
                "Campaign",
                options=campaign_options,
                index=0
            )

        with filter_cols[1]:
            platform_options = []
            if 'Platform' in df.columns:
                platform_options = sorted(df['Platform'].dropna().unique().tolist())
            selected_platforms = st.multiselect(
                "Platforms",
                options=platform_options,
                default=platform_options
            )

        with filter_cols[2]:
            date_range = None
            if 'Date' in df.columns:
                try:
                    df_dates = pd.to_datetime(df['Date'], errors='coerce')
                    min_date = df_dates.min()
                    max_date = df_dates.max()
                    if pd.notna(min_date) and pd.notna(max_date):
                        date_range = st.date_input(
                            "Date range",
                            value=(min_date.date(), max_date.date()) if min_date != max_date else (min_date.date(), max_date.date()),
                        )
                except Exception:
                    date_range = None

        # Build filtered dataframe for management metrics only
        df_mgmt = df.copy()
        if selected_campaign != "All Campaigns" and 'Campaign_Name' in df_mgmt.columns:
            df_mgmt = df_mgmt[df_mgmt['Campaign_Name'] == selected_campaign]
        if selected_platforms and 'Platform' in df_mgmt.columns:
            df_mgmt = df_mgmt[df_mgmt['Platform'].isin(selected_platforms)]
        if date_range and 'Date' in df_mgmt.columns:
            try:
                df_mgmt = df_mgmt.copy()
                df_mgmt['Date'] = pd.to_datetime(df_mgmt['Date'], errors='coerce')
                start_date, end_date = date_range
                df_mgmt = df_mgmt[(df_mgmt['Date'] >= pd.to_datetime(start_date)) & (df_mgmt['Date'] <= pd.to_datetime(end_date))]
            except Exception:
                pass

        # Compute high-level KPIs for management view
        total_spend_mgmt = df_mgmt['Spend'].sum() if 'Spend' in df_mgmt.columns else 0
        total_conversions_mgmt = df_mgmt['Conversions'].sum() if 'Conversions' in df_mgmt.columns else 0
        avg_roas_mgmt = df_mgmt['ROAS'].mean() if 'ROAS' in df_mgmt.columns and not df_mgmt['ROAS'].empty else 0
        avg_cpa_mgmt = df_mgmt['CPA'].mean() if 'CPA' in df_mgmt.columns and not df_mgmt['CPA'].empty else 0

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Mgmt: Total Spend", f"${total_spend_mgmt:,.0f}")
        with col_m2:
            st.metric("Mgmt: Total Conversions", f"{total_conversions_mgmt:,.0f}")
        with col_m3:
            st.metric("Mgmt: Avg ROAS", f"{avg_roas_mgmt:.2f}x")
        with col_m4:
            st.metric("Mgmt: Avg CPA", f"${avg_cpa_mgmt:.2f}")

        # Simple summary chart for management view
        if not df_mgmt.empty:
            st.markdown("### 📊 Management Summary Chart")
            if 'Date' in df_mgmt.columns:
                try:
                    df_mgmt_chart = df_mgmt.copy()
                    df_mgmt_chart['Date'] = pd.to_datetime(df_mgmt_chart['Date'], errors='coerce')
                    daily = df_mgmt_chart.groupby('Date').agg({
                        'Spend': 'sum',
                        'Conversions': 'sum'
                    }).reset_index()
                    daily = daily.sort_values('Date')
                    fig_mgmt = px.line(
                        daily,
                        x='Date',
                        y=['Spend', 'Conversions'],
                        title='Daily Spend and Conversions (Management View)'
                    )
                    st.plotly_chart(fig_mgmt, use_container_width=True)
                except Exception:
                    pass
            elif 'Campaign_Name' in df_mgmt.columns and 'Spend' in df_mgmt.columns:
                top_campaigns = df_mgmt.groupby('Campaign_Name')['Spend'].sum().reset_index().nlargest(10, 'Spend')
                fig_mgmt = px.bar(
                    top_campaigns,
                    x='Campaign_Name',
                    y='Spend',
                    title='Top Campaigns by Spend (Management View)',
                    color='Spend',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_mgmt, use_container_width=True)

        st.markdown("---")
        
        # Key Metrics
        st.markdown("## 📈 Key Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Spend",
                f"${analysis['metrics']['overview']['total_spend']:,.0f}",
                help="Total advertising spend across all campaigns"
            )
        with col2:
            st.metric(
                "Total Conversions",
                f"{analysis['metrics']['overview']['total_conversions']:,.0f}",
                help="Total conversions generated"
            )
        with col3:
            st.metric(
                "Average ROAS",
                f"{analysis['metrics']['overview']['avg_roas']:.2f}x",
                delta=f"{(analysis['metrics']['overview']['avg_roas'] - 3.0):.1f}x vs 3.0x target",
                help="Return on ad spend"
            )
        with col4:
            st.metric(
                "Average CPA",
                f"${analysis['metrics']['overview']['avg_cpa']:.2f}",
                help="Cost per acquisition"
            )
        
        st.markdown("---")
        
        # Visualizations
        st.markdown("## 📊 Performance Visualizations")
        
        viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs([
            "📈 Platform Performance",
            "🎯 Campaign Comparison",
            "💰 ROAS Analysis",
            "📉 Funnel Analysis"
        ])
        
        with viz_tab1:
            # Platform performance charts
            if 'Platform' in df.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Spend by platform
                    platform_spend = df.groupby('Platform')['Spend'].sum().reset_index()
                    fig = px.bar(
                        platform_spend,
                        x='Platform',
                        y='Spend',
                        title='Total Spend by Platform',
                        color='Spend',
                        color_continuous_scale='Blues'
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # ROAS by platform
                    platform_roas = df.groupby('Platform')['ROAS'].mean().reset_index()
                    fig = px.bar(
                        platform_roas,
                        x='Platform',
                        y='ROAS',
                        title='Average ROAS by Platform',
                        color='ROAS',
                        color_continuous_scale='Greens'
                    )
                    fig.add_hline(y=3.0, line_dash="dash", line_color="red", annotation_text="Target: 3.0x")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Platform metrics table
                st.markdown("### Platform Performance Summary")
                platform_metrics = df.groupby('Platform').agg({
                    'Spend': 'sum',
                    'Conversions': 'sum',
                    'ROAS': 'mean',
                    'CPA': 'mean',
                    'CTR': 'mean'
                }).round(2)
                st.dataframe(platform_metrics, use_container_width=True)
        
        with viz_tab2:
            # Campaign comparison
            if 'Campaign_Name' in df.columns:
                campaign_metrics = df.groupby('Campaign_Name').agg({
                    'Spend': 'sum',
                    'Conversions': 'sum',
                    'ROAS': 'mean'
                }).reset_index()
                
                # Bubble chart
                fig = px.scatter(
                    campaign_metrics,
                    x='Spend',
                    y='ROAS',
                    size='Conversions',
                    color='ROAS',
                    hover_name='Campaign_Name',
                    title='Campaign Performance: Spend vs ROAS (size = Conversions)',
                    color_continuous_scale='RdYlGn'
                )
                fig.add_hline(y=3.0, line_dash="dash", line_color="gray", annotation_text="Target ROAS")
                st.plotly_chart(fig, use_container_width=True)
                
                # Top campaigns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🏆 Top 5 Campaigns by ROAS")
                    top_roas = campaign_metrics.nlargest(5, 'ROAS')[['Campaign_Name', 'ROAS', 'Spend']]
                    st.dataframe(top_roas, use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown("### 💰 Top 5 Campaigns by Spend")
                    top_spend = campaign_metrics.nlargest(5, 'Spend')[['Campaign_Name', 'Spend', 'ROAS']]
                    st.dataframe(top_spend, use_container_width=True, hide_index=True)
        
        with viz_tab3:
            # ROAS analysis
            if analysis.get('roas_analysis'):
                roas_data = analysis['roas_analysis']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 💰 Revenue & Profit")
                    st.metric("Total Revenue", f"${roas_data['overall']['implied_revenue']:,.0f}")
                    st.metric("Total Profit", f"${roas_data['overall']['profit']:,.0f}")
                    st.metric("Profit Margin", f"{roas_data['overall']['profit_margin']:.1f}%")
                
                with col2:
                    # ROAS distribution
                    if 'ROAS' in df.columns:
                        fig = px.histogram(
                            df,
                            x='ROAS',
                            nbins=20,
                            title='ROAS Distribution',
                            color_discrete_sequence=['#667eea']
                        )
                        fig.add_vline(x=3.0, line_dash="dash", line_color="red", annotation_text="Target")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Efficiency tiers
                if roas_data.get('efficiency_tiers'):
                    st.markdown("### 🎯 Performance Tiers")
                    tiers = roas_data['efficiency_tiers']
                    
                    tier_df = pd.DataFrame({
                        'Tier': ['Excellent (4.5x+)', 'Good (3.5-4.5x)', 'Needs Improvement (<3.5x)'],
                        'Count': [tiers['excellent']['count'], tiers['good']['count'], tiers['needs_improvement']['count']],
                        'Spend': [tiers['excellent']['spend'], tiers['good']['spend'], tiers['needs_improvement']['spend']]
                    })
                    
                    fig = px.bar(
                        tier_df,
                        x='Tier',
                        y='Spend',
                        color='Tier',
                        title='Spend Distribution by Performance Tier',
                        color_discrete_map={
                            'Excellent (4.5x+)': '#10b981',
                            'Good (3.5-4.5x)': '#f59e0b',
                            'Needs Improvement (<3.5x)': '#ef4444'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with viz_tab4:
            # Funnel analysis
            if analysis.get('funnel_analysis') and analysis['funnel_analysis'].get('stages'):
                funnel_data = analysis['funnel_analysis']
                
                # Funnel visualization
                stages = funnel_data['stages']
                funnel_df = pd.DataFrame({
                    'Stage': ['Awareness', 'Consideration', 'Conversion'],
                    'Value': [
                        stages['awareness']['value'],
                        stages['consideration']['value'],
                        stages['conversion']['value']
                    ],
                    'Percentage': [
                        stages['awareness']['percentage'],
                        stages['consideration']['percentage'],
                        stages['conversion']['percentage']
                    ]
                })
                
                fig = go.Figure(go.Funnel(
                    y=funnel_df['Stage'],
                    x=funnel_df['Value'],
                    textinfo="value+percent initial",
                    marker=dict(color=['#667eea', '#764ba2', '#f093fb'])
                ))
                fig.update_layout(title='Marketing Funnel Performance')
                st.plotly_chart(fig, use_container_width=True)
                
                # Conversion rates
                st.markdown("### 📊 Conversion Rates")
                col1, col2, col3 = st.columns(3)
                
                conv_rates = funnel_data['conversion_rates']
                with col1:
                    st.metric("Awareness → Consideration", f"{conv_rates['awareness_to_consideration']:.2f}%")
                with col2:
                    st.metric("Consideration → Conversion", f"{conv_rates['consideration_to_conversion']:.2f}%")
                with col3:
                    st.metric("Overall Conversion", f"{conv_rates['awareness_to_conversion']:.2f}%")
                
                # Drop-off points
                if funnel_data.get('drop_off_points'):
                    st.markdown("### ⚠️ Drop-off Points")
                    for drop_off in funnel_data['drop_off_points']:
                        st.warning(f"**{drop_off['stage']}**: {drop_off['issue']}")
                        st.info(f"💡 {drop_off['recommendation']}")
        
        st.markdown("---")
        
        # AI Insights
        st.markdown("## 💡 AI-Generated Insights")
        
        insight_cols = st.columns(2)
        for i, insight in enumerate(analysis['insights']):
            with insight_cols[i % 2]:
                impact_emoji = "🔴" if insight['impact'] == "High" else "🟡" if insight['impact'] == "Medium" else "🟢"
                with st.expander(f"{impact_emoji} {insight['category']}: {insight['insight'][:50]}..."):
                    st.markdown(f"**{insight['insight']}**")
                    st.write(insight['explanation'])
                    st.caption(f"Impact: {insight['impact']}")
        
        st.markdown("---")
        
        # Recommendations
        st.markdown("## 🎯 Strategic Recommendations")
        
        for i, rec in enumerate(analysis['recommendations'], 1):
            priority_color = "🔴" if rec['priority'] == "Critical" else "🟠" if rec['priority'] == "High" else "🟡"
            
            with st.expander(f"{priority_color} #{i}: {rec['recommendation'][:60]}...", expanded=i<=3):
                st.markdown(f"### {rec['recommendation']}")
                st.markdown(f"**Expected Impact:** {rec['expected_impact']}")
                st.markdown(f"**Implementation:** {rec['implementation']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Priority", rec['priority'])
                with col2:
                    st.metric("Timeline", rec['timeline'])
                with col3:
                    st.metric("Estimated ROI", rec['estimated_roi'])
        
        st.markdown("---")
        
        # Download report
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            # Convert Period objects in dictionary keys to strings
            def convert_periods(obj):
                """Recursively convert Period objects to strings in nested structures"""
                if isinstance(obj, dict):
                    return {str(k): convert_periods(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_periods(item) for item in obj]
                elif hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                elif hasattr(obj, '__str__') and type(obj).__name__ == 'Period':
                    return str(obj)
                else:
                    return obj
            
            # Convert the analysis data
            analysis_clean = convert_periods(analysis)
            
            # Custom JSON serializer for remaining objects
            def json_serializer(obj):
                """Custom JSON serializer for objects not serializable by default"""
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                elif hasattr(obj, '__str__'):
                    return str(obj)
                return obj
            
            report_json = json.dumps(analysis_clean, indent=2, default=json_serializer)
            st.download_button(
                label="📥 Download Full Analysis Report (JSON)",
                data=report_json,
                file_name=f"campaign_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

with tab2:
    st.markdown("## 💬 Ask Questions About Your Data")
    
    if st.session_state.df is not None:
        df = st.session_state.df
        
        # Query mode
        query_mode = st.radio(
            "Choose query mode:",
            options=["🤖 Natural Language (AI-powered)", "📝 Direct SQL Query"],
            horizontal=True
        )
        
        if query_mode == "🤖 Natural Language (AI-powered)":
            st.markdown("**Ask any question about your data in plain English:**")
            
            # Suggested questions
            with st.expander("💡 Suggested Questions", expanded=True):
                st.markdown("**Temporal Comparisons:**")
                temporal_questions = [
                    "Compare campaign performance between the last 2 weeks vs. the previous 2 weeks",
                    "Show me the week-over-week trend for conversions over the last 2 months",
                    "How did our CTR in the last month compare to the month before?",
                ]
                for q in temporal_questions:
                    if st.button(q, key=f"suggested_{hash(q)}", use_container_width=True):
                        st.session_state.current_question = q
                
                st.markdown("**Channel & Performance:**")
                channel_questions = [
                    "Which marketing channel generated the highest ROI?",
                    "Compare the cost per acquisition (CPA) across different channels",
                    "Which platform performs best in terms of ROAS?",
                ]
                for q in channel_questions:
                    if st.button(q, key=f"suggested_{hash(q)}", use_container_width=True):
                        st.session_state.current_question = q
                
                st.markdown("**Funnel & Conversion:**")
                funnel_questions = [
                    "What was the conversion rate at each stage: impressions to clicks to conversions?",
                    "Calculate the click-through rate and conversion rate for each platform",
                ]
                for q in funnel_questions:
                    if st.button(q, key=f"suggested_{hash(q)}", use_container_width=True):
                        st.session_state.current_question = q
                
                st.markdown("**Strategic Insights:**")
                strategic_questions = [
                    "Identify performance anomalies in the last 2 months using statistical outliers",
                    "Identify top 20% of campaigns driving 80% of results (Pareto analysis)",
                    "Calculate performance volatility (CPA standard deviation) for each campaign",
                    "If we increased budget by 25%, which channels should receive it based on ROAS?",
                ]
                for q in strategic_questions:
                    if st.button(q, key=f"suggested_{hash(q)}", use_container_width=True):
                        st.session_state.current_question = q
            
            question = st.text_input(
                "Your question:",
                value=st.session_state.get('current_question', ''),
                placeholder="e.g., Which campaign had the best ROAS?"
            )
            
            if st.button("🔍 Get Answer", type="primary"):
                if question:
                    with st.spinner("🤔 Thinking..."):
                        try:
                            from src.query_engine import NaturalLanguageQueryEngine
                            
                            api_key = os.getenv('OPENAI_API_KEY')
                            if api_key:
                                engine = NaturalLanguageQueryEngine(api_key)
                                engine.load_data(df)
                                result = engine.ask(question)
                                
                                if result['success']:
                                    st.success("✅ Answer:")
                                    st.markdown(f"### {result['answer']}")
                                    
                                    with st.expander("🔧 Generated SQL Query"):
                                        st.code(result['sql_query'], language="sql")
                                    
                                    with st.expander("📊 Detailed Results"):
                                        st.dataframe(result['results'], use_container_width=True)
                                else:
                                    st.error(f"❌ Error: {result['error']}")
                            else:
                                st.warning("⚠️ OpenAI API key not found.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        
        else:
            st.markdown("**Write your SQL query:**")
            st.info("💡 Table name: `campaigns`")
            
            sql_query = st.text_area(
                "SQL Query:",
                height=150,
                placeholder="SELECT * FROM campaigns WHERE ROAS > 4.0 ORDER BY ROAS DESC LIMIT 10"
            )
            
            if st.button("▶️ Execute Query", type="primary"):
                if sql_query:
                    try:
                        import duckdb
                        conn = duckdb.connect(':memory:')
                        conn.register('campaigns', df)
                        result_df = conn.execute(sql_query).fetchdf()
                        conn.close()
                        
                        st.success(f"✅ Query executed! Returned {len(result_df)} rows.")
                        st.dataframe(result_df, use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ SQL Error: {e}")
    else:
        st.info("👆 Upload data in the Analytics Dashboard tab first!")

with tab3:
    st.markdown("## 📖 Documentation")
    
    st.markdown("""
    ### How to Use PCA Agent
    
    #### 1. Upload Your Data
    - **CSV Mode** (Recommended): Upload campaign data CSV for instant analysis
    - **Screenshot Mode**: Upload dashboard screenshots for vision-based extraction
    
    #### 2. Automatic Analysis
    - Click "Analyze Data & Generate Insights"
    - AI expert analyzes all campaigns
    - Generates insights, recommendations, and visualizations
    
    #### 3. Explore Results
    - **Executive Summary**: High-level overview
    - **Key Metrics**: Performance dashboard
    - **Visualizations**: Interactive charts
    - **AI Insights**: Data-driven insights
    - **Recommendations**: Actionable steps
    
    #### 4. Ask Questions
    - Use natural language or SQL
    - Get instant answers
    - Download results
    
    ### CSV Format
    
    Required columns:
    - `Campaign_Name`: Campaign identifier
    - `Platform`: google_ads, meta_ads, linkedin_ads, etc.
    - `Spend`: Total spend
    - `Conversions`: Total conversions
    - `ROAS`: Return on ad spend
    
    Optional columns:
    - `Date`, `Impressions`, `Clicks`, `CTR`, `CPA`, `CPC`, `CPM`, `Reach`, `Frequency`
    
    ### Supported Platforms
    - Google Ads
    - Meta Ads (Facebook/Instagram)
    - LinkedIn Ads
    - Display & Video 360 (DV360)
    - Campaign Manager 360 (CM360)
    - Snapchat Ads
    
    ### AI Capabilities
    - **Funnel Analysis**: Awareness → Consideration → Conversion
    - **ROAS Optimization**: Revenue and profit analysis
    - **Audience Insights**: Targeting recommendations
    - **Tactical Recommendations**: Bidding, creative, placement strategies
    - **Budget Optimization**: Reallocation recommendations
    - **Risk Assessment**: Identify underperformers
    
    ### Support
    For questions or issues, refer to the documentation files in the project directory.
    """)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666;">PCA Agent - AI-Powered Campaign Analytics | Built with Streamlit & OpenAI</div>',
    unsafe_allow_html=True
)
