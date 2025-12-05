import reflex as rx
from ..state import State
from ..components.layout import require_auth
import plotly.graph_objects as go

def prediction_tab():
    return rx.vstack(
        rx.heading("Campaign Success Predictor", size="5"),
        rx.text("Simulate campaign parameters to predict success probability."),
        
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.text("Campaign Parameters", weight="bold"),
                    rx.input(placeholder="Campaign Name", value=State.campaign_name, on_change=State.set_campaign_name),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Budget ($)", size="1"),
                            rx.input(value=State.budget.to_string(), on_change=State.set_budget, type="number"),
                        ),
                        rx.vstack(
                            rx.text("Duration (Days)", size="1"),
                            rx.slider(min=7, max=90, default_value=[30], on_change=State.set_duration),
                            rx.text(State.duration),
                        ),
                    ),
                    rx.vstack(
                         rx.text("Channels", size="1"),
                         rx.checkbox("Meta", default_checked=True, on_change=lambda x: State.set_selected_channels(x, "Meta")),
                         rx.checkbox("Google", default_checked=True, on_change=lambda x: State.set_selected_channels(x, "Google")),
                         rx.checkbox("LinkedIn", on_change=lambda x: State.set_selected_channels(x, "LinkedIn")),
                         rx.checkbox("TikTok", on_change=lambda x: State.set_selected_channels(x, "TikTok")),
                    ),
                    rx.select(["video", "image", "carousel"], value=State.creative_type, on_change=State.set_creative_type, label="Creative"),
                    rx.select(["conversion", "awareness", "traffic"], value=State.objective, on_change=State.set_objective, label="Objective"),
                    
                    rx.button("Predict Success", on_click=State.run_prediction, loading=State.is_predicting, width="100%"),
                    spacing="4"
                )
            ),
            rx.card(
                rx.cond(
                    State.prediction_result,
                    rx.vstack(
                        rx.circular_progress(
                            value=State.prediction_result["success_probability"], 
                            size="40px", 
                            color_scheme=rx.cond(State.prediction_result["success_probability"] > 70, "green", "orange")
                        ),
                        rx.heading(f"{State.prediction_result['success_probability']}% Success Probability", size="6"),
                        rx.badge(State.prediction_result["confidence_level"] + " Confidence"),
                        rx.divider(),
                        rx.text("Key Drivers:", weight="bold"),
                        rx.foreach(
                            State.prediction_result["key_drivers"],
                            lambda x: rx.text(f"• {x['feature']}: {x['impact']}")
                        ),
                        rx.divider(),
                        rx.text("Recommendations:", weight="bold"),
                        rx.foreach(
                            State.prediction_result["recommendations"],
                            lambda x: rx.alert(x['message'], icon="info")
                        ),
                        spacing="4"
                    ),
                    rx.center(rx.text("Run prediction to see results.", color="gray"))
                )
            ),
            columns="2",
            spacing="4",
            width="100%"
        )
    )

def optimization_tab():
    return rx.vstack(
        rx.heading("Budget Allocation Optimizer", size="5"),
        rx.text("Optimize budget across channels using historical ROAS."),
        
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.text("Optimization Settings", weight="bold"),
                    rx.input(label="Total Budget", value=State.opt_budget.to_string(), on_change=State.set_opt_budget, type="number"),
                    rx.select(["roas", "conversions", "revenue"], label="Goal", value=State.opt_goal, on_change=State.set_opt_goal),
                    rx.input(label="Min Spend / Channel", value=State.opt_min_spend.to_string(), on_change=State.set_opt_min_spend, type="number"),
                    rx.button("Optimize Allocation", on_click=State.run_optimization, loading=State.is_optimizing, width="100%"),
                    spacing="4"
                )
            ),
            rx.card(
                 rx.cond(
                    State.optimization_result,
                    rx.vstack(
                        rx.heading("Recommended Allocation", size="4"),
                        rx.recharts.pie_chart(
                            rx.recharts.pie(
                                data=State.optimization_result['allocation'],
                                data_key="recommended_budget",
                                name_key="channel", # Assuming we transform dict to list of dicts or handle mapping
                                cx="50%", cy="50%", outer_radius=80, fill="#8884d8", label=True
                            ),
                            height=300
                        ),
                        # Note: Simple text fallback for MVP if pie chart data binding is tricky with complex dicts
                         rx.foreach(
                            State.optimization_result['chart_labels'], # Just keys
                            lambda x: rx.text(x) # Placeholder, ideally we show table
                        ),
                        rx.metric("Expected ROAS", State.optimization_result['overall_metrics']['expected_overall_roas']),
                        rx.metric("Expected Revenue", State.optimization_result['overall_metrics']['expected_total_revenue']),
                        spacing="4"
                    ),
                    rx.center(rx.text("Run optimization to see results.", color="gray"))
                )
            ),
            columns="2",
            spacing="4",
            width="100%"
        )
    )

def training_tab():
    return rx.vstack(
        rx.heading("Model Training", size="5"),
        rx.text("Train models using currently uploaded historical data."),
        
        rx.card(
             rx.vstack(
                rx.hstack(
                    rx.input(label="Target ROAS", value=State.target_roas.to_string(), on_change=State.set_target_roas, type="number"),
                    rx.input(label="Target CPA", value=State.target_cpa.to_string(), on_change=State.set_target_cpa, type="number"),
                ),
                rx.button("Train Model", on_click=State.train_model, loading=State.is_training),
                rx.cond(
                    State.training_metrics,
                    rx.vstack(
                        rx.heading("Training Results", size="4"),
                        rx.text(f"Accuracy: {State.training_metrics['test_accuracy']}"),
                         rx.text(f"Samples: {State.training_metrics['training_samples']}"),
                    )
                ),
                spacing="4"
             )
        )
    )

def predictive_content():
    return rx.vstack(
        rx.heading("🔮 Predictive Analytics", size="8"),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Success Predictor", value="predict"),
                rx.tabs.trigger("Budget Optimizer", value="optimize"),
                rx.tabs.trigger("Model Training", value="train"),
            ),
            rx.tabs.content(prediction_tab(), value="predict"),
            rx.tabs.content(optimization_tab(), value="optimize"),
            rx.tabs.content(training_tab(), value="train"),
            default_value="predict",
            width="100%"
        ),
        width="100%",
        spacing="6"
    )

def predictive_page():
    return require_auth(predictive_content())
