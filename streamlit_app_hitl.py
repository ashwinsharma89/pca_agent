"""
Enhanced Streamlit App with Human-in-the-Loop and Traceability
Includes query clarification and evaluation metrics
"""
import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os

# Import existing modules
from src.query_engine.nl_to_sql import NaturalLanguageQueryEngine
from src.query_engine.query_clarification import QueryClarifier, format_interpretations_for_display
from src.evaluation.query_tracker import QueryTracker
import logging

# Setup
logger = logging.getLogger(__name__)
st.set_page_config(page_title="PCA Agent - Enhanced Q&A", page_icon="🤖", layout="wide")

# Initialize session state
if 'query_tracker' not in st.session_state:
    st.session_state.query_tracker = QueryTracker()

if 'clarifier' not in st.session_state:
    st.session_state.clarifier = QueryClarifier(use_anthropic=True)

if 'current_query_id' not in st.session_state:
    st.session_state.current_query_id = None

if 'interpretations' not in st.session_state:
    st.session_state.interpretations = None

if 'selected_interpretation' not in st.session_state:
    st.session_state.selected_interpretation = None

if 'query_engine' not in st.session_state:
    st.session_state.query_engine = None

if 'df' not in st.session_state:
    st.session_state.df = None

# Header
st.title("🤖 PCA Agent - Enhanced Q&A")
st.markdown("**With Human-in-the-Loop Query Clarification & Full Traceability**")

# Sidebar
with st.sidebar:
    st.header("📊 System Metrics")
    
    metrics = st.session_state.query_tracker.get_metrics_summary()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Queries", metrics['total_queries'])
        st.metric("Success Rate", f"{metrics['success_rate']:.1f}%")
    with col2:
        st.metric("Avg Feedback", f"{metrics['avg_feedback']:.2f}")
        st.metric("Interpretation Accuracy", f"{metrics['interpretation_accuracy']:.1f}%")
    
    st.metric("Avg Response Time", f"{metrics['avg_execution_time_ms']:.0f}ms")
    
    st.markdown("---")
    
    if st.button("📥 Export Query Logs"):
        export_path = st.session_state.query_tracker.export_to_csv()
        st.success(f"Exported to {export_path}")
    
    if st.button("📈 View Analytics Dashboard"):
        st.info("Analytics dashboard coming soon!")

# Main content
tab1, tab2, tab3 = st.tabs(["💬 Ask Questions", "📊 Query History", "📈 Analytics"])

