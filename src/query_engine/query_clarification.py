"""
Query Clarification Module - Human-in-the-Loop
Generates multiple interpretations of user queries for clarification
"""
import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from anthropic import Anthropic
import logging

logger = logging.getLogger(__name__)


class QueryClarifier:
    """Generates multiple interpretations of natural language queries."""
    
    def __init__(self, api_key: str = None, use_anthropic: bool = False):
        """Initialize the query clarifier."""
        self.use_anthropic = use_anthropic
        
        if use_anthropic:
            self.client = Anthropic(api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))
            self.model = "claude-3-5-sonnet-20241022"
        else:
            self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
            self.model = "gpt-4"
    
    def generate_interpretations(
        self, 
        query: str, 
        schema_info: Dict[str, Any],
        num_interpretations: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple interpretations of a user query.
        
        Args:
            query: The natural language query from user
            schema_info: Information about available tables and columns
            num_interpretations: Number of interpretations to generate (default 5)
            
        Returns:
            List of interpretation dictionaries with:
            - interpretation: Human-readable interpretation
            - reasoning: Why this interpretation makes sense
            - confidence: Confidence score (0-1)
            - sql_hint: Hint about what SQL would look like
        """
        
        prompt = f"""You are a data analyst helping clarify what a user wants to know about their campaign data.

Available Data Schema:
{json.dumps(schema_info, indent=2)}

User Query: "{query}"

Generate {num_interpretations} different possible interpretations of what the user might be asking.
Each interpretation should be:
1. Specific and actionable
2. Based on the available data
3. Realistic for campaign analysis

For each interpretation, provide:
- A clear, specific interpretation statement
- Brief reasoning for why this interpretation makes sense
- A confidence score (0.0 to 1.0)
- A hint about what the SQL query would focus on

Return ONLY a JSON array with this structure:
[
  {{
    "interpretation": "Show campaigns where total spend exceeds $10,000",
    "reasoning": "User said 'high spend' which typically means above a threshold",
    "confidence": 0.85,
    "sql_hint": "Filter on SUM(Spend) > 10000"
  }},
  ...
]

Order interpretations by confidence score (highest first).
Make interpretations diverse - cover different aspects like thresholds, comparisons, trends, rankings, etc.
"""

        try:
            if self.use_anthropic:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful data analyst assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                content = response.choices[0].message.content
            
            # Extract JSON from response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            interpretations = json.loads(content)
            
            # Add index to each interpretation
            for i, interp in enumerate(interpretations):
                interp['index'] = i
            
            logger.info(f"Generated {len(interpretations)} interpretations for query: {query}")
            return interpretations
            
        except Exception as e:
            logger.error(f"Error generating interpretations: {e}")
            # Return a default interpretation
            return [{
                "index": 0,
                "interpretation": f"Analyze: {query}",
                "reasoning": "Using original query as-is",
                "confidence": 0.5,
                "sql_hint": "Direct query translation"
            }]
    
    def refine_interpretation(
        self,
        original_query: str,
        selected_interpretation: Dict[str, Any],
        user_feedback: str = None
    ) -> str:
        """
        Refine the selected interpretation based on user feedback.
        
        Args:
            original_query: Original user query
            selected_interpretation: The interpretation user selected
            user_feedback: Optional additional feedback from user
            
        Returns:
            Refined query string
        """
        
        if not user_feedback:
            return selected_interpretation['interpretation']
        
        prompt = f"""Refine this query interpretation based on user feedback.

Original Query: "{original_query}"
Selected Interpretation: "{selected_interpretation['interpretation']}"
User Feedback: "{user_feedback}"

Provide a refined, more specific interpretation that incorporates the user's feedback.
Return ONLY the refined interpretation as a single clear statement.
"""

        try:
            if self.use_anthropic:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}]
                )
                refined = response.content[0].text.strip()
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                refined = response.choices[0].message.content.strip()
            
            return refined
            
        except Exception as e:
            logger.error(f"Error refining interpretation: {e}")
            return selected_interpretation['interpretation']


def format_interpretations_for_display(interpretations: List[Dict[str, Any]]) -> str:
    """
    Format interpretations for display in Streamlit.
    
    Args:
        interpretations: List of interpretation dictionaries
        
    Returns:
        Formatted string for display
    """
    output = []
    for i, interp in enumerate(interpretations, 1):
        confidence_bar = "🟢" * int(interp['confidence'] * 5)
        output.append(f"""
**Option {i}** {confidence_bar} ({interp['confidence']:.0%} confidence)

**What it means:** {interp['interpretation']}

**Why:** {interp['reasoning']}

**SQL Focus:** {interp['sql_hint']}
""")
    
    return "\n---\n".join(output)
