import reflex as rx
from ..state import State
from ..components.layout import require_auth

def analysis_content():
    return rx.vstack(
        rx.heading("🧠 AI Analysis", size="8"),
        
        # Controls
        rx.card(
            rx.hstack(
                rx.vstack(
                    rx.text("Configuration", weight="bold"),
                    rx.checkbox("Use RAG Knowledge Base", checked=State.use_rag), # Note: State vars binding to be checked
                    rx.checkbox("Include Industry Benchmarks", checked=State.include_benchmarks),
                    align_items="start",
                ),
                rx.spacer(),
                rx.button(
                    "Run AI Analysis",
                    on_click=State.run_analysis,
                    loading=State.is_analyzing,
                    size="3",
                ),
                width="100%",
                padding="4",
            ),
            width="100%",
        ),
        
        rx.cond(
            State.analysis_complete,
            rx.vstack(
                rx.heading("📊 Executive Summary", size="6"),
                rx.card(rx.markdown(State.executive_summary)),
                
                rx.heading("💡 Key Insights", size="6"),
                rx.foreach(
                    State.insights,
                    lambda insight: rx.card(rx.text(insight), margin_bottom="2")
                ),
                
                rx.heading("🎯 Recommendations", size="6"),
                rx.foreach(
                    State.recommendations,
                    lambda rec: rx.card(rx.text(rec), margin_bottom="2", bg=rx.color("blue", 2))
                ),
                
                spacing="5",
                width="100%",
            ),
            rx.text("Run analysis to see results.")
        ),
        
        spacing="6",
        width="100%",
    )

def analysis():
    return require_auth(analysis_content())
