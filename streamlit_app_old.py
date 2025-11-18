"""
Streamlit Dashboard for PCA Agent - Demo Interface
"""
import streamlit as st
import requests
from datetime import date, timedelta
from pathlib import Path
import json
import pandas as pd
import io

# Page config
st.set_page_config(
    page_title="PCA Agent - Post Campaign Analysis",
    page_icon="📊",
    layout="wide"
)

# API endpoint
API_BASE_URL = "http://localhost:8000"

# Title
st.title("📊 Post Campaign Analysis Agent")
st.markdown("### AI-Powered Multi-Platform Campaign Analysis")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    **PCA Agent** uses Vision Language Models and Agentic AI to:
    - Extract data from dashboard screenshots OR CSV files
    - Analyze multi-platform campaigns
    - Generate insights and recommendations
    - Create automated PowerPoint reports
    
    **Input Methods:**
    - 📸 Dashboard Screenshots (PNG, JPG, PDF)
    - 📊 CSV Data Files (direct data input)
    
    **Supported Platforms:**
    - Google Ads
    - Campaign Manager 360
    - Display & Video 360
    - Meta Ads
    - Snapchat Ads
    - LinkedIn Ads
    """)

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📤 New Analysis", "💬 Ask Questions (SQL)", "📋 Campaigns", "📖 Documentation"])

with tab1:
    st.header("Create New Campaign Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        campaign_name = st.text_input(
            "Campaign Name",
            placeholder="Q4 2024 Holiday Campaign"
        )
        
        objectives = st.multiselect(
            "Campaign Objectives",
            options=["awareness", "consideration", "conversion", "engagement", "traffic", "lead_generation"],
            default=["awareness", "conversion"]
        )
    
    with col2:
        start_date = st.date_input(
            "Start Date",
            value=date.today() - timedelta(days=30)
        )
        
        end_date = st.date_input(
            "End Date",
            value=date.today()
        )
    
    st.markdown("---")
    
    # Input method selection
    input_method = st.radio(
        "Choose Input Method",
        options=["📸 Dashboard Screenshots", "📊 CSV Data Files"],
        horizontal=True
    )
    
    uploaded_files = None
    uploaded_csvs = None
    
    if input_method == "📸 Dashboard Screenshots":
        st.subheader("Upload Dashboard Snapshots")
        st.markdown("Upload screenshots from your advertising platforms (PNG, JPG, PDF)")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            type=["png", "jpg", "jpeg", "pdf"],
            accept_multiple_files=True,
            help="Upload dashboard screenshots from Google Ads, Meta Ads, LinkedIn, etc.",
            key="screenshot_uploader"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} files ready to upload")
            
            # Show preview
            with st.expander("Preview Uploaded Files"):
                cols = st.columns(3)
                for i, file in enumerate(uploaded_files):
                    with cols[i % 3]:
                        st.image(file, caption=file.name, use_container_width=True)
    
    else:  # CSV Data Files
        st.subheader("Upload Campaign Database (CSV)")
        st.markdown("""
        Upload CSV file(s) containing **ALL your campaign data**. The system will analyze:
        - ✅ **All campaigns** in the file
        - ✅ **All platforms** (Google Ads, Meta, LinkedIn, etc.)
        - ✅ **All time periods** (if date columns included)
        - ✅ **Cross-campaign insights** and patterns
        
        **CSV Format Options:**
        
        **Option 1: Multi-Campaign Database**
        ```
        Campaign_Name,Platform,Date,Impressions,Clicks,Conversions,Spend,ROAS
        Q4_Holiday,google_ads,2024-10-01,125000,2500,85,4500,4.2
        Q4_Holiday,meta_ads,2024-10-01,98000,1850,62,3200,3.8
        Black_Friday,google_ads,2024-11-01,250000,5000,180,8500,5.1
        Black_Friday,linkedin_ads,2024-11-01,45000,1200,38,1800,3.5
        ```
        
        **Option 2: Platform Summary**
        ```
        Platform,Total_Impressions,Total_Clicks,CTR,Conversions,Total_Spend,CPC,CPA,ROAS
        google_ads,1250000,25000,2.0,850,45000,1.80,52.94,4.2
        meta_ads,980000,18500,1.89,620,32000,1.73,51.61,3.8
        linkedin_ads,450000,12000,2.67,380,18000,1.50,47.37,3.5
        ```
        
        **The system will automatically:**
        - 📊 Detect all campaigns in your data
        - 🔍 Analyze each campaign individually
        - 📈 Compare performance across campaigns
        - 💡 Generate insights for the entire dataset
        - 📑 Create comprehensive report covering all campaigns
        """)
        
        # Download sample CSV template - FULL VERSION
        sample_csv = """Campaign_Name,Platform,Date,Impressions,Clicks,CTR,Conversions,Spend,CPC,CPA,ROAS,Reach,Frequency
