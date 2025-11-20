"""Unified PCA Agent Streamlit app with auto-analysis + HITL Q&A."""
# At the top of streamlit_app_hitl.py
import sys
import os
from pathlib import Path

# Add both current directory and parent to Python path for Streamlit Cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

import streamlit as st

# DELETE OR COMMENT OUT THESE LINES (11-17):
# print("Project root:", project_root)
# print("Files in src/query_engine/:")
# query_engine_path = project_root / "src" / "query_engine"
# if query_engine_path.exists():
#     print(os.listdir(query_engine_path))
# else:
#     print("Directory doesn't exist!")

# Then your imports...
import time
from datetime import datetime
from typing import Optional

import pandas as pd
import plotly.express as px
# REMOVE this duplicate streamlit import (line 25):
# import streamlit as st
from dotenv import load_dotenv

from src.analytics import MediaAnalyticsExpert
from src.evaluation.query_tracker import QueryTracker
from src.query_engine.nl_to_sql import NaturalLanguageQueryEngine
#from src.query_engine.smart_interpretation import SmartQueryInterpreter
from src.orchestration.query_orchestrator import QueryOrchestrator

load_dotenv()

CACHE_DIR = ".pca_cache"
LAST_CSV_PATH = os.path.join(CACHE_DIR, "last_campaign_data.csv")
os.makedirs(CACHE_DIR, exist_ok=True)

st.set_page_config(
    page_title="PCA Agent - Auto Analysis + HITL Q&A",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.75rem;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #ff6cab 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    .section-divider {
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(102,126,234,0.35);
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.95), rgba(118,75,162,0.95));
        padding: 1.25rem;
        border-radius: 12px;
        color: white;
        box-shadow: 0 20px 45px rgba(50,50,93,0.15);
    }
    .insight-card {
        background: #f8f9ff;
        padding: 1.1rem;
        border-left: 4px solid #667eea;
        border-radius: 8px;
        margin-bottom: 0.75rem;
    }

    /* App background and main container */
    .stApp {
        background: radial-gradient(circle at top left, #0f172a 0, #020617 45%, #000000 100%);
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617 0%, #0b1120 35%, #111827 100%);
        border-right: 1px solid rgba(148,163,184,0.35);
    }
    [data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }

    /* Tabs styling */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        background: rgba(15,23,42,0.85);
        border-radius: 999px;
        padding: 0.5rem 1.1rem;
        color: #cbd5f5;
        font-weight: 600;
        border: 1px solid transparent;
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        background: linear-gradient(90deg, #4f46e5, #7c3aed);
        color: #f9fafb !important;
        border-color: rgba(191,219,254,0.35);
    }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #4f46e5, #ec4899);
        color: white;
        border-radius: 999px;
        padding: 0.4rem 1.5rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 12px 25px rgba(15,23,42,0.45);
    }
    .stButton > button[kind="primary"]:hover {
        filter: brightness(1.05);
        box-shadow: 0 18px 35px rgba(15,23,42,0.65);
    }

    /* Dataframes */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 18px 40px rgba(15,23,42,0.35);
    }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------
