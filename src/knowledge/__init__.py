"""
Knowledge Module
Enables PCA Agent to learn from URLs, YouTube videos, and PDFs
"""
from .knowledge_ingestion import KnowledgeIngestion
from .enhanced_reasoning import EnhancedReasoningEngine

__all__ = ['KnowledgeIngestion', 'EnhancedReasoningEngine']