Q4_Holiday_2024,google_ads,2024-10-01,1250000,25000,2.0,850,45000,1.80,52.94,4.2,980000,1.28
Q4_Holiday_2024,meta_ads,2024-10-01,980000,18500,1.89,620,32000,1.73,51.61,3.8,750000,1.31
Q4_Holiday_2024,linkedin_ads,2024-10-01,450000,12000,2.67,380,18000,1.50,47.37,3.5,380000,1.18
Q4_Holiday_2024,dv360,2024-10-01,2100000,31500,1.5,720,38000,1.21,52.78,3.2,1800000,1.17
Q4_Holiday_2024,snapchat_ads,2024-10-01,1500000,22500,1.5,450,28000,1.24,62.22,2.8,1200000,1.25
Q4_Holiday_2024,cm360,2024-10-01,1800000,27000,1.5,600,35000,1.30,58.33,3.0,1500000,1.20
Black_Friday_2024,google_ads,2024-11-24,2500000,50000,2.0,1800,85000,1.70,47.22,5.1,2000000,1.25
Black_Friday_2024,meta_ads,2024-11-24,1800000,35000,1.94,1200,62000,1.77,51.67,4.8,1400000,1.29
Black_Friday_2024,linkedin_ads,2024-11-24,680000,18500,2.72,620,28000,1.51,45.16,4.5,580000,1.17
Black_Friday_2024,snapchat_ads,2024-11-24,2200000,38000,1.73,850,42000,1.11,49.41,4.2,1800000,1.22
Cyber_Monday_2024,google_ads,2024-11-27,2800000,56000,2.0,2100,92000,1.64,43.81,5.5,2300000,1.22
Cyber_Monday_2024,meta_ads,2024-11-27,2100000,41000,1.95,1450,68000,1.66,46.90,5.2,1650000,1.27
Cyber_Monday_2024,linkedin_ads,2024-11-27,650000,18000,2.77,580,28000,1.56,48.28,4.2,550000,1.18
Cyber_Monday_2024,dv360,2024-11-27,3200000,48000,1.5,1100,58000,1.21,52.73,4.0,2800000,1.14
Back_To_School_2024,google_ads,2024-08-15,1800000,36000,2.0,1200,62000,1.72,51.67,4.5,1450000,1.24
Back_To_School_2024,meta_ads,2024-08-15,1350000,26000,1.93,850,42000,1.62,49.41,4.2,1050000,1.29
Back_To_School_2024,linkedin_ads,2024-08-15,520000,14500,2.79,480,22000,1.52,45.83,3.9,440000,1.18
Summer_Sale_2024,google_ads,2024-07-01,2200000,44000,2.0,1500,75000,1.70,50.00,4.8,1800000,1.22
Summer_Sale_2024,meta_ads,2024-07-01,1650000,32000,1.94,1050,52000,1.63,49.52,4.5,1300000,1.27
Summer_Sale_2024,snapchat_ads,2024-07-01,1900000,32000,1.68,720,38000,1.19,52.78,3.8,1550000,1.23
Spring_Launch_2024,google_ads,2024-03-15,1600000,32000,2.0,1100,58000,1.81,52.73,4.3,1300000,1.23
Spring_Launch_2024,meta_ads,2024-03-15,1200000,23000,1.92,750,38000,1.65,50.67,4.0,950000,1.26
Spring_Launch_2024,linkedin_ads,2024-03-15,480000,13500,2.81,450,20000,1.48,44.44,3.7,410000,1.17
Valentine_Day_2024,google_ads,2024-02-10,950000,19000,2.0,650,35000,1.84,53.85,4.1,780000,1.22
Valentine_Day_2024,meta_ads,2024-02-10,720000,14000,1.94,480,24000,1.71,50.00,3.9,580000,1.24
Valentine_Day_2024,snapchat_ads,2024-02-10,850000,14500,1.71,350,18000,1.24,51.43,3.2,700000,1.21
New_Year_2024,google_ads,2024-01-05,1100000,22000,2.0,750,40000,1.82,53.33,4.4,900000,1.22
New_Year_2024,meta_ads,2024-01-05,850000,16500,1.94,550,28000,1.70,50.91,4.1,680000,1.25
New_Year_2024,linkedin_ads,2024-01-05,420000,11500,2.74,380,17000,1.48,44.74,3.6,360000,1.17"""
        
        st.download_button(
            label="📥 Download Complete Multi-Campaign Database (8 Campaigns, 29 Rows)",
            data=sample_csv,
            file_name="sample_multi_campaign_database.csv",
            mime="text/csv",
            help="Download complete sample with 8 campaigns across full year 2024"
        )
        
        uploaded_csvs = st.file_uploader(
            "Choose CSV files",
            type=["csv"],
            accept_multiple_files=True,
            help="Upload CSV files with campaign metrics from different platforms",
            key="csv_uploader"
        )
        
        if uploaded_csvs:
            st.success(f"✅ {len(uploaded_csvs)} CSV files ready to analyze")
            
            # Show preview and analysis summary
            with st.expander("📊 Data Preview & Analysis Summary", expanded=True):
                total_campaigns = 0
                total_platforms = set()
                total_rows = 0
                
                for csv_file in uploaded_csvs:
                    st.markdown(f"### 📄 {csv_file.name}")
                    try:
                        df = pd.read_csv(csv_file)
                        total_rows += len(df)
                        
                        # Display data preview
                        st.dataframe(df.head(10), use_container_width=True)
                        if len(df) > 10:
                            st.caption(f"Showing first 10 of {len(df)} rows")
                        
                        # Detect campaigns
                        campaign_col = None
                        for col in df.columns:
                            if 'campaign' in col.lower() or 'name' in col.lower():
                                campaign_col = col
                                break
                        
                        if campaign_col:
                            unique_campaigns = df[campaign_col].nunique()
                            total_campaigns += unique_campaigns
                            st.success(f"🎯 **Detected {unique_campaigns} unique campaigns**")
                            campaign_list = df[campaign_col].unique()[:5]
                            st.write(f"Examples: {', '.join(map(str, campaign_list))}")
                            if len(df[campaign_col].unique()) > 5:
                                st.caption(f"... and {len(df[campaign_col].unique()) - 5} more")
                        
                        # Detect platforms
                        platform_col = None
                        for col in df.columns:
                            if 'platform' in col.lower() or 'channel' in col.lower():
                                platform_col = col
                                break
                        
                        if platform_col:
                            platforms = df[platform_col].unique()
                            total_platforms.update(platforms)
                            st.info(f"📱 **Platforms**: {', '.join(platforms)}")
                        
                        # Detect metrics
                        metric_keywords = ['impressions', 'clicks', 'ctr', 'conversions', 'spend', 
                                         'cpc', 'cpm', 'cpa', 'roas', 'reach', 'frequency', 
                                         'likes', 'shares', 'comments', 'views']
                        metrics_found = [col for col in df.columns 
                                       if any(keyword in col.lower() for keyword in metric_keywords)]
                        
                        if metrics_found:
                            st.info(f"📊 **Detected {len(metrics_found)} metrics**: {', '.join(metrics_found[:8])}")
                            if len(metrics_found) > 8:
                                st.caption(f"... and {len(metrics_found) - 8} more")
                        
                        # Detect date columns
                        date_col = None
                        for col in df.columns:
                            if 'date' in col.lower() or 'time' in col.lower() or 'period' in col.lower():
                                date_col = col
                                break
                        
                        if date_col:
                            try:
                                df[date_col] = pd.to_datetime(df[date_col])
                                date_range = f"{df[date_col].min().date()} to {df[date_col].max().date()}"
                                st.info(f"📅 **Date Range**: {date_range}")
                            except:
                                pass
                        
                        # Calculate totals
                        if 'spend' in [col.lower() for col in df.columns]:
                            spend_col = [col for col in df.columns if 'spend' in col.lower()][0]
                            total_spend = df[spend_col].sum()
                            st.metric("💰 Total Spend", f"${total_spend:,.2f}")
                        
                        if 'conversions' in [col.lower() for col in df.columns]:
                            conv_col = [col for col in df.columns if 'conversions' in col.lower()][0]
                            total_conversions = df[conv_col].sum()
                            st.metric("🎯 Total Conversions", f"{total_conversions:,.0f}")
                        
                        # Reset file pointer for later use
                        csv_file.seek(0)
                        
                    except Exception as e:
                        st.error(f"❌ Error reading {csv_file.name}: {str(e)}")
                    
                    st.markdown("---")
                
                # Overall summary
                if total_campaigns > 0 or total_platforms:
                    st.markdown("### 📈 Overall Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Campaigns", total_campaigns if total_campaigns > 0 else "N/A")
                    with col2:
                        st.metric("Total Platforms", len(total_platforms) if total_platforms else "N/A")
                    with col3:
                        st.metric("Total Data Rows", total_rows)
                    
                    st.success("✅ **Ready to analyze all campaigns in the dataset!**")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if input_method == "📊 CSV Data Files":
            analyze_button = st.button("🚀 Analyze All Campaigns", type="primary", use_container_width=True)
        else:
            analyze_button = st.button("🚀 Analyze Campaign", type="primary", use_container_width=True)
    
    with col2:
        if st.button("🔄 Reset", use_container_width=True):
            st.rerun()
    
    if analyze_button:
        if not campaign_name:
            st.error("❌ Please enter a campaign name")
        elif not objectives:
            st.error("❌ Please select at least one objective")
        elif not uploaded_files and not uploaded_csvs:
            st.error("❌ Please upload at least one file (screenshot or CSV)")
        else:
            # Handle CSV input - BULK ANALYSIS MODE
            if input_method == "📊 CSV Data Files" and uploaded_csvs:
                with st.spinner("🔄 Analyzing ALL campaigns in your database..."):
                    try:
                        st.info("📊 **BULK ANALYSIS MODE**: Processing entire campaign database from CSV files")
                        
                        # Parse and combine all CSV files
                        all_dataframes = []
                        total_campaigns_detected = 0
                        total_platforms_detected = set()
                        
                        for csv_file in uploaded_csvs:
                            df = pd.read_csv(csv_file)
                            all_dataframes.append(df)
                            
                            # Detect campaigns
                            campaign_col = next((col for col in df.columns if 'campaign' in col.lower() or 'name' in col.lower()), None)
                            if campaign_col:
                                total_campaigns_detected += df[campaign_col].nunique()
                            
                            # Detect platforms
                            platform_col = next((col for col in df.columns if 'platform' in col.lower() or 'channel' in col.lower()), None)
                            if platform_col:
                                total_platforms_detected.update(df[platform_col].unique())
                        
                        # Combine all data
                        combined_df = pd.concat(all_dataframes, ignore_index=True)
                        
                        # Display comprehensive analysis summary
                        st.success(f"✅ **Successfully processed {len(uploaded_csvs)} CSV file(s)**")
                        
                        # Analysis Overview
                        st.markdown("### 📊 Bulk Analysis Overview")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("📁 Files Processed", len(uploaded_csvs))
                        with col2:
                            st.metric("📝 Total Data Rows", len(combined_df))
                        with col3:
                            st.metric("🎯 Campaigns Found", total_campaigns_detected if total_campaigns_detected > 0 else "All Data")
                        with col4:
                            st.metric("📱 Platforms", len(total_platforms_detected) if total_platforms_detected else "Multiple")
                        
                        # Show detailed breakdown
                        with st.expander("📈 Detailed Analysis Breakdown", expanded=True):
                            # Campaign-level analysis
                            campaign_col = next((col for col in combined_df.columns if 'campaign' in col.lower() or 'name' in col.lower()), None)
                            
                            if campaign_col:
                                st.markdown("#### 🎯 Campaign-Level Analysis")
                                campaigns = combined_df[campaign_col].unique()
                                
                                for campaign in campaigns[:10]:  # Show first 10
                                    campaign_data = combined_df[combined_df[campaign_col] == campaign]
                                    
                                    # Calculate metrics for this campaign
                                    spend_col = next((col for col in campaign_data.columns if 'spend' in col.lower()), None)
                                    conv_col = next((col for col in campaign_data.columns if 'conversion' in col.lower()), None)
                                    
                                    col_a, col_b, col_c = st.columns([2, 1, 1])
                                    with col_a:
                                        st.write(f"**{campaign}**")
                                    with col_b:
                                        if spend_col:
                                            st.write(f"💰 ${campaign_data[spend_col].sum():,.0f}")
                                    with col_c:
                                        if conv_col:
                                            st.write(f"🎯 {campaign_data[conv_col].sum():,.0f} conv")
                                
                                if len(campaigns) > 10:
                                    st.caption(f"... and {len(campaigns) - 10} more campaigns")
                            
                            # Platform-level analysis
                            platform_col = next((col for col in combined_df.columns if 'platform' in col.lower() or 'channel' in col.lower()), None)
                            
                            if platform_col:
                                st.markdown("#### 📱 Platform Distribution")
                                platform_counts = combined_df[platform_col].value_counts()
                                for platform, count in platform_counts.items():
                                    st.write(f"• **{platform}**: {count} records")
                            
                            # Time period analysis
                            date_col = next((col for col in combined_df.columns if 'date' in col.lower() or 'period' in col.lower()), None)
                            
                            if date_col:
                                try:
                                    combined_df[date_col] = pd.to_datetime(combined_df[date_col])
                                    st.markdown("#### 📅 Time Period Coverage")
                                    st.write(f"From: **{combined_df[date_col].min().date()}**")
                                    st.write(f"To: **{combined_df[date_col].max().date()}**")
                                    st.write(f"Duration: **{(combined_df[date_col].max() - combined_df[date_col].min()).days} days**")
                                except:
                                    pass
                        
                        # Analysis capabilities
                        st.markdown("### 🤖 AI Analysis Will Include:")
                        st.markdown("""
                        - ✅ **Individual Campaign Performance**: Analyze each campaign separately
                        - ✅ **Cross-Campaign Comparison**: Compare performance across all campaigns
                        - ✅ **Platform Performance**: Analyze which platforms perform best
                        - ✅ **Time-Series Trends**: Identify patterns over time (if dates included)
                        - ✅ **Budget Efficiency**: Identify best and worst performing campaigns
                        - ✅ **Optimization Opportunities**: Recommend budget reallocation
                        - ✅ **Consolidated Report**: Single PowerPoint with all insights
                        """)
                        
                        # Show what will be generated
                        st.info(f"""
                        **📑 Report Generation (Bulk Mode)**
                        - Analysis Scope: **ALL {total_campaigns_detected if total_campaigns_detected > 0 else 'campaigns'}** in your database
                        - Report Type: **Consolidated Multi-Campaign Analysis**
                        - Platforms Covered: **{len(total_platforms_detected) if total_platforms_detected else 'All'}** platforms
                        - Data Points: **{len(combined_df)}** rows
                        
                        **The system will:**
                        1. Analyze each campaign individually
                        2. Compare performance across campaigns
                        3. Identify top and bottom performers
                        4. Generate cross-campaign insights
                        5. Create comprehensive PowerPoint report
                        """)
                        
                        st.success("✅ **Ready for bulk analysis!** The system will process ALL campaigns in your dataset.")
                        
                        # AUTO-ANALYSIS BUTTON
                        st.markdown("---")
                        if st.button("🧠 **Generate AI Insights & Recommendations**", type="primary", use_container_width=True):
                            with st.spinner("🤖 AI Expert analyzing your data... This may take 30-60 seconds..."):
                                try:
                                    import os
                                    from src.analytics import MediaAnalyticsExpert
                                    
                                    api_key = os.getenv('OPENAI_API_KEY')
                                    if not api_key:
                                        st.error("❌ OpenAI API key not found. Set OPENAI_API_KEY in .env file.")
                                    else:
                                        # Initialize analytics expert
                                        expert = MediaAnalyticsExpert(api_key)
                                        
                                        # Run automated analysis
                                        analysis = expert.analyze_all(combined_df)
                                        
                                        # Display Executive Summary
                                        st.markdown("## 📊 Executive Summary")
                                        st.info(analysis['executive_summary'])
                                        
                                        # Display Key Metrics
                                        st.markdown("## 📈 Key Metrics")
                                        col1, col2, col3, col4 = st.columns(4)
                                        with col1:
                                            st.metric("Total Spend", f"${analysis['metrics']['overview']['total_spend']:,.0f}")
                                        with col2:
                                            st.metric("Total Conversions", f"{analysis['metrics']['overview']['total_conversions']:,.0f}")
                                        with col3:
                                            st.metric("Average ROAS", f"{analysis['metrics']['overview']['avg_roas']:.2f}x")
                                        with col4:
                                            st.metric("Average CPA", f"${analysis['metrics']['overview']['avg_cpa']:.2f}")
                                        
                                        # Display Insights
                                        st.markdown("## 💡 Key Insights")
                                        for i, insight in enumerate(analysis['insights'], 1):
                                            with st.expander(f"🔍 Insight {i}: {insight['category']} - {insight['impact']} Impact"):
                                                st.markdown(f"**{insight['insight']}**")
                                                st.write(insight['explanation'])
                                        
                                        # Display Recommendations
                                        st.markdown("## 🎯 Strategic Recommendations")
                                        for i, rec in enumerate(analysis['recommendations'], 1):
                                            priority_emoji = "🔴" if rec['priority'] == "Critical" else "🟠" if rec['priority'] == "High" else "🟡"
                                            with st.expander(f"{priority_emoji} Recommendation {i}: {rec['priority']} Priority"):
                                                st.markdown(f"### {rec['recommendation']}")
                                                st.markdown(f"**Expected Impact:** {rec['expected_impact']}")
                                                st.markdown(f"**Implementation:** {rec['implementation']}")
                                                col_a, col_b = st.columns(2)
                                                with col_a:
                                                    st.metric("Timeline", rec['timeline'])
                                                with col_b:
                                                    st.metric("Estimated ROI", rec['estimated_roi'])
                                        
                                        # Display Opportunities
                                        if analysis['opportunities']:
                                            st.markdown("## 🚀 Growth Opportunities")
                                            for i, opp in enumerate(analysis['opportunities'], 1):
                                                with st.expander(f"💎 Opportunity {i}: {opp['type']}"):
                                                    for key, value in opp.items():
                                                        if key != 'type':
                                                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                                        
                                        # Display Risks
                                        if analysis['risks']:
                                            st.markdown("## ⚠️ Risk Assessment")
                                            for i, risk in enumerate(analysis['risks'], 1):
                                                severity_color = "🔴" if risk['severity'] == "High" else "🟠"
                                                with st.expander(f"{severity_color} Risk {i}: {risk['risk']} ({risk['severity']} Severity)"):
                                                    st.markdown(f"**Details:** {risk['details']}")
                                                    st.markdown(f"**Impact:** {risk['impact']}")
                                                    st.markdown(f"**Recommended Action:** {risk['action']}")
                                        
                                        # Display Budget Optimization
                                        if analysis['budget_optimization'].get('recommended_allocation'):
                                            st.markdown("## 💰 Budget Optimization")
                                            
                                            st.markdown("### Current vs Recommended Allocation")
                                            
                                            # Create comparison dataframe
                                            budget_data = []
                                            for platform in analysis['budget_optimization']['current_allocation'].keys():
                                                current = analysis['budget_optimization']['current_allocation'][platform]
                                                recommended = analysis['budget_optimization']['recommended_allocation'][platform]
                                                
                                                budget_data.append({
                                                    'Platform': platform,
                                                    'Current Spend': f"${current['spend']:,.0f}",
                                                    'Current %': f"{current['percentage']:.1f}%",
                                                    'Recommended Spend': f"${recommended['spend']:,.0f}",
                                                    'Recommended %': f"{recommended['percentage']:.1f}%",
                                                    'Change': f"${recommended['change']:,.0f}",
                                                    'Change %': f"{recommended['change_pct']:+.1f}%"
                                                })
                                            
                                            budget_df = pd.DataFrame(budget_data)
                                            st.dataframe(budget_df, use_container_width=True)
                                            
                                            # Show expected improvement
                                            improvement = analysis['budget_optimization']['expected_improvement']
                                            st.success(f"""
                                            **Expected Improvement:**
                                            - Current Portfolio ROAS: {improvement['current_roas']:.2f}x
                                            - Expected Portfolio ROAS: {improvement['expected_roas']:.2f}x
                                            - Improvement: +{improvement['improvement']:.2f}x ({improvement['improvement_pct']:.1f}%)
                                            """)
                                        
                                        # Download full report
                                        st.markdown("---")
                                        report_json = json.dumps(analysis, indent=2, default=str)
                                        st.download_button(
                                            label="📥 Download Full Analysis Report (JSON)",
                                            data=report_json,
                                            file_name=f"campaign_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                                            mime="application/json"
                                        )
                                        
                                        st.success("✅ **Analysis Complete!** Review insights and recommendations above.")
                                
                                except Exception as e:
                                    st.error(f"❌ Error during analysis: {str(e)}")
                                    import traceback
                                    st.code(traceback.format_exc())
                        
                    except Exception as e:
                        st.error(f"❌ Error processing CSV: {str(e)}")
            
            # Handle screenshot input
            elif input_method == "📸 Dashboard Screenshots" and uploaded_files:
                with st.spinner("Creating campaign and uploading snapshots..."):
                    try:
                        # Create campaign
                        response = requests.post(
                            f"{API_BASE_URL}/api/campaigns",
                            params={
                                "campaign_name": campaign_name,
                                "objectives": objectives,
                                "start_date": start_date.isoformat(),
                                "end_date": end_date.isoformat()
                            }
                        )
                        
                        if response.status_code == 200:
                            campaign_data = response.json()
                            campaign_id = campaign_data["campaign_id"]
                            
                            st.success(f"✅ Campaign created: {campaign_id}")
                            
                            # Upload snapshots
                            files = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
                            
                            upload_response = requests.post(
                                f"{API_BASE_URL}/api/campaigns/{campaign_id}/snapshots",
                                files=files
                            )
                            
                            if upload_response.status_code == 200:
                                st.success(f"✅ Uploaded {len(uploaded_files)} snapshots")
                                
                                # Start analysis
                                analyze_response = requests.post(
                                    f"{API_BASE_URL}/api/campaigns/{campaign_id}/analyze"
                                )
                                
                                if analyze_response.status_code == 200:
                                    st.success("✅ Analysis started!")
                                    st.info(f"Campaign ID: `{campaign_id}`")
                                    st.markdown("Check the **Campaigns** tab to monitor progress.")
                                else:
                                    st.error(f"❌ Failed to start analysis: {analyze_response.text}")
                            else:
                                st.error(f"❌ Failed to upload snapshots: {upload_response.text}")
                        else:
                            st.error(f"❌ Failed to create campaign: {response.text}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

with tab2:
    st.header("💬 Ask Questions About Your Data")
    st.markdown("### Natural Language SQL Query Engine")
    st.markdown("Ask questions in plain English and get instant answers from your campaign data!")
    
    # Initialize session state for query engine
    if 'query_engine' not in st.session_state:
        st.session_state.query_engine = None
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    # Upload data section
    st.markdown("---")
    st.subheader("📊 Step 1: Upload Your Campaign Data")
    
    uploaded_query_csv = st.file_uploader(
        "Upload CSV file to query",
        type=["csv"],
        key="query_csv_uploader",
        help="Upload your campaign data CSV to start asking questions"
    )
    
    if uploaded_query_csv:
        try:
            df = pd.read_csv(uploaded_query_csv)
            st.success(f"✅ Loaded {len(df)} rows with {len(df.columns)} columns")
            
            # Show data preview
            with st.expander("📋 Data Preview"):
                st.dataframe(df.head(10), use_container_width=True)
                st.caption(f"Showing first 10 of {len(df)} rows")
            
            # Initialize query engine
            if st.session_state.query_engine is None:
                try:
                    import os
                    from src.query_engine import NaturalLanguageQueryEngine
                    
                    api_key = os.getenv('OPENAI_API_KEY')
                    if api_key:
                        st.session_state.query_engine = NaturalLanguageQueryEngine(api_key)
                        st.session_state.query_engine.load_data(df)
                        st.success("✅ Query engine initialized! You can now ask questions.")
                    else:
                        st.warning("⚠️ OpenAI API key not found. Set OPENAI_API_KEY in .env file to enable natural language queries.")
                        st.info("💡 You can still write SQL queries directly below.")
                except Exception as e:
                    st.error(f"❌ Error initializing query engine: {e}")
            
            st.markdown("---")
            st.subheader("💬 Step 2: Ask Questions")
            
            # Query mode selection
            query_mode = st.radio(
                "Choose query mode:",
                options=["🤖 Natural Language (AI-powered)", "📝 Direct SQL Query"],
                horizontal=True
            )
            
            if query_mode == "🤖 Natural Language (AI-powered)":
                # Natural language interface
                st.markdown("**Ask any question about your data in plain English:**")
                
                # Suggested questions
                with st.expander("💡 Suggested Questions"):
                    suggested = [
                        "Which campaign had the highest ROAS?",
                        "What is the total spend across all campaigns?",
                        "Show me the top 5 campaigns by conversions",
                        "Which platform performs best on average?",
                        "What is the average CPA by campaign?",
                        "Compare spend between google_ads and meta_ads",
                        "Which campaigns ran in November 2024?",
                        "Show campaigns with ROAS greater than 4.0",
                        "What is the CTR for each platform?",
                        "Which campaign had the lowest CPA?"
                    ]
                    
                    cols = st.columns(2)
                    for i, q in enumerate(suggested):
                        with cols[i % 2]:
                            if st.button(q, key=f"suggested_{i}", use_container_width=True):
                                st.session_state.current_question = q
                
                # Question input
                question = st.text_input(
                    "Your question:",
                    value=st.session_state.get('current_question', ''),
                    placeholder="e.g., Which campaign had the best ROAS?",
                    key="nl_question_input"
                )
                
                if st.button("🔍 Get Answer", type="primary", use_container_width=True):
                    if question and st.session_state.query_engine:
                        with st.spinner("🤔 Thinking..."):
                            result = st.session_state.query_engine.ask(question)
                            
                            if result['success']:
                                # Show answer
                                st.success("✅ Answer:")
                                st.markdown(f"### {result['answer']}")
                                
                                # Show SQL query
                                with st.expander("🔧 Generated SQL Query"):
                                    st.code(result['sql_query'], language="sql")
                                
                                # Show results
                                with st.expander("📊 Detailed Results"):
                                    st.dataframe(result['results'], use_container_width=True)
                                    
                                    # Download results
                                    csv = result['results'].to_csv(index=False)
                                    st.download_button(
                                        label="📥 Download Results as CSV",
                                        data=csv,
                                        file_name="query_results.csv",
                                        mime="text/csv"
                                    )
                                
                                # Add to history
                                st.session_state.query_history.append({
                                    "question": question,
                                    "answer": result['answer'],
                                    "sql": result['sql_query']
                                })
                            else:
                                st.error(f"❌ Error: {result['error']}")
                    elif not st.session_state.query_engine:
                        st.warning("⚠️ Query engine not initialized. Please set OPENAI_API_KEY.")
                    else:
                        st.warning("⚠️ Please enter a question.")
            
            else:
                # Direct SQL interface
                st.markdown("**Write your SQL query:**")
                st.info("💡 Table name: `campaigns` | Use standard SQL syntax")
                
                # Show schema
                with st.expander("📋 Table Schema"):
                    schema_df = pd.DataFrame({
                        'Column': df.columns,
                        'Type': [str(dtype) for dtype in df.dtypes]
                    })
                    st.dataframe(schema_df, use_container_width=True)
                
                sql_query = st.text_area(
                    "SQL Query:",
                    height=150,
                    placeholder="SELECT * FROM campaigns WHERE ROAS > 4.0 ORDER BY ROAS DESC LIMIT 10",
                    key="direct_sql_input"
                )
                
                if st.button("▶️ Execute Query", type="primary", use_container_width=True):
                    if sql_query:
                        try:
                            import duckdb
                            conn = duckdb.connect(':memory:')
                            conn.register('campaigns', df)
                            result_df = conn.execute(sql_query).fetchdf()
                            conn.close()
                            
                            st.success(f"✅ Query executed successfully! Returned {len(result_df)} rows.")
                            st.dataframe(result_df, use_container_width=True)
                            
                            # Download results
                            csv = result_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results as CSV",
                                data=csv,
                                file_name="query_results.csv",
                                mime="text/csv"
                            )
                        except Exception as e:
                            st.error(f"❌ SQL Error: {e}")
                    else:
                        st.warning("⚠️ Please enter a SQL query.")
            
            # Query history
            if st.session_state.query_history:
                st.markdown("---")
                st.subheader("📜 Query History")
                
                for i, item in enumerate(reversed(st.session_state.query_history[-5:]), 1):
                    with st.expander(f"Q{i}: {item['question'][:50]}..."):
                        st.markdown(f"**Question:** {item['question']}")
                        st.markdown(f"**Answer:** {item['answer']}")
                        st.code(item['sql'], language="sql")
        
        except Exception as e:
            st.error(f"❌ Error loading CSV: {e}")
    
    else:
        st.info("👆 Upload a CSV file to start asking questions about your campaign data!")
        
        # Show example
        st.markdown("---")
        st.markdown("### 🎯 How It Works")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Natural Language Mode:**
            1. Upload your campaign CSV
            2. Ask questions in plain English
            3. AI converts to SQL automatically
            4. Get instant answers with data
            
            **Example Questions:**
            - "Which campaign performed best?"
            - "Show total spend by platform"
            - "What's the average ROAS?"
            """)
        
        with col2:
            st.markdown("""
            **Direct SQL Mode:**
            1. Upload your campaign CSV
            2. Write SQL queries directly
            3. Execute against your data
            4. Download results as CSV
            
            **Example Query:**
            ```sql
            SELECT Campaign_Name, 
                   SUM(Spend) as Total_Spend,
                   AVG(ROAS) as Avg_ROAS
            FROM campaigns
            GROUP BY Campaign_Name
            ORDER BY Total_Spend DESC
            ```
            """)

