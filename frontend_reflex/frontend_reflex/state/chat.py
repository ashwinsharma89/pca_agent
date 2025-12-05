import reflex as rx
from typing import List, Dict, Any
from .viz import VizState

class ChatState(VizState):
    """State for Q&A / Chat."""
    
    question: str = ""
    is_knowledge_mode: bool = False
    chat_history: List[Dict[str, Any]] = []

    
    def set_question(self, value: str):
        self.question = value
        
    def toggle_knowledge_mode(self, value: bool):
        self.is_knowledge_mode = value

    def ask_question(self):

        """Process the natural language question."""
        if not self.question:
            return
            
        if not hasattr(self, "_df") or self._df is None:
            return rx.window_alert("Please upload data first.")
            
        try:
            # KNOWLEDGE MODE (RAG)
            if self.is_knowledge_mode:
                 # TODO: Implement actual vector search if needed.
                 # For now, we simulate RAG by searching the static knowledge base
                 # or using an LLM to answer general questions if no specific match.
                 from src.knowledge.causal_kb_rag import get_knowledge_base
                 kb = get_knowledge_base()
                 
                 # Basic keyword search simulation for MVP
                 q_lower = self.question.lower()
                 answer = "I checked the Knowledge Base."
                 
                 if "roas" in q_lower:
                     info = kb.knowledge['metrics'].get('ROAS', {})
                     answer = f"**ROAS Insight:**\n\nTraditional: {info.get('traditional')}\nCausal: {info.get('causal')}\n\n*{info.get('interpretation')}*"
                 elif "cpa" in q_lower:
                     info = kb.knowledge['metrics'].get('CPA', {})
                     answer = f"**CPA Insight:**\n\nTraditional: {info.get('traditional')}\nCausal: {info.get('causal')}\n\n*{info.get('interpretation')}*"
                 elif "ab test" in q_lower or "experiment" in q_lower:
                     info = kb.knowledge['methods'].get('ab_testing', {})
                     answer = f"**A/B Testing:**\n\nIdeally used for: {', '.join(info.get('when_to_use', []))}.\n\nPros: {', '.join(info.get('pros', []))}"
                 else:
                     answer = "I can answer questions about ROAS, CPA, A/B Testing, DiD, etc. based on our Causal Knowledge Base."
                     
                 self.chat_history.append({
                    "question": self.question,
                    "answer": answer,
                    "sql": "N/A (Knowledge Query)",
                    "table_result": ""
                 })
                 self.question = ""
                 return

            # DATA MODE (SQL)
            # Fix import path if needed (it was correct in view_file)
            from src.query_engine.nl_to_sql import NaturalLanguageQueryEngine
            import os
            
            api_key = os.getenv('OPENAI_API_KEY', '')
            engine = NaturalLanguageQueryEngine(api_key)
            # Use filtered_df
            df = self.filtered_df
            if df is not None:
                engine.load_data(df)
            else:
                return rx.window_alert("No data to query.")
            
            result = engine.ask(self.question)
            
            self.chat_history.append({
                "question": self.question,
                "answer": result.get('answer', 'No answer generated.'),
                "sql": result.get('sql_query', ''),
                "table_result": str(result.get('results', ''))
            })
            
            self.question = ""
            
        except Exception as e:
            print(f"QA Error: {e}")
            return rx.window_alert(f"Error: {str(e)}")
            
    def clear_history(self):
        self.chat_history = []