with tab1:
    st.header("Ask Questions About Your Campaign Data")
    
    # File upload
    uploaded_file = st.file_uploader("Upload Campaign Data (CSV)", type=['csv'])
    
    if uploaded_file:
        # Load data
        if st.session_state.df is None:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.session_state.query_engine = NaturalLanguageQueryEngine()
            st.session_state.query_engine.load_data(st.session_state.df)
            st.success(f"✅ Loaded {len(st.session_state.df)} rows")
        
        # Show data preview
        with st.expander("📋 Data Preview"):
            st.dataframe(st.session_state.df.head())
        
        st.markdown("---")
        
        # Query input
        user_query = st.text_input(
            "🔍 Ask a question about your campaigns:",
            placeholder="e.g., Show me campaigns with high spend",
            key="user_query_input"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            ask_button = st.button("🚀 Ask", type="primary", use_container_width=True)
        
        if ask_button and user_query:
            # Step 1: Generate interpretations
            with st.spinner("🤔 Understanding your query..."):
                schema_info = {
                    "table": "campaigns",
                    "columns": list(st.session_state.df.columns),
                    "sample_data": st.session_state.df.head(3).to_dict('records')
                }
                
                interpretations = st.session_state.clarifier.generate_interpretations(
                    user_query,
                    schema_info,
                    num_interpretations=5
                )
                
                st.session_state.interpretations = interpretations
                
                # Start tracking
                st.session_state.current_query_id = st.session_state.query_tracker.start_query(
                    original_query=user_query,
                    interpretations=interpretations,
                    user_id="demo_user",
                    session_id=st.session_state.get('session_id', 'default_session')
                )
            
            # Step 2: Show interpretations for user selection
            st.markdown("### 🎯 Which interpretation best matches what you want?")
            st.markdown("*Select the option that closest matches your intent:*")
            
            # Display interpretations as radio buttons
            interpretation_options = [
                f"**{i+1}.** {interp['interpretation']} (Confidence: {interp['confidence']:.0%})"
                for i, interp in enumerate(interpretations)
            ]
            
            selected_index = st.radio(
                "Select interpretation:",
                range(len(interpretation_options)),
                format_func=lambda x: interpretation_options[x],
                key="interpretation_radio"
            )
            
            # Show details of selected interpretation
            selected_interp = interpretations[selected_index]
            with st.expander("📝 Details of selected interpretation"):
                st.markdown(f"**Reasoning:** {selected_interp['reasoning']}")
                st.markdown(f"**SQL Focus:** {selected_interp['sql_hint']}")
            
            # Optional: User can provide additional feedback
            additional_feedback = st.text_input(
                "💬 Any additional clarification? (optional)",
                placeholder="e.g., Only show last 30 days",
                key="additional_feedback"
            )
            
            # Execute button
            if st.button("✅ Execute Query", type="primary"):
                start_time = time.time()
                
                try:
                    # Update tracker with selection
                    st.session_state.query_tracker.update_query(
                        query_id=st.session_state.current_query_id,
                        selected_interpretation_index=selected_index,
                        selected_interpretation=selected_interp['interpretation']
                    )
                    
                    # Refine if additional feedback provided
                    if additional_feedback:
                        refined_query = st.session_state.clarifier.refine_interpretation(
                            user_query,
                            selected_interp,
                            additional_feedback
                        )
                    else:
                        refined_query = selected_interp['interpretation']
                    
                    # Generate and execute SQL
                    with st.spinner("🔄 Generating and executing SQL..."):
                        result = st.session_state.query_engine.ask(refined_query)
                        
                        execution_time = int((time.time() - start_time) * 1000)
                        
                        # Update tracker
                        st.session_state.query_tracker.update_query(
                            query_id=st.session_state.current_query_id,
                            generated_sql=result.get('sql', ''),
                            execution_time_ms=execution_time,
                            result_count=len(result.get('data', []))
                        )
                    
                    # Show results
                    st.markdown("### 📊 Results")
                    
                    # Show SQL (collapsible)
                    with st.expander("🔍 View Generated SQL"):
                        st.code(result.get('sql', ''), language='sql')
                    
                    # Show data
                    if 'data' in result and len(result['data']) > 0:
                        result_df = pd.DataFrame(result['data'])
                        st.dataframe(result_df, use_container_width=True)
                        
                        # Download button
                        csv = result_df.to_csv(index=False)
                        st.download_button(
                            "📥 Download Results",
                            csv,
                            "query_results.csv",
                            "text/csv"
                        )
                    else:
                        st.info("No results found")
                    
                    # Show answer
                    if 'answer' in result:
                        st.markdown("### 💡 Insights")
                        st.markdown(result['answer'])
                    
                    # Feedback section
                    st.markdown("---")
                    st.markdown("### 📝 How helpful was this result?")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("👍 Helpful", use_container_width=True):
                            st.session_state.query_tracker.add_feedback(
                                st.session_state.current_query_id,
                                feedback=1
                            )
                            st.success("Thanks for your feedback!")
                    with col2:
                        if st.button("😐 Neutral", use_container_width=True):
                            st.session_state.query_tracker.add_feedback(
                                st.session_state.current_query_id,
                                feedback=0
                            )
                            st.success("Thanks for your feedback!")
                    with col3:
                        if st.button("👎 Not Helpful", use_container_width=True):
                            st.session_state.query_tracker.add_feedback(
                                st.session_state.current_query_id,
                                feedback=-1
                            )
                            st.success("Thanks for your feedback!")
                    
                    feedback_comment = st.text_area("Additional comments (optional):")
                    if st.button("Submit Comment"):
                        st.session_state.query_tracker.add_feedback(
                            st.session_state.current_query_id,
                            feedback=0,
                            comment=feedback_comment
                        )
                        st.success("Comment submitted!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    
                    # Log error
                    st.session_state.query_tracker.update_query(
                        query_id=st.session_state.current_query_id,
                        error_message=str(e)
                    )

with tab2:
    st.header("📊 Query History")
    
    # Get recent queries
    query_df = st.session_state.query_tracker.get_all_queries(limit=50)
    
    if len(query_df) > 0:
        # Show summary stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Queries", len(query_df))
        with col2:
            successful = len(query_df[query_df['error_message'].isna()])
            st.metric("Successful", successful)
        with col3:
            with_feedback = len(query_df[query_df['user_feedback'].notna()])
            st.metric("With Feedback", with_feedback)
        with col4:
            avg_time = query_df['execution_time_ms'].mean()
            st.metric("Avg Time", f"{avg_time:.0f}ms" if not pd.isna(avg_time) else "N/A")
        
        st.markdown("---")
        
        # Show query table
        display_df = query_df[[
            'timestamp', 'original_query', 'selected_interpretation',
            'execution_time_ms', 'result_count', 'user_feedback'
        ]].copy()
        
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(display_df, use_container_width=True)
        
    else:
        st.info("No queries yet. Start asking questions in the 'Ask Questions' tab!")

with tab3:
    st.header("📈 Analytics Dashboard")
    
    query_df = st.session_state.query_tracker.get_all_queries(limit=999)
    
    if len(query_df) > 0:
        # Interpretation accuracy over time
        st.subheader("🎯 Interpretation Accuracy")
        interpretation_accuracy = (query_df['selected_interpretation_index'] == 0).mean() * 100
        st.metric("First Interpretation Selected", f"{interpretation_accuracy:.1f}%")
        
        # Feedback distribution
        st.subheader("📊 Feedback Distribution")
        feedback_counts = query_df['user_feedback'].value_counts()
        feedback_df = pd.DataFrame({
            'Feedback': ['Thumbs Up', 'Neutral', 'Thumbs Down'],
            'Count': [
                feedback_counts.get(1.0, 0),
                feedback_counts.get(0.0, 0),
                feedback_counts.get(-1.0, 0)
            ]
        })
        st.bar_chart(feedback_df.set_index('Feedback'))
        
        # Most common queries
        st.subheader("🔥 Most Common Queries")
        top_queries = query_df['original_query'].value_counts().head(10)
        st.dataframe(top_queries, use_container_width=True)
        
    else:
        st.info("No data yet. Start using the system to see analytics!")

# Footer
st.markdown("---")
st.markdown("**PCA Agent Enhanced** | Human-in-the-Loop + Full Traceability | Built with ❤️")
