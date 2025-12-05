import reflex as rx
from ..state import State
from ..components.layout import require_auth

def step_indicator(current_step):
    steps = ["Upload", "Map", "Download"]
    return rx.hstack(
        *[
            rx.hstack(
                rx.circle(
                    rx.text(str(i + 1), color="white"),
                    size="8",
                    bg=rx.cond(State.active_step >= i, "violet", "gray"),
                ),
                rx.text(step, weight=rx.cond(State.active_step == i, "bold", "regular")),
                align_items="center",
                spacing="2"
            )
            for i, step in enumerate(steps)
        ],
        spacing="6",
        margin_bottom="6",
        justify="center",
        width="100%"
    )

def upload_step():
    return rx.vstack(
        rx.heading("1. Upload Assets", size="5"),
        rx.text("Upload your data (CSV) and report template (Excel)."),
        
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.text("Source Data", weight="bold"),
                    rx.cond(
                         State.data_uploaded,
                         rx.alert("Data Uploaded", icon="check", color_scheme="green"),
                         rx.upload(
                            rx.vstack(
                                rx.button("Select Data File", color="violet", bg="white", border="1px solid violet"),
                                rx.text("Drag and drop or click to select", font_size="10px"),
                            ),
                            id="data_upload",
                            multiple=False,
                            accept={ "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"], "text/csv": [".csv"] },
                            max_files=1,
                            border="1px dotted violet",
                            padding="4",
                        ) 
                    ),
                    rx.button("Upload Data", on_click=State.handle_upload(rx.upload_files("data_upload"))),
                    width="100%"
                )
            ),
            rx.card(
                rx.vstack(
                    rx.text("Report Template", weight="bold"),
                    rx.cond(
                        State.template_filename,
                        rx.alert(f"Template: {State.template_filename}", icon="check", color_scheme="green"),
                        rx.upload(
                            rx.vstack(
                                rx.button("Select Template", color="violet", bg="white", border="1px solid violet"),
                                rx.text("Drag and drop or click to select", font_size="10px"),
                            ),
                            id="template_upload",
                            multiple=False,
                            accept={ "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"] },
                            max_files=1,
                            border="1px dotted violet",
                            padding="4",
                        )
                    ),
                    rx.button("Upload Template", on_click=State.handle_template_upload(rx.upload_files("template_upload"))),
                    width="100%"
                )
            ),
            columns="2",
            spacing="4",
            width="100%"
        ),
        
        rx.cond(
            State.template_structure,
            rx.button("Next: Map Fields", on_click=lambda: State.set_active_step(1), size="3"),
        )
    )

def mapping_step():
    return rx.vstack(
        rx.heading("2. Map Fields", size="5"),
        rx.text("Map template placeholders to data columns."),
        
        rx.card(
            rx.vstack(
                rx.foreach(
                    State.template_structure["placeholders"],
                    lambda p: rx.hstack(
                        rx.text(p, width="200px", weight="bold"),
                        rx.icon("arrow-right"),
                        rx.select(
                            State.columns, 
                            placeholder="Select data column...",
                            on_change=lambda val: State.set_mapping(p, val)
                        ),
                        width="100%",
                        align_items="center"
                    )
                ),
                width="100%",
                spacing="4"
            )
        ),
        
        rx.hstack(
            rx.button("Back", on_click=lambda: State.set_active_step(0), variant="soft"),
            rx.button("Generate Report", on_click=State.generate_report, loading=State.is_generating, size="3"),
            spacing="4"
        )
    )

def download_step():
    return rx.vstack(
        rx.center(
            rx.vstack(
                rx.icon("check-circle", size=64, color="green"),
                rx.heading("Report Generated!", size="6"),
                rx.text("Your report is ready for download."),
                rx.button("Download Report (Simulated)", variant="outline"),
                rx.button("Start Over", on_click=State.reset, variant="ghost"),
                spacing="4",
                align_items="center"
            )
        ),
        padding_y="12"
    )

def reporting_content():
    return rx.vstack(
        rx.heading("📊 Automated Reporting", size="8"),
        step_indicator(State.active_step),
        
        rx.cond(
            State.active_step == 0,
            upload_step(),
            rx.cond(
                State.active_step == 1,
                mapping_step(),
                download_step()
            )
        ),
        
        width="100%",
        spacing="6"
    )

def reporting_page():
    return require_auth(reporting_content())
