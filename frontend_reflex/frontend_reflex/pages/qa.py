import reflex as rx
from ..state import State
from ..components.layout import require_auth

def qa_content():
    return rx.vstack(
        rx.heading("💬 Q&A", size="8"),
        rx.text("Ask questions about your data in natural language."),
        
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text("Query Mode:"),
                    rx.switch(
                        checked=State.is_knowledge_mode,
                        on_change=State.toggle_knowledge_mode
                    ),
                    rx.cond(
                        State.is_knowledge_mode,
                        rx.badge("Knowledge Base (RAG)", color_scheme="violet"),
                        rx.badge("Data (SQL)", color_scheme="blue")
                    ),
                    align_items="center",
                    spacing="2"
                ),

                rx.text_area(
                    placeholder="e.g., What is the total spend by platform?",
                    value=State.question,
                    on_change=State.set_question,
                    width="100%",
                ),
                rx.hstack(
                    rx.button("Ask", on_click=State.ask_question, width="100%"),
                    rx.button("Clear History", on_click=State.clear_history, variant="soft"),
                    width="100%",
                ),
                gap="4",
            ),
            width="100%",
        ),
        
        rx.heading("History", size="6"),
        rx.foreach(
            State.chat_history,
            lambda chat: rx.card(
                rx.vstack(
                    rx.text(chat["question"], weight="bold"),
                    rx.divider(),
                    rx.text(chat["answer"]),
                    rx.cond(
                        chat["sql"],
                        rx.code(chat["sql"], language="sql")
                    ),
                    spacing="2",
                ),
                margin_bottom="4",
                width="100%",
            ),
        ),
        
        spacing="6",
        width="100%",
    )

def qa_page():
    return require_auth(qa_content())
