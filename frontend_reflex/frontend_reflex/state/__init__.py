from .diagnostics import DiagnosticsState
from .predictive import PredictiveState
from .reporting import ReportingState

class State(PredictiveState, DiagnosticsState, ReportingState):
    """The Main App State."""
    pass
