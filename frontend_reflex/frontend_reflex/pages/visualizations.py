import reflex as rx
from ..state import State
from ..components.layout import require_auth
from ..style import metric_card_style

def viz_content():
    return rx.vstack(
        rx.heading("📊 Advanced Visualizations", size="8", margin_bottom="4"),
        
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Custom Builder", value="custom"),
                rx.tabs.trigger("Funnel Analysis", value="funnel"),
                rx.tabs.trigger("Correlation Matrix", value="correlation"),
            ),
            
            # Custom Builder Tab
            rx.tabs.content(
                rx.vstack(
                    rx.card(
                        rx.vstack(
                            rx.heading("Chart Settings", size="4"),
                            rx.hstack(
                                rx.select(
                                    ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart"],
                                    placeholder="Chart Type",
                                    label="Chart Type",
                                    value=State.chart_type,
                                    on_change=State.set_chart_type,
                                ),
                                rx.select(
                                    State.columns,
                                    placeholder="X Axis",
                                    label="X Axis",
                                    value=State.x_axis,
                                    on_change=State.update_x_axis,
                                ),
                                rx.select(
                                    State.columns,
                                    placeholder="Y Axis",
                                    label="Y Axis",
                                    value=State.y_axis,
                                    on_change=State.update_y_axis,
                                ),
                                rx.select(
                                    State.color_options,
                                    placeholder="Color By",
                                    label="Color By",
                                    value=State.color_by,
                                    on_change=State.set_color_by, # Need setter in State? or direct attr
                                ),
                                rx.select(
                                    ["Sum", "Mean", "Count", "Max", "Min"],
                                    placeholder="Aggregation",
                                    label="Aggregation",
                                    value=State.aggregation,
                                    on_change=State.set_aggregation,
                                ),
                                rx.button("Generte Chart", on_click=State.generate_custom_chart),
                                wrap="wrap",
                                spacing="4",
                                align_items="end",
                            ),
                            width="100%",
                            padding="4",
                        ),
                        width="100%",
                        variant="surface",
                    ),
                    rx.cond(
                        State.custom_chart_figure,
                        rx.card(
                            rx.plotly(data=State.custom_chart_figure, height="600px"),
                            width="100%",
                            variant="surface",
                        ),
                        rx.text("Select options and click Generate Chart.", color="gray"),
                    ),
                    spacing="4",
                    width="100%",
                ),
                value="custom",
                padding="4",
            ),
            
            # Funnel Tab
            rx.tabs.content(
                rx.vstack(
                    rx.button("Generate Funnel", on_click=State.generate_funnel_chart),
                    rx.cond(
                        State.funnel_figure,
                        rx.card(
                            rx.plotly(data=State.funnel_figure, height="600px"),
                            width="100%",
                            variant="surface",
                        ),
                        rx.text("No funnel generated yet.", color="gray"),
                    ),
                    spacing="4",
                    width="100%",
                ),
                value="funnel",
                padding="4",
            ),
            
            # Correlation Tab
            rx.tabs.content(
                rx.vstack(
                    rx.button("Generate Matrix", on_click=State.generate_correlation_matrix),
                    rx.cond(
                        State.correlation_figure,
                        rx.card(
                            rx.plotly(data=State.correlation_figure, height="800px"),
                            width="100%",
                            variant="surface",
                        ),
                        rx.text("No matrix generated yet.", color="gray"),
                    ),
                    spacing="4",
                    width="100%",
                ),
                value="correlation",
                padding="4",
            ),
            
            default_value="custom",
            width="100%",
        ),
        width="100%",
        spacing="6",
    )

def visualizations_page():
    return require_auth(viz_content())
