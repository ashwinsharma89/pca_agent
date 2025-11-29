"""
Channel-Specific Intelligence Layer
Specialized agents for different advertising channels
"""

from .base_specialist import BaseChannelSpecialist
from .search_agent import SearchChannelAgent
from .social_agent import SocialChannelAgent
from .programmatic_agent import ProgrammaticAgent

__all__ = [
    'BaseChannelSpecialist',
    'SearchChannelAgent',
    'SocialChannelAgent',
    'ProgrammaticAgent'
]
