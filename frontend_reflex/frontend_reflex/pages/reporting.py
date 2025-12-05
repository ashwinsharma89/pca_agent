import reflex as rx
from ..state import State
from ..components.layout import require_auth

def reporting_content():
    return rx.vstack(
        rx.heading("📊 Automated Reporting", size="8"),
        rx.text("Reporting features are under development."),
        rx.callout(
            "This page will include Template Upload, Field Mapping, and Report Generation.",
            icon="info"
        ),
        width="100%",
        spacing="6"
    )

def reporting_page():
    return require_auth(reporting_content())
