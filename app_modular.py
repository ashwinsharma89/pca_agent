"""
Modular Streamlit App - Main Entry Point.

This is the refactored version of streamlit_app.py with:
1. Modular component structure (< 500 lines per file)
2. Consolidated single app version
3. Clean code with proper logging (no debug prints)
4. Component-level caching strategy

Usage:
    streamlit run app_modular.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

import streamlit as st
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging (no print statements!)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import modular components
from streamlit_components.data_loader import DataLoaderComponent, load_cached_dataframe
from streamlit_components.analysis_runner import AnalysisRunnerComponent, AnalysisHistoryComponent
from streamlit_components.caching_strategy import CacheManager
from streamlit_components.smart_filters import InteractiveFilterPanel

# Page configuration
st.set_page_config(
    page_title="PCA Agent - Modular",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        "df": None,
        "df_loaded_from_cache": False,
        "analysis_complete": False,
        "analysis_data": None,
        "analysis_history": [],
        "current_page": "home"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    """Render sidebar navigation and controls."""
    with st.sidebar:
        st.title("📊 PCA Agent")
        st.caption("Performance Campaign Analytics")
        
        st.divider()
        
        # Navigation
        st.subheader("Navigation")
        
        page = st.radio(
            "Select Page",
            options=["Home", "Data Upload", "Analysis", "Q&A", "Settings"],
            key="nav_radio"
        )
        
        st.session_state.current_page = page.lower()
        
        st.divider()
        
        # Data status
        st.subheader("Data Status")
        
        if st.session_state.df is not None:
            st.success(f"✅ Data loaded: {len(st.session_state.df)} rows")
            
            if st.button("🗑️ Clear Data"):
                st.session_state.df = None
                st.session_state.analysis_complete = False
                st.session_state.analysis_data = None
                st.rerun()
        else:
            st.info("No data loaded")
        
        st.divider()
        
        # Analysis history
        if st.session_state.get('analysis_history'):
            AnalysisHistoryComponent.render_history()
        
        st.divider()
        
        # Cache management
        CacheManager.render_cache_controls()


def render_home_page():
    """Render home page."""
    st.markdown('<div class="main-header">🏠 Welcome to PCA Agent</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Performance Campaign Analytics Agent
    
    A modular, production-ready application for campaign performance analysis.
    
    **Features:**
    - 📁 Multi-source data loading (CSV, Excel, S3, Azure, GCS)
    - 🤖 AI-powered auto-analysis
    - 💬 Natural language Q&A
    - 📊 Interactive visualizations
    - 🗄️ Smart caching for performance
    
    **Get Started:**
    1. Navigate to **Data Upload** to load your campaign data
    2. Go to **Analysis** to run AI-powered insights
    3. Use **Q&A** to ask questions about your data
    """)
    
    # Quick stats
    if st.session_state.df is not None:
        st.subheader("📈 Quick Stats")
        
        df = st.session_state.df
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        
        with col2:
            st.metric("Columns", len(df.columns))
        
        with col3:
            if 'Spend' in df.columns:
                st.metric("Total Spend", f"${df['Spend'].sum():,.2f}")
        
        with col4:
            if 'Clicks' in df.columns:
                st.metric("Total Clicks", f"{df['Clicks'].sum():,}")


def render_data_upload_page():
    """Render data upload page."""
    st.markdown('<div class="main-header">📁 Data Upload</div>', unsafe_allow_html=True)
    
    # Try to load cached data first
    if st.session_state.df is None and not st.session_state.df_loaded_from_cache:
        cached_df = load_cached_dataframe()
        if cached_df is not None:
            st.session_state.df = cached_df
            st.session_state.df_loaded_from_cache = True
            st.success("✅ Loaded cached data from previous session")
    
    # File uploader
    df = DataLoaderComponent.render_file_uploader()
    
    # Sample data button
    if st.session_state.df is None:
        DataLoaderComponent.render_sample_data_button()
    
    # Cloud storage options
    st.divider()
    DataLoaderComponent.render_cloud_storage_options()
    
    # Show data preview
    if st.session_state.df is not None:
        st.divider()
        st.subheader("📋 Data Preview")
        
        # Show first few rows
        st.dataframe(
            st.session_state.df.head(10),
            use_container_width=True,
            height=300
        )
        
        # Show column info
        with st.expander("ℹ️ Column Information"):
            col_info = st.session_state.df.dtypes.to_frame('Type')
            col_info['Non-Null Count'] = st.session_state.df.count()
            col_info['Null Count'] = st.session_state.df.isnull().sum()
            st.dataframe(col_info)


def render_analysis_page():
    """Render analysis page."""
    st.markdown('<div class="main-header">🤖 AI Analysis</div>', unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.warning("⚠️ Please upload data first")
        return
    
    # Analysis configuration
    config = AnalysisRunnerComponent.render_analysis_config()
    
    st.divider()
    
    # Run analysis button
    if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
        results = AnalysisRunnerComponent.run_analysis(st.session_state.df, config)
        
        if results:
            st.session_state.analysis_data = results
            st.session_state.analysis_complete = True
            
            # Save to history
            AnalysisHistoryComponent.save_to_history(results)
            
            st.success("✅ Analysis complete!")
            st.rerun()
    
    # Display results
    if st.session_state.analysis_complete and st.session_state.analysis_data:
        st.divider()
        AnalysisRunnerComponent.display_results(st.session_state.analysis_data)


def render_qa_page():
    """Render Q&A page."""
    st.markdown('<div class="main-header">💬 Ask Questions</div>', unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.warning("⚠️ Please upload data first")
        return
    
    st.markdown("""
    Ask natural language questions about your campaign data.
    
    **Examples:**
    - "What is the total spend by platform?"
    - "Which campaign has the highest CTR?"
    - "Show me performance trends over time"
    """)
    
    # Question input
    question = st.text_input(
        "Your question:",
        placeholder="e.g., What is the average CPC by channel?"
    )
    
    if st.button("🔍 Ask", type="primary") and question:
        with st.spinner("Thinking..."):
            # TODO: Integrate with NL to SQL engine
            st.info("Q&A functionality will be integrated with the improved NL to SQL engine")


def render_settings_page():
    """Render settings page."""
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    st.subheader("Application Settings")
    
    # Cache settings
    st.markdown("### 🗄️ Cache Settings")
    
    cache_enabled = st.checkbox("Enable caching", value=True)
    cache_ttl = st.slider("Cache TTL (minutes)", 5, 120, 60)
    
    if st.button("Apply Settings"):
        st.success("✅ Settings saved")
    
    # Debug info
    with st.expander("🔧 Debug Information"):
        st.json({
            'session_state_keys': list(st.session_state.keys()),
            'cache_stats': CacheManager.get_cache_stats()
        })


def main():
    """Main application entry point."""
    # Initialize
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render current page
    page = st.session_state.current_page
    
    if page == "home":
        render_home_page()
    elif page == "data upload":
        render_data_upload_page()
    elif page == "analysis":
        render_analysis_page()
    elif page == "q&a":
        render_qa_page()
    elif page == "settings":
        render_settings_page()
    
    # Footer
    st.divider()
    st.caption("PCA Agent v2.0 - Modular Architecture | Built with Streamlit")


if __name__ == "__main__":
    logger.info("Starting PCA Agent (Modular)")
    main()