with tab3:
    st.header("Campaign List")
    
    if st.button("🔄 Refresh"):
        st.rerun()
    
    # In a real app, this would fetch from the API
    st.info("Campaign list will be displayed here. Currently showing demo data.")
    
    # Demo campaign card
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            st.markdown("**Q4 2024 Holiday Campaign**")
            st.caption("Created: 2024-11-14")
        
        with col2:
            st.metric("Status", "Completed", delta="✓")
        
        with col3:
            st.metric("Channels", "6")
        
        with col4:
            if st.button("📥 Download Report", key="demo_download"):
                st.info("Report download functionality")
    
    st.markdown("---")
    
    # Campaign details
    with st.expander("View Campaign Details"):
        st.json({
            "campaign_id": "demo-123",
            "campaign_name": "Q4 2024 Holiday Campaign",
            "status": "completed",
            "objectives": ["awareness", "conversion"],
            "date_range": {
                "start": "2024-10-01",
                "end": "2024-12-31"
            },
            "snapshots_count": 6,
            "total_spend": 125000.50,
            "total_conversions": 3250,
            "overall_roas": 4.2
        })

with tab4:
    st.header("Documentation")
    
    st.markdown("""
    ## How to Use PCA Agent
    
    ### 1. Create Campaign
    - Enter campaign name and objectives
    - Set date range
    - Choose input method: Screenshots or CSV
    
    ### 2A. Upload Dashboard Screenshots
    - Supported formats: PNG, JPG, PDF
    - Upload screenshots from multiple platforms
    - System will auto-detect platforms using Vision AI
    
    ### 2B. Upload CSV Data Files (Alternative)
    - Upload CSV files with campaign metrics
    - Each CSV should contain platform and metric columns
    - Bypasses vision extraction, uses direct data
    
    **CSV Format Example:**
    ```csv
    Platform,Impressions,Clicks,CTR,Conversions,Spend,CPC,CPA,ROAS
    google_ads,1250000,25000,2.0,850,45000,1.80,52.94,4.2
    meta_ads,980000,18500,1.89,620,32000,1.73,51.61,3.8
    linkedin_ads,450000,12000,2.67,380,18000,1.50,47.37,3.5
    ```
    
    **Required Columns:**
    - Platform (e.g., google_ads, meta_ads, linkedin_ads)
    - At least 3 metrics (Impressions, Clicks, Spend, etc.)
    
    **Optional Columns:**
    - CTR, Conversions, CPC, CPM, CPA, ROAS
    - Reach, Frequency, Engagement metrics
    
    ### 3. Analysis Process
    The AI agent will:
    1. **Extract Data**: Use Vision AI (screenshots) or parse CSV (data files)
    2. **Normalize**: Standardize data across platforms
    3. **Analyze**: Generate insights using AI reasoning
    4. **Visualize**: Create charts and graphs
    5. **Report**: Generate PowerPoint presentation
    
    ### 4. Download Report
    - PowerPoint format with all insights
    - Executive summary
    - Channel-by-channel analysis
    - Cross-channel insights
    - Key achievements
    - Recommendations
    
    ## Supported Platforms
    
    | Platform | Metrics Extracted |
    |----------|------------------|
    | Google Ads | Impressions, Clicks, CTR, Conversions, Spend, CPC, CPA, Quality Score |
    | CM360 | Impressions, Clicks, CTR, Reach, Frequency, Viewability |
    | DV360 | Impressions, Clicks, CTR, Spend, CPM, Viewability, Video Completion |
    | Meta Ads | Impressions, Reach, Clicks, Spend, ROAS, Engagement (Likes, Shares, Comments) |
    | Snapchat Ads | Impressions, Reach, Clicks, Video Views, Completion Rate |
    | LinkedIn Ads | Impressions, Clicks, CTR, Conversions, Spend, CPC, CPA, Engagement |
    
    ## API Endpoints
    
    ```python
    # Create campaign
    POST /api/campaigns
    
    # Upload snapshots
    POST /api/campaigns/{id}/snapshots
    
    # Start analysis
    POST /api/campaigns/{id}/analyze
    
    # Check status
    GET /api/campaigns/{id}/status
    
    # Download report
    GET /api/campaigns/{id}/report
    ```
    
    ## Tips for Best Results
    
    1. **High Quality Screenshots**: Use full-screen captures with clear text
    2. **Complete Data**: Include all relevant metrics in screenshots
    3. **Consistent Date Ranges**: Ensure all platforms show the same period
    4. **Multiple Platforms**: Upload at least 2 platforms for cross-channel analysis
    5. **Clear Objectives**: Select accurate campaign objectives for better insights
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>PCA Agent v1.0.0 | Powered by GPT-4V, Claude Sonnet 4, and LangGraph</p>
</div>
""", unsafe_allow_html=True)