def init_state():
    defaults = {
        "analysis_complete": False,
        "analysis_data": None,
        "df": None,
        "df_loaded_from_cache": False,
        "query_tracker": QueryTracker(),
        "interpreter": None,
        "orchestrator": None,
        "current_query_id": None,
        "interpretations": None,
        "selected_interpretation": None,
        "query_engine": None,
        "session_id": str(datetime.now().timestamp()),
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


init_state()


def load_cached_df_if_available():
    if st.session_state.get("df") is None and os.path.exists(LAST_CSV_PATH):
        try:
            df_cached = pd.read_csv(LAST_CSV_PATH)
            st.session_state.df = df_cached
            st.session_state.df_loaded_from_cache = True
        except Exception:
            st.session_state.df_loaded_from_cache = False


load_cached_df_if_available()


def _get_column(df: pd.DataFrame, metric: str) -> Optional[str]:
    """Use shared column mappings from MediaAnalyticsExpert to find actual column name."""
    mappings = getattr(MediaAnalyticsExpert, "COLUMN_MAPPINGS", {})
    metric = metric.lower()
    if metric in mappings:
        for col_name in mappings[metric]:
            if col_name in df.columns:
                return col_name
    return None


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image(
        "https://via.placeholder.com/220x80/667eea/ffffff?text=PCA+Agent",
        use_container_width=True,
    )
    st.markdown("---")

    st.markdown("### 🎯 Capabilities")
    st.markdown(
        """
        - 📊 Auto-insights dashboard
        - 💡 Executive summaries & metrics
        - 🔮 Predictive & ROAS views
        - 💬 Natural language Q&A
        - 🤝 Human-in-the-loop disambiguation
        - 📈 Traceability & evaluation metrics
        """
    )

    st.markdown("---")
    st.markdown("### 📱 Supported Platforms")
    for platform in ["Google Ads", "Meta Ads", "LinkedIn", "DV360", "CM360", "Snapchat"]:
        st.markdown(f"✓ {platform}")

    st.markdown("---")
    if st.button("🔄 Reset Workspace", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        if os.path.exists(LAST_CSV_PATH):
            try:
                os.remove(LAST_CSV_PATH)
            except Exception:
                pass
        st.experimental_set_query_params()
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 HITL Metrics")
    metrics = st.session_state.query_tracker.get_metrics_summary()
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Total Queries", metrics["total_queries"])
        st.metric("Success Rate", f"{metrics['success_rate']:.1f}%")
    with col_b:
        st.metric("Avg Feedback", f"{metrics['avg_feedback']:.2f}")
        st.metric("Interp. Accuracy", f"{metrics['interpretation_accuracy']:.1f}%")
    st.metric("Avg Response Time", f"{metrics['avg_execution_time_ms']:.0f} ms")

    if st.button("📥 Export Query Logs", use_container_width=True):
        export_path = st.session_state.query_tracker.export_to_csv()
        st.success(f"Exported to {export_path}")


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<h1 class="main-header">PCA Agent Intelligence Hub</h1>', unsafe_allow_html=True)
st.markdown(
    "**Auto-analysis, predictive insights, and human-in-the-loop Q&A in one place.**"
)
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_auto, tab_hitl, tab_history, tab_metrics = st.tabs(
    [
        "📊 Auto Analysis",
        "💬 Natural Language Q&A",
        "📜 Query History",
        "📈 System Analytics",
    ]
)


# ---------------------------------------------------------------------------
# Auto Analysis Tab (restored UI)
# ---------------------------------------------------------------------------
with tab_auto:
    if not st.session_state.analysis_complete:
        st.markdown("## 📤 Upload Your Campaign Data")
        col_upload, col_tip = st.columns([2, 1])
        with col_upload:
            input_method = st.radio(
                "Choose Input Method",
                options=["📊 CSV Data", "📸 Dashboard Screenshots"],
                horizontal=True,
            )
        with col_tip:
            st.info("💡 CSV upload gives instant results.")

        st.markdown("---")

        if input_method == "📊 CSV Data":
            uploaded_file = st.file_uploader(
                "Upload your campaign CSV",
                type=["csv"],
                help="Include Campaign_Name, Platform, Spend, ROAS, etc.",
            )

            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.session_state.df = df
                    try:
                        df.to_csv(LAST_CSV_PATH, index=False)
                    except Exception:
                        pass
                    st.success(f"✅ Loaded {len(df)} rows • {len(df.columns)} columns")

                    with st.expander("📋 Data Preview", expanded=True):
                        st.dataframe(df.head(10), use_container_width=True)
                        col_a, col_b, col_c, col_d = st.columns(4)

                        # Basic row count
                        col_a.metric("Rows", len(df))

                        # Campaign count using flexible column mapping
                        campaign_col = _get_column(df, "campaign")
                        campaigns = (
                            df[campaign_col].nunique() if campaign_col else 0
                        )
                        col_b.metric("Campaigns", campaigns)

                        # Platform count (fallback to 0 if missing)
                        platforms = (
                            df["Platform"].nunique()
                            if "Platform" in df.columns
                            else 0
                        )
                        col_c.metric("Platforms", platforms)

                        # Total spend using flexible column mapping
                        spend_col = _get_column(df, "spend")
                        total_spend = (
                            float(df[spend_col].sum()) if spend_col else 0.0
                        )
                        col_d.metric("Total Spend", f"${total_spend:,.0f}")

                    st.markdown("---")
                    if st.button("🚀 Analyze Data & Generate Insights", type="primary"):
                        with st.spinner("🤖 AI Expert analyzing your data (30-60s)..."):
                            expert = MediaAnalyticsExpert()
                            analysis = expert.analyze_all(df)
                            st.session_state.analysis_data = analysis
                            st.session_state.analysis_complete = True
                            st.rerun()
                except Exception as exc:
                    st.error(f"❌ Error loading CSV: {exc}")
            elif st.session_state.df is not None:
                df = st.session_state.df
                st.success(
                    f"✅ Using previously loaded data • {len(df)} rows • {len(df.columns)} columns"
                )

                with st.expander("📋 Data Preview", expanded=True):
                    st.dataframe(df.head(10), use_container_width=True)
                    col_a, col_b, col_c, col_d = st.columns(4)

                    col_a.metric("Rows", len(df))

                    campaign_col = _get_column(df, "campaign")
                    campaigns = (
                        df[campaign_col].nunique() if campaign_col else 0
                    )
                    col_b.metric("Campaigns", campaigns)

                    platforms = (
                        df["Platform"].nunique()
                        if "Platform" in df.columns
                        else 0
                    )
                    col_c.metric("Platforms", platforms)

                    spend_col = _get_column(df, "spend")
                    total_spend = (
                        float(df[spend_col].sum()) if spend_col else 0.0
                    )
                    col_d.metric("Total Spend", f"${total_spend:,.0f}")

                st.markdown("---")
                if st.button("🚀 Analyze Data & Generate Insights", type="primary"):
                    with st.spinner("🤖 AI Expert analyzing your data (30-60s)..."):
                        expert = MediaAnalyticsExpert()
                        analysis = expert.analyze_all(df)
                        st.session_state.analysis_data = analysis
                        st.session_state.analysis_complete = True
                        st.rerun()

        else:
            st.warning(
                "Screenshot ingestion requires the backend vision pipeline. "
                "Switch to CSV mode for self-contained analysis."
            )
            uploaded_images = st.file_uploader(
                "Upload dashboard screenshots",
                type=["png", "jpg", "jpeg", "pdf"],
                accept_multiple_files=True,
            )
            if uploaded_images:
                st.success(f"📸 {len(uploaded_images)} files uploaded")
                with st.expander("Preview Files"):
                    cols = st.columns(3)
                    for i, img in enumerate(uploaded_images):
                        cols[i % 3].image(img, caption=img.name, use_column_width=True)

    else:
        analysis = st.session_state.analysis_data
        df = st.session_state.df

        st.markdown("## 📊 Executive Summary")
        st.info(analysis["executive_summary"])
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

        st.markdown("## 🧭 Management Overview")
        filter_cols = st.columns(3)
        campaign_options = ["All Campaigns"] + (
            sorted(df["Campaign_Name"].dropna().unique().tolist())
            if "Campaign_Name" in df.columns
            else []
        )
        selected_campaign = filter_cols[0].selectbox(
            "Campaign",
            options=campaign_options,
        )
        platform_options = (
            sorted(df["Platform"].dropna().unique().tolist())
            if "Platform" in df.columns
            else []
        )
        selected_platforms = filter_cols[1].multiselect(
            "Platforms",
            options=platform_options,
            default=platform_options,
        )
        date_range = None
        if "Date" in df.columns:
            try:
                df_dates = pd.to_datetime(df["Date"], errors="coerce")
                min_date, max_date = df_dates.min(), df_dates.max()
                if pd.notna(min_date) and pd.notna(max_date):
                    date_range = filter_cols[2].date_input(
                        "Date Range",
                        value=(min_date.date(), max_date.date()),
                    )
            except Exception:
                date_range = None

        df_mgmt = df.copy()
        if selected_campaign != "All Campaigns" and "Campaign_Name" in df_mgmt.columns:
            df_mgmt = df_mgmt[df_mgmt["Campaign_Name"] == selected_campaign]
        if selected_platforms and "Platform" in df_mgmt.columns:
            df_mgmt = df_mgmt[df_mgmt["Platform"].isin(selected_platforms)]
        if date_range and "Date" in df_mgmt.columns:
            df_mgmt = df_mgmt.copy()
            df_mgmt["Date"] = pd.to_datetime(df_mgmt["Date"], errors="coerce")
            start_date, end_date = date_range
            df_mgmt = df_mgmt[
                (df_mgmt["Date"] >= pd.to_datetime(start_date))
                & (df_mgmt["Date"] <= pd.to_datetime(end_date))
            ]

        # Use flexible column mapping for spend/conversions
        spend_col_mgmt = _get_column(df_mgmt, "spend")
        conv_col_mgmt = _get_column(df_mgmt, "conversions")
        roas_col_mgmt = _get_column(df_mgmt, "roas")
        cpa_col_mgmt = _get_column(df_mgmt, "cpa")

        # Build dynamic metrics based on available columns
        available_metrics = []
        if spend_col_mgmt:
            available_metrics.append(("Total Spend", f"${float(df_mgmt[spend_col_mgmt].sum()):,.0f}"))
        if conv_col_mgmt:
            available_metrics.append(("Total Conversions", f"{float(df_mgmt[conv_col_mgmt].sum()):,.0f}"))
        if roas_col_mgmt:
            available_metrics.append(("Avg ROAS", f"{df_mgmt[roas_col_mgmt].mean():.2f}x"))
        if cpa_col_mgmt:
            available_metrics.append(("Avg CPA", f"${df_mgmt[cpa_col_mgmt].mean():.2f}"))
        
        # Show only available metrics
        if available_metrics:
            cols = st.columns(len(available_metrics))
            for idx, (label, value) in enumerate(available_metrics):
                cols[idx].metric(label, value)

        if not df_mgmt.empty and "Date" in df_mgmt.columns and (spend_col_mgmt or conv_col_mgmt):
            df_line = df_mgmt.copy()
            df_line["Date"] = pd.to_datetime(df_line["Date"], errors="coerce")
            agg_dict = {}
            if spend_col_mgmt:
                agg_dict[spend_col_mgmt] = "sum"
            if conv_col_mgmt:
                agg_dict[conv_col_mgmt] = "sum"
            daily = df_line.groupby("Date").agg(agg_dict).reset_index()
            fig = px.line(
                daily,
                x="Date",
                y=list(agg_dict.keys()),
                title="Daily Performance",
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("## 📈 Key Performance Metrics")
        overview = analysis["metrics"]["overview"]
        
        # Build dynamic overview metrics based on what's available
        overview_metrics = []
        if overview.get('total_spend', 0) > 0:
            overview_metrics.append(("Total Spend", f"${overview['total_spend']:,.0f}"))
        if overview.get('total_conversions', 0) > 0:
            overview_metrics.append(("Total Conversions", f"{overview['total_conversions']:,.0f}"))
        if overview.get('avg_roas') and overview['avg_roas'] > 0:
            overview_metrics.append(("Average ROAS", f"{overview['avg_roas']:.2f}x"))
        if overview.get('avg_cpa') and overview['avg_cpa'] > 0:
            overview_metrics.append(("Average CPA", f"${overview['avg_cpa']:.2f}"))
        
        if overview_metrics:
            cols = st.columns(len(overview_metrics))
            for idx, (label, value) in enumerate(overview_metrics):
                cols[idx].metric(label, value)

        st.markdown("## 💡 Opportunities & Risks")

        # Nicely formatted opportunity cards
        for opp in analysis["opportunities"]:
            opp_type = opp.get("type", "Opportunity")
            period = opp.get("period")
            avg_roas = opp.get("avg_roas")
            desc = opp.get("opportunity") or opp.get("description")
            impact = opp.get("potential_impact") or opp.get("impact")

            details = []
            if period:
                details.append(f"<strong>Period:</strong> {period}")
            if avg_roas is not None:
                try:
                    details.append(f"<strong>Avg ROAS:</strong> {float(avg_roas):.2f}x")
                except Exception:
                    details.append(f"<strong>Avg ROAS:</strong> {avg_roas}")
            if desc:
                details.append(f"<strong>Why it matters:</strong> {desc}")
            if impact:
                details.append(f"<strong>Recommended action:</strong> {impact}")

            body_html = "<br>".join(details)
            card_html = (
                "<div class='insight-card'>"
                f"✅ <strong>{opp_type}</strong><br>"
                f"{body_html}"
                "</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)

        # Nicely formatted risk cards
        for risk in analysis["risks"]:
            severity = risk.get("severity", "Risk")
            title = risk.get("risk", "Performance Risk")
            details = risk.get("details")
            impact = risk.get("impact")
            action = risk.get("action")

            lines = []
            lines.append(f"<strong>Severity:</strong> {severity}")
            lines.append(f"<strong>Risk:</strong> {title}")
            if details:
                lines.append(f"<strong>Details:</strong> {details}")
            if impact:
                lines.append(f"<strong>Impact:</strong> {impact}")
            if action:
                lines.append(f"<strong>Recommended action:</strong> {action}")

            body_html = "<br>".join(lines)
            card_html = (
                "<div class='insight-card' style='border-left-color:#e74c3c'>"
                f"⚠️ <strong>{title}</strong><br>"
                f"{body_html}"
                "</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)

        st.markdown("## 🔁 Want to re-run?")
        if st.button("🧹 Clear Analysis", use_container_width=True):
            st.session_state.analysis_complete = False
            st.session_state.analysis_data = None
            st.session_state.df = None
            st.rerun()


# ---------------------------------------------------------------------------
# Natural Language Q&A Tab
# ---------------------------------------------------------------------------
with tab_hitl:
    st.markdown("## 💬 Ask Questions in Natural Language")
    if st.session_state.df is None:
        st.info("Upload data in the Auto Analysis tab before running HITL queries.")
    else:
        # Lazily initialize the NL → SQL engine and orchestrator
        if st.session_state.query_engine is None:
            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key:
                st.error("❌ OPENAI_API_KEY not found. Set it in your .env to use Q&A.")
            else:
                with st.spinner("🤖 Initializing Q&A engine..."):
                    engine = NaturalLanguageQueryEngine(api_key)
                    engine.load_data(st.session_state.df)
                    st.session_state.query_engine = engine
                    
                    # Initialize orchestrator
                    st.session_state.orchestrator = QueryOrchestrator(
                        query_engine=engine,
                        interpreter=st.session_state.interpreter
                    )

        user_query = st.text_input(
            "🔍 Ask a question about your campaigns",
            placeholder="e.g., sort by funnel performance, show top campaigns, what are the KPIs",
            key="user_query_input"
        )
        
        # Direct execution only - no interpretation layer
        if st.button("🚀 Ask Question", type="primary", use_container_width=True) and user_query:
            if st.session_state.query_engine:
                with st.spinner("🔄 Generating SQL & running query..."):
                    try:
                        start = time.time()
                        result = st.session_state.query_engine.ask(user_query)
                        exec_time = int((time.time() - start) * 1000)
                        
                        # Extract results
                        sql_text = result.get("sql_query") or result.get("sql") or ""
                        results_df = result.get("results")
                        answer = result.get("answer")
                        
                        # Store results
                        st.session_state.last_result = {
                            "sql": sql_text,
                            "df": results_df,
                            "answer": answer,
                            "model_used": result.get("model_used", "unknown")
                        }
                        
                        # Log to tracker
                        st.session_state.current_query_id = st.session_state.query_tracker.start_query(
                            original_query=user_query,
                            interpretations=[],
                            user_id="analyst",
                            session_id=st.session_state["session_id"],
                        )
                        st.session_state.query_tracker.update_query(
                            query_id=st.session_state.current_query_id,
                            generated_sql=sql_text,
                            execution_time_ms=exec_time,
                            result_count=len(results_df) if isinstance(results_df, pd.DataFrame) else 0,
                        )
                        
                        st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        if "insufficient_quota" in error_msg or "429" in error_msg:
                            st.error("❌ **OpenAI API Quota Exceeded**")
                            st.warning("⚠️ Your OpenAI API key has no credits left.")
                            st.info("**Solutions:**\n1. Add credits at https://platform.openai.com/account/billing\n2. Or use a different API key")
                        elif "authentication_error" in error_msg or "401" in error_msg:
                            st.error("❌ **API Authentication Failed**")
                            st.warning("⚠️ Your API key is invalid or expired.")
                            st.info("**Solutions:**\n1. Check your .env file\n2. Get a new API key from OpenAI or Anthropic")
                        else:
                            st.error(f"❌ Query failed: {error_msg}")
                        
                        import traceback
                        with st.expander("🔍 Error Details"):
                            st.code(traceback.format_exc())
        
        # Display results if available
        if st.session_state.get("last_result"):
            result_data = st.session_state.last_result
            
            st.markdown("### 📊 Results")
            
            # Show which model was used
            if result_data.get("model_used"):
                model_name = result_data["model_used"]
                if "gemini" in model_name.lower():
                    st.success(f"🤖 **Model Used:** {model_name} (FREE)")
                else:
                    st.info(f"🤖 **Model Used:** {model_name}")
            
            with st.expander("🔍 Generated SQL", expanded=False):
                sql_text = result_data.get("sql")
                if sql_text:
                    st.code(sql_text, language="sql")
                else:
                    # No SQL captured (likely due to an error before generation/execution)
                    st.code("-- No SQL was generated or the query failed before SQL could be produced.\n-- Check the error details shown above.", language="sql")

            results_df = result_data.get("df")
            if results_df is not None and isinstance(results_df, pd.DataFrame) and not results_df.empty:
                st.dataframe(result_data["df"], use_container_width=True)
                csv = result_data["df"].to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    "query_results.csv",
                    "text/csv",
                )
            else:
                st.info("No data returned.")

            if result_data.get("answer"):
                st.markdown("### 💡 Insight")
                st.write(result_data["answer"])

            col_fb1, col_fb2, col_fb3 = st.columns(3)
            if col_fb1.button("👍 Helpful"):
                st.session_state.query_tracker.add_feedback(
                    st.session_state.current_query_id,
                    feedback=1,
                )
                st.success("Thanks for your feedback!")
            if col_fb2.button("😐 Neutral"):
                st.session_state.query_tracker.add_feedback(
                    st.session_state.current_query_id,
                    feedback=0,
                )
                st.info("Feedback recorded.")
            if col_fb3.button("👎 Needs work"):
                st.session_state.query_tracker.add_feedback(
                    st.session_state.current_query_id,
                    feedback=-1,
                )
                st.warning("We'll work on improving this.")


# ---------------------------------------------------------------------------
# Query history tab
# ---------------------------------------------------------------------------
with tab_history:
    st.markdown("## 📜 Recent Queries")
    query_df = st.session_state.query_tracker.get_all_queries(limit=100)
    if query_df.empty:
        st.info("No queries yet. Run HITL Q&A to populate history.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", len(query_df))
        col2.metric("Successful", len(query_df[query_df["error_message"].isna()]))
        col3.metric("With Feedback", len(query_df[query_df["user_feedback"].notna()]))
        col4.metric(
            "Avg Time",
            f"{query_df['execution_time_ms'].mean():.0f} ms"
            if query_df["execution_time_ms"].notna().any()
            else "N/A",
        )
        query_df["timestamp"] = pd.to_datetime(query_df["timestamp"]).dt.strftime(
            "%Y-%m-%d %H:%M"
        )
        st.dataframe(
            query_df[
                [
                    "timestamp",
                    "original_query",
                    "selected_interpretation",
                    "execution_time_ms",
                    "result_count",
                    "user_feedback",
                ]
            ],
            use_container_width=True,
        )

        st.markdown("### 🔎 Query details")
        query_ids = query_df["query_id"].tolist()
        if query_ids:
            labels = {
                row["query_id"]: f"{row['timestamp']} • {row['original_query'][:80]}"
                for _, row in query_df.iterrows()
            }
            selected_qid = st.selectbox(
                "Select a query to inspect",
                options=query_ids,
                format_func=lambda qid: labels.get(qid, qid),
            )
            if selected_qid:
                trace = st.session_state.query_tracker.get_full_trace(selected_qid)
                if trace:
                    log = trace["log"]
                    interpretations = trace["interpretations"]
                    sample_df = trace["sample_results"]
                    models = trace["models"]

                    st.markdown(f"**Original query:** {log['original_query']}")
                    st.caption(
                        f"Timestamp: {log['timestamp']} • Query ID: {log['query_id']}"
                    )
                    col_a, col_b, col_c, col_d = st.columns(4)
                    exec_ms = log.get("execution_time_ms") or 0
                    col_a.metric("Exec time", f"{exec_ms} ms")
                    col_b.metric("Rows", str(log.get("result_count") or 0))
                    sel_idx = log.get("selected_interpretation_index")
                    if sel_idx is not None:
                        col_c.metric("Selected interpretation", str(sel_idx + 1))
                    else:
                        col_c.metric("Selected interpretation", "None")
                    fb_map = {1: "👍", 0: "😐", -1: "👎"}
                    col_d.metric("Feedback", fb_map.get(log.get("user_feedback"), "—"))

                    left, right = st.columns(2)
                    with left:
                        st.markdown("#### 🧠 Interpretations")
                        if interpretations:
                            for i, interp in enumerate(interpretations):
                                label = interp.get("interpretation", "")
                                prefix = f"{i+1}. {label}"
                                if sel_idx is not None and i == sel_idx:
                                    prefix += " (selected)"
                                st.markdown(f"- {prefix}")
                        else:
                            st.caption("No interpretations stored.")
                    with right:
                        st.markdown("#### 🔍 Generated SQL")
                        st.code(
                            log.get("generated_sql") or "No SQL generated",
                            language="sql",
                        )

                    st.markdown("#### 📊 Sample results")
                    if isinstance(sample_df, pd.DataFrame) and not sample_df.empty:
                        st.dataframe(sample_df, use_container_width=True)
                    else:
                        st.caption("No sample results stored for this query.")

                    st.markdown("#### 🤖 Models used")
                    if models:
                        model_df = pd.DataFrame(models)
                        st.dataframe(model_df, use_container_width=True)
                    else:
                        st.caption("No model usage logged for this query yet.")

                    if log.get("feedback_comment"):
                        st.markdown("#### 💬 User comment")
                        st.write(log["feedback_comment"])


# ---------------------------------------------------------------------------
# Metrics tab
# ---------------------------------------------------------------------------
with tab_metrics:
    st.markdown("## 📈 HITL Performance Analytics")
    query_df = st.session_state.query_tracker.get_all_queries(limit=1000)
    if query_df.empty:
        st.info("Run a few HITL queries to unlock analytics.")
    else:
        interp_accuracy = (
            query_df["selected_interpretation_index"].fillna(-1) == 0
        ).mean() * 100
        st.metric("First Interpretation Selected", f"{interp_accuracy:.1f}%")
        feedback_counts = query_df["user_feedback"].value_counts()
        feedback_df = pd.DataFrame(
            {
                "Feedback": ["👍", "😐", "👎"],
                "Count": [
                    feedback_counts.get(1.0, 0),
                    feedback_counts.get(0.0, 0),
                    feedback_counts.get(-1.0, 0),
                ],
            }
        ).set_index("Feedback")
        st.bar_chart(feedback_df)
        st.markdown("### 🔥 Most common queries")
        st.write(query_df["original_query"].value_counts().head(10))

        st.markdown("### 🤖 Model usage and performance")
        model_df = st.session_state.query_tracker.get_per_model_metrics()
        if model_df.empty:
            st.caption("No model usage logged yet.")
        else:
            st.dataframe(model_df, use_container_width=True)
            if "model_name" in model_df.columns and "usage_count" in model_df.columns:
                chart_df = model_df.set_index("model_name")["usage_count"]
                st.bar_chart(chart_df)


st.markdown("---")
st.caption("PCA Agent • Unified intelligence workspace • Built with ❤️")
