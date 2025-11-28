"""
Automated Analytics Engine with Media Domain Expertise
Generates insights and recommendations automatically from campaign data
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from openai import OpenAI
import google.generativeai as genai
from loguru import logger
import json
import os
import re
from dotenv import load_dotenv
from ..data_processing import MediaDataProcessor


# Ensure environment variables from .env are available when this module loads
load_dotenv()


class MediaAnalyticsExpert:
    """AI-powered media analytics expert that generates insights automatically."""
    
    # Column name mappings for flexibility
    COLUMN_MAPPINGS = {
        'spend': ['Spend', 'Total Spent', 'Total_Spent', 'Cost'],
        'conversions': ['Conversions', 'Site Visit', 'Site_Visit', 'Conv'],
        'revenue': ['Revenue', 'Conversion Value', 'Conversion_Value'],
        'impressions': ['Impressions', 'Impr'],
        'clicks': ['Clicks', 'Click'],
        'platform': ['Platform', 'Channel', 'Source'],
        'campaign': ['Campaign', 'Campaign_Name', 'Campaign Name', 'Campaign_Name_Full']
    }
    
    def __init__(self, api_key: Optional[str] = None, use_anthropic: Optional[bool] = None):
        """Initialize the analytics expert."""
        # Determine which LLM to use
        if use_anthropic is None:
            use_anthropic = os.getenv('USE_ANTHROPIC', 'false').lower() == 'true'
        
        self.use_anthropic = use_anthropic
        
        if self.use_anthropic:
            self.anthropic_api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            if self.anthropic_api_key:
                # Don't use the SDK - we'll call the API directly via HTTP
                self.client = None  # We'll use requests library instead
                self.model = (
                    os.getenv('DEFAULT_ANTHROPIC_MODEL')
                    or os.getenv('DEFAULT_LLM_MODEL')
                    or 'claude-3-5-sonnet-20241022'
                )
                logger.info(f"✅ Initialized with Anthropic Claude (HTTP API): {self.model}")
            else:
                logger.warning("No Anthropic API key found. Falling back to OpenAI.")
                self.use_anthropic = False
                self.anthropic_api_key = None

        if not self.use_anthropic:
            openai_key = api_key or os.getenv('OPENAI_API_KEY')
            if not openai_key:
                raise ValueError("OPENAI_API_KEY not found")
            self.client = OpenAI(api_key=openai_key)
            self.model = (
                os.getenv('DEFAULT_OPENAI_MODEL')
                or os.getenv('OPENAI_MODEL')
                or 'gpt-4o-mini'
            )
            logger.info(f"Initialized with OpenAI: {self.model}")
        
        # Initialize Gemini client as a fallback
        self.gemini_client = None
        google_key = os.getenv('GOOGLE_API_KEY')
        if google_key:
            try:
                genai.configure(api_key=google_key)
                self.gemini_client = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("Gemini 2.0 Flash client initialized successfully for fallback.")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini client: {e}")
        
        self.insights = []
        self.recommendations = []
        self.processor = MediaDataProcessor()
        logger.info("Initialized MediaAnalyticsExpert with advanced data processor")
    
    def _get_column(self, df: pd.DataFrame, metric: str) -> Optional[str]:
        """
        Get the actual column name from DataFrame based on metric type.
        
        Args:
            df: DataFrame to search
            metric: Metric type (e.g., 'spend', 'conversions')
            
        Returns:
            Actual column name or None if not found
        """
        if metric.lower() in self.COLUMN_MAPPINGS:
            for col_name in self.COLUMN_MAPPINGS[metric.lower()]:
                if col_name in df.columns:
                    return col_name
        return None

    @staticmethod
    def _strip_italics(text: str) -> str:
        """Comprehensive formatting cleanup with regex to fix common LLM formatting issues.
        
        Nuclear approach: Remove all formatting and ensure perfect spacing around numbers.
        """
        if not isinstance(text, str):
            return text
        
        # NUCLEAR PASS 1: Remove ALL formatting characters completely
        text = re.sub(r'\*+', '', text)  # Remove all asterisks
        text = re.sub(r'_+', '', text)   # Remove all underscores
        
        # NUCLEAR PASS 2: Fix ALL number-related spacing (most aggressive)
        # This will run MULTIPLE times to catch all edge cases
        
        for _ in range(3):  # Run 3 times to catch cascading issues
            # CRITICAL: Fix K/M/B abbreviations FIRST (before general digit-letter fix)
            # This handles cases like "973K" followed by text
            text = re.sub(r'(\d)([KMB])([a-z])', r'\1\2 \3', text, flags=re.IGNORECASE)
            text = re.sub(r'(\d)([KMB])([A-Z])', r'\1\2 \3', text)
            
            # Fix digit followed by letter (but preserve K/M/B)
            text = re.sub(r'(\d)([A-DF-JL-Z])([a-z])', r'\1 \2\3', text)  # Skip K
            text = re.sub(r'(\d)([a-jl-z])', r'\1 \2', text)  # Lowercase (skip k)
            
            # Fix letter followed by digit
            text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)
            
            # Fix comma-separated numbers followed by letters
            text = re.sub(r'(\d,\d{3})([A-Za-z])', r'\1 \2', text)
            
            # Fix decimal numbers followed by letters
            text = re.sub(r'(\d\.\d+)([A-Za-z])', r'\1 \2', text)
            
            # Fix uppercase abbreviations (CPC, CTR, ROAS, etc.)
            text = re.sub(r'(\d)([A-Z]{2,})', r'\1 \2', text)
        
        # PASS 3: Fix symbols (keep them attached to numbers)
        text = re.sub(r'([\$€£¥])\s+(\d)', r'\1\2', text)  # $100 not $ 100
        text = re.sub(r'(\d)\s+(%)', r'\1\2', text)         # 50% not 50 %
        text = re.sub(r'(\d)\s+(x)', r'\1\2', text)         # 2x not 2 x
        
        # PASS 4: Fix punctuation spacing
        text = re.sub(r'([.,!?:;])([A-Za-z0-9])', r'\1 \2', text)
        text = re.sub(r',([^\s])', r', \1', text)
        
        # PASS 5: Fix parentheses and brackets
        text = re.sub(r'([A-Za-z0-9])\(', r'\1 (', text)
        text = re.sub(r'\)([A-Za-z0-9])', r') \1', text)
        text = re.sub(r'([A-Za-z0-9])\[', r'\1 [', text)
        text = re.sub(r'\]([A-Za-z0-9])', r'] \1', text)
        
        # PASS 6: Fix special cases
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # camelCase
        
        # PASS 7: Clean up spacing
        text = re.sub(r' {2,}', ' ', text)      # Multiple spaces
        text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple newlines
        
        # FINAL NUCLEAR PASS: One more time for numbers
        for _ in range(2):
            text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
            text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)
            text = re.sub(r' {2,}', ' ', text)
        
        # Clean up whitespace per line
        text = '\n'.join(line.strip() for line in text.split('\n'))
        
        return text.strip()

    @staticmethod
    def _extract_json_array(text: str) -> List[Dict[str, Any]]:
        """Extract the first JSON array from an LLM response."""
        if not text:
            raise ValueError("Empty response")

        cleaned = text.strip()
        if "```" in cleaned:
            parts = cleaned.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("[") and part.endswith("]"):
                    cleaned = part
                    break

        if not cleaned.startswith("["):
            start = cleaned.find("[")
            end = cleaned.rfind("]")
            if start != -1 and end != -1 and end > start:
                cleaned = cleaned[start:end + 1]

        return json.loads(cleaned)

    @staticmethod
    def _deduplicate(entries: List[Dict[str, Any]], key_fields: List[str]) -> List[Dict[str, Any]]:
        """Remove duplicate dict entries using provided key fields."""
        deduped: List[Dict[str, Any]] = []
        seen: set[Tuple[Any, ...]] = set()

        for entry in entries:
            key_parts: List[Any] = []
            for field in key_fields:
                value = entry.get(field)
                # Convert unhashable types to hashable equivalents
                if isinstance(value, list):
                    key_parts.append(tuple(value))
                elif isinstance(value, (pd.Series, pd.DataFrame)):
                    # Convert pandas objects to string representation
                    key_parts.append(str(value))
                elif isinstance(value, dict):
                    # Convert dict to sorted tuple of items
                    key_parts.append(tuple(sorted(value.items())))
                else:
                    key_parts.append(value)
            key = tuple(key_parts)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(entry)

        return deduped
    
    def analyze_all(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run complete automated analysis on campaign data.
        
        Args:
            df: DataFrame with campaign data
            
        Returns:
            Dictionary with all insights and recommendations
        """
        logger.info(f"Starting automated analysis on {len(df)} rows")
        
        # Process data with advanced processor
        df = self.processor.load_data(df, auto_detect=True)
        
        # Get data summary
        data_summary = self.processor.get_data_summary()
        logger.info(f"Data summary: {data_summary['time_granularity']} granularity, {len(data_summary['dimensions_found'])} dimensions")
        
        # Calculate overall KPIs
        overall_kpis = self.processor.calculate_overall_kpis()
        
        # Calculate metrics
        metrics = self._calculate_metrics(df)
        metrics['overall_kpis'] = overall_kpis
        metrics['data_summary'] = data_summary
        
        # Funnel analysis
        funnel_analysis = self._analyze_funnel(df, metrics)
        
        # ROAS & Revenue analysis (with error handling)
        try:
            roas_analysis = self._analyze_roas_revenue(df, metrics)
        except Exception as e:
            logger.warning(f"Could not generate ROAS analysis: {e}")
            roas_analysis = {"overall": {}, "by_platform": {}, "efficiency_tiers": {}}
        
        # Audience analysis (if data available)
        audience_analysis = self._analyze_audience(df, metrics)
        
        # Tactics analysis
        tactics_analysis = self._analyze_tactics(df, metrics)
        
        # Generate insights
        insights = self._generate_insights(df, metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(df, metrics, insights)
        
        # Identify opportunities
        opportunities = self._identify_opportunities(df, metrics)
        
        # Risk assessment
        risks = self._assess_risks(df, metrics)
        
        # Budget optimization (with error handling)
        try:
            budget_insights = self._optimize_budget(df, metrics)
        except Exception as e:
            logger.warning(f"Could not generate budget optimization: {e}")
            budget_insights = {"current_allocation": {}, "recommended_allocation": {}, "expected_improvement": {}}
        
        return {
            "metrics": metrics,
            "funnel_analysis": funnel_analysis,
            "roas_analysis": roas_analysis,
            "audience_analysis": audience_analysis,
            "tactics_analysis": tactics_analysis,
            "insights": insights,
            "recommendations": recommendations,
            "opportunities": opportunities,
            "risks": risks,
            "budget_optimization": budget_insights,
            "executive_summary": self._generate_executive_summary(metrics, insights, recommendations)
        }
    
    def _calculate_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive metrics from the data."""
        metrics = {
            "overview": {},
            "by_campaign": {},
            "by_platform": {},
            "performance_tiers": {},
            "trends": {}
        }
        
        # Overall metrics
        # Get column names using helper
        spend_col = self._get_column(df, 'spend')
        conv_col = self._get_column(df, 'conversions')
        impr_col = self._get_column(df, 'impressions')
        clicks_col = self._get_column(df, 'clicks')
        campaign_col = self._get_column(df, 'campaign')
        
        metrics["overview"] = {
            "total_campaigns": df[campaign_col].nunique() if campaign_col else len(df),
            "total_platforms": df['Platform'].nunique() if 'Platform' in df.columns else 0,
            "total_spend": float(df[spend_col].sum()) if spend_col else 0,
            "total_conversions": float(df[conv_col].sum()) if conv_col else 0,
            "total_impressions": float(df[impr_col].sum()) if impr_col else 0,
            "total_clicks": float(df[clicks_col].sum()) if clicks_col else 0,
            "avg_roas": float(df['ROAS'].mean()) if 'ROAS' in df.columns else 0,
            "avg_cpa": float(df['CPA'].mean()) if 'CPA' in df.columns else 0,
            "avg_ctr": float(df['CTR'].mean()) if 'CTR' in df.columns else 0,
            "avg_cpc": float(df['CPC'].mean()) if 'CPC' in df.columns else 0,
            "avg_conversion_rate": float(df['Conversion_Rate'].mean()) if 'Conversion_Rate' in df.columns else 0,
        }
        
        # Campaign-level metrics
        if 'Campaign_Name' in df.columns:
            campaign_metrics = df.groupby('Campaign_Name').agg({
                'Spend': 'sum',
                'Conversions': 'sum',
                'ROAS': 'mean',
                'CPA': 'mean',
                'Impressions': 'sum',
                'Clicks': 'sum'
            }).round(2)
            
            metrics["by_campaign"] = campaign_metrics.to_dict('index')
        
        # Platform-level metrics
        if 'Platform' in df.columns:
            try:
                # Handle potential duplicate columns by selecting first occurrence
                platform_col = df['Platform']
                if isinstance(platform_col, pd.DataFrame):
                    platform_col = platform_col.iloc[:, 0]
                
                # Create temp df with unique column
                temp_df = df.copy()
                temp_df['_Platform'] = platform_col
                
                # Build aggregation dict based on available columns using helper
                agg_dict = {}
                
                # Get column names using mapping
                spend_col = self._get_column(temp_df, 'spend')
                if spend_col:
                    agg_dict[spend_col] = 'sum'
                
                conv_col = self._get_column(temp_df, 'conversions')
                if conv_col:
                    agg_dict[conv_col] = 'sum'
                
                impr_col = self._get_column(temp_df, 'impressions')
                if impr_col:
                    agg_dict[impr_col] = 'sum'
                
                clicks_col = self._get_column(temp_df, 'clicks')
                if clicks_col:
                    agg_dict[clicks_col] = 'sum'
                
                # These are usually calculated metrics
                for col_name in ['ROAS', 'CPA', 'CTR']:
                    if col_name in temp_df.columns:
                        agg_dict[col_name] = 'mean'
                
                if agg_dict:
                    platform_metrics = temp_df.groupby('_Platform').agg(agg_dict).round(2)
                    metrics["by_platform"] = platform_metrics.to_dict('index')
                else:
                    metrics["by_platform"] = {}
            except Exception as e:
                logger.warning(f"Could not calculate platform metrics: {e}")
                metrics["by_platform"] = {}
        
        # Performance tiers
        if 'ROAS' in df.columns:
            metrics["performance_tiers"] = {
                "excellent": len(df[df['ROAS'] >= 4.5]),
                "good": len(df[(df['ROAS'] >= 3.5) & (df['ROAS'] < 4.5)]),
                "average": len(df[(df['ROAS'] >= 2.5) & (df['ROAS'] < 3.5)]),
                "poor": len(df[df['ROAS'] < 2.5])
            }
        
        # Time trends (if date column exists)
        if 'Date' in df.columns:
            try:
                df['Date'] = pd.to_datetime(df['Date'])
                
                # Build aggregation dict based on available columns using helper
                agg_dict = {}
                
                spend_col = self._get_column(df, 'spend')
                if spend_col:
                    agg_dict[spend_col] = 'sum'
                
                conv_col = self._get_column(df, 'conversions')
                if conv_col:
                    agg_dict[conv_col] = 'sum'
                
                if 'ROAS' in df.columns:
                    agg_dict['ROAS'] = 'mean'
                
                if agg_dict:
                    monthly = df.groupby(df['Date'].dt.to_period('M')).agg(agg_dict).round(2)
                    metrics["monthly_trends"] = monthly.to_dict('index')
                else:
                    metrics["monthly_trends"] = {}
            except Exception as e:
                logger.warning(f"Could not calculate monthly trends: {e}")
                metrics["monthly_trends"] = {}
        
        return metrics
    
    def _call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
        """
        Call LLM (OpenAI or Anthropic) with unified interface.
        
        Args:
            system_prompt: System message
            user_prompt: User message
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLM response text
        """
        try:
            if self.use_anthropic:
                # Anthropic Claude API via HTTP (bypass SDK proxy issues)
                import requests
                headers = {
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
                payload = {
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "temperature": 0.3,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": user_prompt}
                    ]
                }
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                return response.json()["content"][0]["text"]
            else:
                # OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def _generate_insights(self, df: pd.DataFrame, metrics: Dict) -> List[Dict[str, str]]:
        """Generate AI-powered insights from the data."""
        insights = []
        
        # Prepare data summary for AI
        data_summary = self._prepare_data_summary(df, metrics)
        
        prompt = f"""You are a senior media analytics expert with 15+ years of experience in digital advertising across Google Ads, Meta, LinkedIn, DV360, CM360, and Snapchat.

You have DEEP EXPERTISE in:
- **Funnel Analysis**: Awareness → Consideration → Conversion optimization
- **ROAS & Revenue**: Return on ad spend, revenue attribution, LTV analysis
- **Audience Strategy**: Demographics, segments, targeting, lookalikes
- **Tactics**: Creative performance, bidding strategies, placement optimization, A/B testing
- **Attribution**: Multi-touch attribution, assisted conversions, path analysis
- **Media Mix**: Cross-channel synergies, budget allocation, incrementality

Analyze this campaign data and provide 8-10 KEY INSIGHTS that a CMO would find valuable:

{data_summary}

For each insight:
1. Be specific with numbers and percentages
2. Explain WHY it matters from a funnel/ROAS/audience/tactics perspective
3. Compare to industry benchmarks where relevant (e.g., ROAS benchmarks by platform)
4. Highlight patterns or anomalies in funnel performance, audience behavior, or tactical execution
5. Consider full-funnel impact (not just last-click conversions)

Industry Benchmarks to Consider:
- Google Ads ROAS: 2.0-4.0x (Search), 1.5-3.0x (Display)
- Meta Ads ROAS: 2.5-4.5x (average)
- LinkedIn Ads ROAS: 2.0-3.5x (B2B)
- CTR: 1.5-3.0% (good), 3.0%+ (excellent)
- CPA: Varies by industry, but look for consistency and trends

STRICT OUTPUT RULES:
- Return VALID JSON array only (no prose before or after the array, no Markdown fences, no italics).
- Each insight must reference concrete metrics from the data summary.

Format exactly as JSON array:
[
  {{
    "category": "Funnel|ROAS|Audience|Tactics|Attribution|Platform",
    "insight": "Specific insight with numbers and funnel/audience/tactics context",
    "impact": "High|Medium|Low",
    "explanation": "Why this matters for business outcomes, considering full-funnel and audience dynamics"
  }}
]

Focus on actionable insights that drive business decisions across the entire customer journey."""

        try:
            system_prompt = "You are a world-class media analytics expert. Provide data-driven insights with specific numbers. Return JSON only."
            insights_text = self._call_llm(system_prompt, prompt, max_tokens=2000).strip()
            insights = self._extract_json_array(insights_text)
            logger.info(f"Generated {len(insights)} insights")
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            # Fallback to rule-based insights
            insights = self._generate_rule_based_insights(df, metrics)
        
        return insights
    
    def _generate_recommendations(self, df: pd.DataFrame, metrics: Dict, insights: List) -> List[Dict[str, str]]:
        """Generate actionable recommendations."""
        
        data_summary = self._prepare_data_summary(df, metrics)
        insights_summary = json.dumps(insights, indent=2)
        
        prompt = f"""You are a strategic media planning expert with deep expertise in funnel optimization, ROAS improvement, audience targeting, and tactical execution.

Based on this campaign data and insights, provide 6-8 ACTIONABLE RECOMMENDATIONS:

Campaign Data:
{data_summary}

Key Insights:
{insights_summary}

For each recommendation:
1. Be SPECIFIC and ACTIONABLE (not generic advice)
2. Include expected impact with numbers
3. Prioritize by potential ROI
4. Consider budget constraints
5. Include implementation timeline
6. Address one or more of these areas:
   - **Funnel Optimization**: Move users through awareness → consideration → conversion
   - **ROAS Improvement**: Increase return on ad spend through better targeting/bidding
   - **Audience Strategy**: Refine targeting, create lookalikes, segment optimization
   - **Tactical Execution**: Creative refresh, bidding strategy, placement optimization
   - **Attribution**: Better measurement and credit assignment
   - **Budget Allocation**: Shift spend to higher-performing channels/audiences

Tactical Recommendations Should Include:
- Specific bidding strategies (Target ROAS, Maximize Conversions, Manual CPC)
- Audience tactics (Lookalikes, Custom Audiences, In-Market, Affinity)
- Creative recommendations (Video vs Static, Messaging, CTAs)
- Placement strategies (Feed, Stories, Search, Display Network)
- Funnel stage focus (Top-of-funnel awareness vs bottom-of-funnel conversion)

Format as JSON array:
[
  {{
    "priority": "Critical|High|Medium",
    "recommendation": "Specific action to take (include funnel stage, audience, or tactic)",
    "expected_impact": "Quantified expected outcome (ROAS, conversions, funnel movement)",
    "implementation": "How to execute (2-3 specific steps with platform/tactic details)",
    "timeline": "Immediate|1-2 weeks|1 month",
    "estimated_roi": "Expected return percentage",
    "focus_area": "Funnel|ROAS|Audience|Tactics|Attribution|Budget"
  }}
]

Focus on recommendations that can be implemented immediately with clear tactical steps."""

        try:
            system_prompt = "You are a strategic media planning expert. Provide specific, actionable recommendations with expected ROI."
            recs_text = self._call_llm(system_prompt, prompt, max_tokens=2000).strip()
            if "```json" in recs_text:
                recs_text = recs_text.split("```json")[1].split("```")[0].strip()
            elif "```" in recs_text:
                recs_text = recs_text.split("```")[1].split("```")[0].strip()
            
            recommendations = json.loads(recs_text)
            logger.info(f"Generated {len(recommendations)} recommendations")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations = self._generate_rule_based_recommendations(df, metrics)
        
        return recommendations
    
    def _identify_opportunities(self, df: pd.DataFrame, metrics: Dict) -> List[Dict[str, Any]]:
        """Identify growth opportunities across multiple KPIs."""
        opportunities = []
        
        # Get column names
        spend_col = self._get_column(df, 'spend')
        conv_col = self._get_column(df, 'conversions')
        clicks_col = self._get_column(df, 'clicks')
        impr_col = self._get_column(df, 'impressions')
        
        # 1. High ROAS campaigns that could scale (limit to top 3)
        if 'ROAS' in df.columns and spend_col:
            try:
                high_performers = df[df['ROAS'] > 4.0].sort_values('ROAS', ascending=False)
                top_campaigns = []
                for _, row in high_performers.head(3).iterrows():
                    campaign_name = row.get('Campaign_Name', 'Unknown')
                    top_campaigns.append(campaign_name)
                
                if top_campaigns:
                    total_current_spend = high_performers.head(3)[spend_col].sum()
                    avg_roas = high_performers.head(3)['ROAS'].mean()
                    potential_revenue = total_current_spend * 0.75 * avg_roas  # 75% budget increase
                    
                    campaigns_text = ", ".join(top_campaigns[:3])
                    if len(top_campaigns) > 3:
                        campaigns_text += f" and {len(top_campaigns) - 3} more"
                    
                    opportunities.append({
                        "type": "Scale Winners",
                        "campaigns": top_campaigns[:3],
                        "details": f"High-performing campaigns with average ROAS of {avg_roas:.2f}x",
                        "why_it_matters": f"These campaigns ({campaigns_text}) are delivering exceptional returns",
                        "recommended_action": f"Increase budget by 50-100% across these {len(top_campaigns[:3])} campaigns",
                        "expected_impact": f"Could generate ${potential_revenue:,.0f} in additional revenue",
                        "current_metrics": f"Current spend: ${total_current_spend:,.0f}, Avg ROAS: {avg_roas:.2f}x"
                    })
            except Exception as e:
                logger.warning(f"Could not identify ROAS scale winners: {e}")
        
        # 2. High CTR campaigns (engagement opportunity)
        if 'CTR' in df.columns and spend_col:
            try:
                high_ctr = df[df['CTR'] > 3.0].sort_values('CTR', ascending=False)
                for _, row in high_ctr.head(2).iterrows():
                    opportunities.append({
                        "type": "High Engagement (CTR)",
                        "campaign": row.get('Campaign_Name', 'Unknown'),
                        "platform": row.get('Platform', 'Unknown'),
                        "current_ctr": float(row['CTR']),
                        "opportunity": f"CTR of {float(row['CTR']):.2f}% shows strong audience engagement - optimize for conversions",
                        "potential_impact": "Improve conversion rate to maximize this engaged traffic"
                    })
            except Exception as e:
                logger.warning(f"Could not identify CTR opportunities: {e}")
        
        # 3. Low CPC with good conversion rate (efficiency opportunity)
        if 'CPC' in df.columns and 'Conversion_Rate' in df.columns and spend_col:
            try:
                efficient = df[(df['CPC'] < df['CPC'].median()) & (df['Conversion_Rate'] > df['Conversion_Rate'].median())]
                for _, row in efficient.head(2).iterrows():
                    opportunities.append({
                        "type": "Efficient Performer (CPC + Conv Rate)",
                        "campaign": row.get('Campaign_Name', 'Unknown'),
                        "platform": row.get('Platform', 'Unknown'),
                        "current_cpc": float(row['CPC']),
                        "current_conv_rate": float(row['Conversion_Rate']),
                        "opportunity": f"Low CPC (${float(row['CPC']):.2f}) + High Conv Rate ({float(row['Conversion_Rate']):.2f}%) = Scale opportunity",
                        "potential_impact": "Efficient acquisition cost with strong conversion - ideal for scaling"
                    })
            except Exception as e:
                logger.warning(f"Could not identify CPC/Conv Rate opportunities: {e}")
        
        # 4. High impression share but low CTR (creative opportunity)
        if impr_col and 'CTR' in df.columns:
            try:
                high_impr_low_ctr = df[(df[impr_col] > df[impr_col].quantile(0.75)) & (df['CTR'] < 1.5)]
                for _, row in high_impr_low_ctr.head(2).iterrows():
                    opportunities.append({
                        "type": "Creative Optimization (Impressions vs CTR)",
                        "campaign": row.get('Campaign_Name', 'Unknown'),
                        "platform": row.get('Platform', 'Unknown'),
                        "impressions": int(row[impr_col]),
                        "current_ctr": float(row['CTR']),
                        "opportunity": f"High impressions ({int(row[impr_col]):,}) but low CTR ({float(row['CTR']):.2f}%) - refresh creative",
                        "potential_impact": "Improving CTR to 2.5% could double clicks without additional spend"
                    })
            except Exception as e:
                logger.warning(f"Could not identify creative opportunities: {e}")
        
        # 5. Good CTR but low conversion rate (landing page opportunity)
        if 'CTR' in df.columns and 'Conversion_Rate' in df.columns:
            try:
                good_ctr_low_conv = df[(df['CTR'] > 2.0) & (df['Conversion_Rate'] < df['Conversion_Rate'].median())]
                for _, row in good_ctr_low_conv.head(2).iterrows():
                    opportunities.append({
                        "type": "Landing Page Optimization (CTR vs Conv Rate)",
                        "campaign": row.get('Campaign_Name', 'Unknown'),
                        "platform": row.get('Platform', 'Unknown'),
                        "current_ctr": float(row['CTR']),
                        "current_conv_rate": float(row['Conversion_Rate']),
                        "opportunity": f"Good CTR ({float(row['CTR']):.2f}%) but low Conv Rate ({float(row['Conversion_Rate']):.2f}%) - optimize landing page",
                        "potential_impact": "Improving conversion rate could 2x conversions with same traffic"
                    })
            except Exception as e:
                logger.warning(f"Could not identify landing page opportunities: {e}")
        
        # 6. Underutilized platforms with strong KPIs
        if 'Platform' in df.columns and spend_col:
            try:
                platform_col = df['Platform']
                if isinstance(platform_col, pd.DataFrame):
                    platform_col = platform_col.iloc[:, 0]
                
                temp_df = df.copy()
                temp_df['_Platform'] = platform_col
                platform_spend = temp_df.groupby('_Platform')[spend_col].sum()
                total_spend = platform_spend.sum()
                
                for platform, spend in platform_spend.items():
                    if spend / total_spend < 0.10:  # Less than 10% of budget
                        platform_data = df[df['Platform'] == platform]
                        kpis = []
                        if 'ROAS' in df.columns:
                            avg_roas = platform_data['ROAS'].mean()
                            if avg_roas > 3.5:
                                kpis.append(f"ROAS {avg_roas:.2f}x")
                        if 'CTR' in df.columns:
                            avg_ctr = platform_data['CTR'].mean()
                            if avg_ctr > 2.0:
                                kpis.append(f"CTR {avg_ctr:.2f}%")
                        if 'Conversion_Rate' in df.columns:
                            avg_conv = platform_data['Conversion_Rate'].mean()
                            if avg_conv > platform_data['Conversion_Rate'].median():
                                kpis.append(f"Conv Rate {avg_conv:.2f}%")
                        
                        if kpis:
                            opportunities.append({
                                "type": "Underutilized Platform",
                                "platform": platform,
                                "current_spend": float(spend),
                                "kpi_highlights": ", ".join(kpis),
                                "recommendation": "Shift incremental budget to this platform while monitoring ROAS"
                            })
            except Exception as e:
                logger.warning(f"Could not identify underutilized platforms: {e}")
        
        opportunities = self._deduplicate(opportunities, ["type", "campaign", "campaigns", "platform", "details"])
        
        # 7. Seasonal/temporal opportunities
        if 'Date' in df.columns:
            try:
                df_copy = df.copy()
                df_copy['Month'] = pd.to_datetime(df_copy['Date']).dt.month
                
                # Analyze multiple KPIs by month
                agg_dict = {}
                if 'ROAS' in df.columns:
                    agg_dict['ROAS'] = 'mean'
                if 'CTR' in df.columns:
                    agg_dict['CTR'] = 'mean'
                if conv_col:
                    agg_dict[conv_col] = 'sum'
                
                if agg_dict:
                    monthly_performance = df_copy.groupby('Month').agg(agg_dict)
                    
                    # Find best month by primary metric
                    if 'ROAS' in agg_dict:
                        best_month = monthly_performance['ROAS'].idxmax()
                        best_roas = monthly_performance.loc[best_month, 'ROAS']
                        opportunities.append({
                            "type": "Seasonal Opportunity",
                            "period": f"Month {best_month}",
                            "avg_roas": float(best_roas),
                            "opportunity": f"Historical peak performance in Month {best_month} (ROAS {best_roas:.2f}x)",
                            "potential_impact": "Plan increased investment 2-3 weeks before this period"
                        })
            except Exception as e:
                logger.warning(f"Could not calculate seasonal opportunities: {e}")
        
        # Limit to top 5 opportunities
        return opportunities[:5]
    
    def _assess_risks(self, df: pd.DataFrame, metrics: Dict) -> List[Dict[str, Any]]:
        """Assess risks and red flags across multiple KPIs."""
        risks = []
        
        spend_col = self._get_column(df, 'spend')
        
        # 1. Low ROAS campaigns with campaign names
        if 'ROAS' in df.columns and spend_col:
            poor_performers = df[df['ROAS'] < 2.5].sort_values('ROAS')
            if len(poor_performers) > 0:
                total_waste = poor_performers[spend_col].sum()
                worst_campaigns = []
                for _, row in poor_performers.head(3).iterrows():
                    campaign_name = row.get('Campaign_Name', 'Unknown')
                    worst_campaigns.append(f"{campaign_name} (ROAS: {row['ROAS']:.2f}x)")
                
                campaigns_text = ", ".join(worst_campaigns)
                risks.append({
                    "severity": "High",
                    "risk": "Low ROAS Campaigns",
                    "details": f"{len(poor_performers)} campaigns with ROAS below 2.5x",
                    "impact": f"${total_waste:,.0f} at risk",
                    "worst_performers": campaigns_text,
                    "action": f"Review and optimize or pause these campaigns immediately. Focus on: {campaigns_text}"
                })
        
        # 2. High CPA campaigns
        if 'CPA' in df.columns and spend_col:
            high_cpa = df[df['CPA'] > df['CPA'].quantile(0.75)]
            if len(high_cpa) > 0:
                avg_high_cpa = high_cpa['CPA'].mean()
                risks.append({
                    "severity": "Medium",
                    "risk": "High Cost Per Acquisition",
                    "details": f"{len(high_cpa)} campaigns with CPA in top 25% (avg ${avg_high_cpa:.2f})",
                    "impact": "Reducing efficiency and profitability",
                    "action": "Optimize targeting, creative, or bidding strategy"
                })
        
        # 3. Low CTR (poor ad relevance/creative)
        if 'CTR' in df.columns:
            low_ctr = df[df['CTR'] < 1.0]
            if len(low_ctr) > 0:
                risks.append({
                    "severity": "Medium",
                    "risk": "Low Click-Through Rate",
                    "details": f"{len(low_ctr)} campaigns with CTR below 1.0%",
                    "impact": "Poor ad relevance or creative fatigue - wasting impressions",
                    "action": "Refresh ad creative, improve targeting, or test new messaging"
                })
        
        # 4. High CPC (overpaying for clicks)
        if 'CPC' in df.columns and spend_col:
            high_cpc = df[df['CPC'] > df['CPC'].quantile(0.90)]
            if len(high_cpc) > 0:
                avg_high_cpc = high_cpc['CPC'].mean()
                total_high_cpc_spend = high_cpc[spend_col].sum()
                risks.append({
                    "severity": "Medium",
                    "risk": "High Cost Per Click",
                    "details": f"{len(high_cpc)} campaigns with CPC in top 10% (avg ${avg_high_cpc:.2f})",
                    "impact": f"${total_high_cpc_spend:,.0f} spend at elevated CPC",
                    "action": "Review bidding strategy, improve quality score, or adjust targeting"
                })
        
        # 5. Low conversion rate (funnel drop-off)
        if 'Conversion_Rate' in df.columns:
            low_conv = df[df['Conversion_Rate'] < df['Conversion_Rate'].quantile(0.25)]
            if len(low_conv) > 0:
                risks.append({
                    "severity": "High",
                    "risk": "Low Conversion Rate",
                    "details": f"{len(low_conv)} campaigns with Conv Rate in bottom 25%",
                    "impact": "Traffic not converting - landing page or offer issues",
                    "action": "Optimize landing pages, improve offer, or refine audience targeting"
                })
        
        # Platform concentration risk
        spend_col = self._get_column(df, 'spend')
        if 'Platform' in df.columns and spend_col:
            try:
                platform_col = df['Platform']
                if isinstance(platform_col, pd.DataFrame):
                    platform_col = platform_col.iloc[:, 0]
                
                temp_df = df.copy()
                temp_df['_Platform'] = platform_col
                platform_spend = temp_df.groupby('_Platform')[spend_col].sum()
                max_concentration = (platform_spend.max() / platform_spend.sum()) * 100
            except Exception as e:
                logger.warning(f"Could not calculate platform concentration: {e}")
                max_concentration = 0
            
            if max_concentration > 50:
                risks.append({
                    "severity": "Medium",
                    "risk": "Platform Concentration",
                    "details": f"{max_concentration:.1f}% of budget on single platform",
                    "impact": "High dependency risk if platform performance declines",
                    "action": "Diversify across multiple platforms to reduce risk"
                })
        
        # Declining performance trend
        if 'Date' in df.columns and 'ROAS' in df.columns:
            df_sorted = df.sort_values('Date')
            recent_roas = df_sorted.tail(5)['ROAS'].mean()
            earlier_roas = df_sorted.head(5)['ROAS'].mean()
            
            if recent_roas < earlier_roas * 0.9:  # 10% decline
                risks.append({
                    "severity": "High",
                    "risk": "Declining Performance Trend",
                    "details": f"ROAS declined from {earlier_roas:.2f} to {recent_roas:.2f}",
                    "impact": "Continued decline could significantly impact ROI",
                    "action": "Investigate root cause and implement corrective measures"
                })
        
        risks = self._deduplicate(risks, ["risk", "details"])

        # Limit to top 5 risks
        return risks[:5]
    
    def _optimize_budget(self, df: pd.DataFrame, metrics: Dict) -> Dict[str, Any]:
        """Suggest budget optimization."""
        # This method has hardcoded column references - skip if columns don't exist
        logger.warning("Budget optimization skipped - requires 'Spend' and 'Conversions' columns")
        return {
            "current_allocation": {},
            "recommended_allocation": {},
            "expected_improvement": {}
        }
    
    def _generate_executive_summary(self, metrics: Dict, insights: List, recommendations: List) -> Dict[str, str]:
        """Generate both brief and detailed executive summaries.
        
        Returns:
            Dict with 'brief' and 'detailed' keys containing respective summaries
        """
        
        # Convert to JSON-serializable format
        def make_serializable(obj):
            """Convert pandas objects to JSON-serializable types."""
            if isinstance(obj, pd.Series):
                return obj.to_dict()
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict('records')
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            return obj
        
        overview = make_serializable(metrics.get('overview', {}))
        
        platform_metrics = metrics.get('by_platform', {})
        campaign_metrics = metrics.get('by_campaign', {})

        def _get_best_metric(metric_key: str, source: Dict[str, Dict[str, Any]], prefer_max: bool = True):
            best_name = None
            best_stats = None
            comparator = max if prefer_max else min
            filtered = {
                name: data for name, data in source.items()
                if isinstance(data, dict) and metric_key in data and data[metric_key] is not None
            }
            if not filtered:
                return None
            best_name = comparator(filtered, key=lambda k: filtered[k][metric_key])
            best_stats = filtered[best_name]
            return {
                "name": best_name,
                metric_key: float(best_stats[metric_key]),
                "spend": float(best_stats.get('Spend') or best_stats.get('Cost') or 0),
                "conversions": float(best_stats.get('Conversions') or best_stats.get('Site Visit') or best_stats.get('Site_Visit') or 0)
            }

        top_platform_roas = _get_best_metric('ROAS', platform_metrics, prefer_max=True)
        bottom_platform_roas = _get_best_metric('ROAS', platform_metrics, prefer_max=False)
        top_campaign_roas = _get_best_metric('ROAS', campaign_metrics, prefer_max=True)
        top_campaign_ctr = _get_best_metric('CTR', campaign_metrics, prefer_max=True)

        # Build comprehensive KPI summary
        summary_data = {
            "total_spend": overview.get('total_spend', 0),
            "total_conversions": overview.get('total_conversions', 0),
            "total_impressions": overview.get('total_impressions', 0),
            "total_clicks": overview.get('total_clicks', 0),
            "campaigns": overview.get('total_campaigns', 0),
            "platforms": overview.get('total_platforms', 0),
            "kpis": {
                "avg_roas": overview.get('avg_roas', 0),
                "avg_cpa": overview.get('avg_cpa', 0),
                "avg_ctr": overview.get('avg_ctr', 0),
                "avg_cpc": overview.get('avg_cpc', 0) if 'avg_cpc' in overview else None,
                "avg_conversion_rate": overview.get('avg_conversion_rate', 0) if 'avg_conversion_rate' in overview else None
            },
            "top_insights": insights[:3] if insights else [],
            "top_recommendations": recommendations[:3] if recommendations else [],
            "leaders": {
                "platform_roas": top_platform_roas,
                "campaign_roas": top_campaign_roas,
                "campaign_ctr": top_campaign_ctr
            },
            "laggards": {
                "platform_roas": bottom_platform_roas
            }
        }
        
        brief_prompt = f"""Create a BRIEF executive summary (3-4 bullet points) for a CMO based on this campaign analysis:

Data:
{json.dumps(summary_data, indent=2)}

INSTRUCTIONS:
- Write EXACTLY 3-4 bullet points
- Each bullet MUST be ONE crisp, impactful sentence (max 25 words)
- Include specific numbers (spend, ROAS, CTR, conversions)
- Focus on: overall performance, key win/challenge, top priority action
- Use bullet points (•) format
- Be concise and data-driven

Example:
• Portfolio delivered $X revenue from $Y spend across Z platforms with A.Bx ROAS
• [Platform] outperformed by C% with D% lower CPA
• [Issue] causing $X revenue loss - immediate action required
• Reallocate $X to [Channel] for Y% ROAS improvement"""

        detailed_prompt = f"""Create a DETAILED executive summary with sub-headers for a CMO based on this campaign analysis:

Data:
{json.dumps(summary_data, indent=2)}

STRUCTURE (MANDATORY):
Write 5-6 sections, each with a sub-header (###) followed by 2-3 crisp sentences:

### 📊 Performance Overview
[2-3 sentences: Total spend, conversions, platforms, overall ROAS with specific numbers]

### 📈 Multi-KPI Analysis
[2-3 sentences: CTR, CPC, CPA, Conversion Rate performance with benchmarks and trends]

### ✅ What's Working
[2-3 sentences: Top performers, successful strategies, positive trends with specific metrics]

### ⚠️ What's Not Working
[2-3 sentences: Underperformers, challenges, areas of concern with impact quantification]

### 🎯 Priority Actions
[2-3 sentences: Top 3 specific recommendations with expected impact and timeline]

### 💰 Budget Optimization
[2-3 sentences: Reallocation suggestions with expected ROI improvement]

FORMATTING RULES (CRITICAL - MUST FOLLOW EXACTLY):
- Start each section with ### [Emoji] [Title]
- Each sentence must be crisp (max 30 words)
- Include specific numbers and percentages

CRITICAL SPACING RULES - READ CAREFULLY:

Rule 1: ALWAYS put a space after ANY number before ANY letter
✓ CORRECT: "15 campaigns", "973K revenue", "0.60 CPC", "79,492 budget"
✗ WRONG: "15campaigns", "973Krevenue", "0.60CPC", "79,492budget"

Rule 2: ALWAYS put a space before ANY number after ANY letter
✓ CORRECT: "from 364K", "approximately 1 million", "generated 8,560 conversions"
✗ WRONG: "from364K", "approximately1million", "generated8,560conversions"

Rule 3: ALWAYS put a space after punctuation
✓ CORRECT: "ROAS. The campaign", "competitive, though the"
✗ WRONG: "ROAS.The campaign", "competitive,though the"

Rule 4: ALWAYS put a space before opening parentheses
✓ CORRECT: "budget (approximately", "campaigns (15 total)"
✗ WRONG: "budget(approximately", "campaigns(15 total)"

Rule 5: NO formatting characters - write in PLAIN TEXT ONLY
✓ CORRECT: "The 0.60 CPC is competitive"
✗ WRONG: "The **0.60 CPC** is competitive" or "The 0.60CPC**is**competitive"

FORMATTING REQUIREMENTS:
- NO asterisks (*)
- NO underscores (_)
- NO bold or italics
- NO bullet points in detailed summary
- Write complete sentences in plain text
- Each section starts with ### [Emoji] [Title]

BEFORE SUBMITTING YOUR RESPONSE:
1. Check EVERY number has a space after it
2. Check EVERY number has a space before it
3. Remove ALL asterisks and underscores
4. Verify punctuation has spaces after it"""

        # Try LLMs in order: Claude Sonnet → Gemini 2.5 Pro → GPT-4o-mini
        brief_summary = None
        detailed_summary = None
        system_prompt = "You are a strategic marketing consultant writing for C-level executives. Focus on multi-KPI analysis, not just ROAS. Write clear, professional, well-structured content."
        
        # 1. Try Claude Sonnet (primary)
        if self.use_anthropic and self.anthropic_api_key:
            try:
                logger.info("Attempting brief executive summary with Claude Sonnet")
                brief_summary = self._call_llm(system_prompt, brief_prompt, max_tokens=800)
                logger.info(f"✅ Brief summary generated with Claude Sonnet ({len(brief_summary)} chars)")
                
                logger.info("Attempting detailed executive summary with Claude Sonnet")
                detailed_summary = self._call_llm(system_prompt, detailed_prompt, max_tokens=2000)
                logger.info(f"✅ Detailed summary generated with Claude Sonnet ({len(detailed_summary)} chars)")
            except Exception as e:
                logger.warning(f"❌ Claude Sonnet failed: {e}")
        
        # 2. Try Gemini 2.5 Pro (fallback 1)
        if (not brief_summary or not detailed_summary) and self.gemini_client:
            try:
                if not brief_summary:
                    logger.info("Attempting brief executive summary with Gemini 2.5 Pro")
                    full_prompt = f"{system_prompt}\n\n{brief_prompt}"
                    response = self.gemini_client.generate_content(full_prompt)
                    brief_summary = response.text
                    logger.info(f"✅ Brief summary generated with Gemini 2.5 Pro ({len(brief_summary)} chars)")
                
                if not detailed_summary:
                    logger.info("Attempting detailed executive summary with Gemini 2.5 Pro")
                    full_prompt = f"{system_prompt}\n\n{detailed_prompt}"
                    response = self.gemini_client.generate_content(full_prompt)
                    detailed_summary = response.text
                    logger.info(f"✅ Detailed summary generated with Gemini 2.5 Pro ({len(detailed_summary)} chars)")
            except Exception as e:
                logger.warning(f"❌ Gemini 2.5 Pro failed: {e}")
        
        # 3. Try GPT-4o-mini (fallback 2)
        if (not brief_summary or not detailed_summary) and not self.use_anthropic and self.client:
            try:
                if not brief_summary:
                    logger.info("Attempting brief executive summary with GPT-4o-mini")
                    brief_summary = self._call_llm(system_prompt, brief_prompt, max_tokens=800)
                    logger.info(f"✅ Brief summary generated with GPT-4o-mini ({len(brief_summary)} chars)")
                
                if not detailed_summary:
                    logger.info("Attempting detailed executive summary with GPT-4o-mini")
                    detailed_summary = self._call_llm(system_prompt, detailed_prompt, max_tokens=2000)
                    logger.info(f"✅ Detailed summary generated with GPT-4o-mini ({len(detailed_summary)} chars)")
            except Exception as e:
                logger.warning(f"❌ GPT-4o-mini failed: {e}")
        
        if brief_summary:
            brief_summary = self._strip_italics(brief_summary.strip())
        if detailed_summary:
            detailed_summary = self._strip_italics(detailed_summary.strip())
        
        if not brief_summary or not detailed_summary:
            logger.error("⚠️ All LLM clients failed for executive summary - using fallback")
            # Enhanced fallback summary
            kpi_summary = []
            if overview.get('avg_roas', 0) > 0:
                kpi_summary.append(f"ROAS {overview['avg_roas']:.2f}x")
            if overview.get('avg_ctr', 0) > 0:
                kpi_summary.append(f"CTR {overview['avg_ctr']:.2f}%")
            if overview.get('avg_cpa', 0) > 0:
                kpi_summary.append(f"CPA ${overview['avg_cpa']:.2f}")
            
            kpi_text = ", ".join(kpi_summary) if kpi_summary else "multiple KPIs"
            fallback_text = f"Campaign portfolio analysis complete. {summary_data['campaigns']} campaigns analyzed across {summary_data['platforms']} platforms with total spend of ${summary_data['total_spend']:,.0f}. Key metrics: {kpi_text}. {summary_data['total_conversions']:,.0f} total conversions generated from {summary_data['total_clicks']:,.0f} clicks."
            
            if not brief_summary:
                brief_summary = f"• {fallback_text}"
            if not detailed_summary:
                detailed_summary = fallback_text
        
        return {
            "brief": brief_summary,
            "detailed": detailed_summary
        }
    
    
    def _prepare_data_summary(self, df: pd.DataFrame, metrics: Dict) -> str:
        """Prepare comprehensive data summary for AI prompts with multi-KPI focus."""
        overview = metrics['overview']
        
        summary = f"""
Campaign Data Summary:
- Total Campaigns: {overview.get('total_campaigns', 0)}
- Total Platforms: {overview.get('total_platforms', 0)}
- Total Spend: ${overview.get('total_spend', 0):,.0f}
- Total Impressions: {overview.get('total_impressions', 0):,.0f}
- Total Clicks: {overview.get('total_clicks', 0):,.0f}
- Total Conversions: {overview.get('total_conversions', 0):,.0f}

Key Performance Indicators:
- Average ROAS: {overview.get('avg_roas', 0):.2f}x
- Average CPA: ${overview.get('avg_cpa', 0):.2f}
- Average CTR: {overview.get('avg_ctr', 0):.2f}%
- Average CPC: ${overview.get('avg_cpc', 0):.2f} (if available)

Platform Performance (Multi-KPI View):
"""
        
        if metrics.get('by_platform'):
            for platform, data in metrics['by_platform'].items():
                summary += f"\n{platform}:"
                # Use flexible column mapping
                spend_key = next((k for k in ['Spend', 'Total Spent', 'Total_Spent', 'Cost'] if k in data), None)
                conv_key = next((k for k in ['Conversions', 'Site Visit', 'Site_Visit'] if k in data), None)
                clicks_key = next((k for k in ['Clicks', 'Click'] if k in data), None)
                impr_key = next((k for k in ['Impressions', 'Impr'] if k in data), None)
                
                if spend_key:
                    summary += f"\n  - Spend: ${data.get(spend_key, 0):,.0f}"
                if 'ROAS' in data:
                    summary += f"\n  - ROAS: {data.get('ROAS', 0):.2f}x"
                if 'CTR' in data:
                    summary += f"\n  - CTR: {data.get('CTR', 0):.2f}%"
                if 'CPA' in data:
                    summary += f"\n  - CPA: ${data.get('CPA', 0):.2f}"
                if conv_key:
                    summary += f"\n  - Conversions: {data.get(conv_key, 0):,.0f}"
                if clicks_key:
                    summary += f"\n  - Clicks: {data.get(clicks_key, 0):,.0f}"
        
        return summary
    
    def _generate_rule_based_insights(self, df: pd.DataFrame, metrics: Dict) -> List[Dict]:
        """Fallback rule-based insights."""
        insights = []
        
        # Best performing campaign
        if 'ROAS' in df.columns and 'Campaign_Name' in df.columns:
            best = df.loc[df['ROAS'].idxmax()]
            insights.append({
                "category": "Performance",
                "insight": f"{best['Campaign_Name']} achieved highest ROAS of {best['ROAS']:.2f}x",
                "impact": "High",
                "explanation": "This campaign demonstrates best practices worth replicating"
            })
        
        return insights
    
    def _generate_rule_based_recommendations(self, df: pd.DataFrame, metrics: Dict) -> List[Dict]:
        """Fallback rule-based recommendations."""
        recommendations = []
        
        # Scale winners
        if 'ROAS' in df.columns:
            high_roas = df[df['ROAS'] > 4.0]
            if len(high_roas) > 0:
                recommendations.append({
                    "priority": "High",
                    "recommendation": f"Scale the {len(high_roas)} campaigns with ROAS > 4.0x",
                    "expected_impact": "20-30% increase in conversions",
                    "implementation": "Increase budgets by 50% incrementally",
                    "timeline": "1-2 weeks",
                    "estimated_roi": "25%",
                    "focus_area": "ROAS"
                })
        
        return recommendations
    
    def _analyze_funnel(self, df: pd.DataFrame, metrics: Dict) -> Dict[str, Any]:
        """Analyze marketing funnel performance with intelligent stage detection."""
        funnel = {
            "stages": {},
            "conversion_rates": {},
            "drop_off_points": [],
            "recommendations": [],
            "by_funnel_stage": {}
        }
        
        # Helper function to detect funnel stage from text
        def detect_funnel_stage(text: str) -> str:
            """Detect funnel stage from campaign/placement/ad set name."""
            if not isinstance(text, str):
                return "Unknown"
            text_lower = text.lower()
            
            # Awareness patterns
            awareness_patterns = ['awareness', 'aw', 'awa', 'tofu', 'top-of-funnel', 'brand', 'reach', 'impression']
            if any(pattern in text_lower for pattern in awareness_patterns):
                return "Awareness"
            
            # Consideration patterns
            consideration_patterns = ['consideration', 'co', 'cons', 'mofu', 'mid-funnel', 'engagement', 'interest', 'video view']
            if any(pattern in text_lower for pattern in consideration_patterns):
                return "Consideration"
            
            # Conversion patterns
            conversion_patterns = ['conversion', 'conv', 'bofu', 'bottom-funnel', 'purchase', 'lead', 'signup', 'sale', 'retargeting', 'remarketing']
            if any(pattern in text_lower for pattern in conversion_patterns):
                return "Conversion"
            
            return "Unknown"
        
        # Try to detect funnel stages from column names
        funnel_col = None
        for col in ['Funnel_Stage', 'Funnel', 'Stage', 'Campaign_Type']:
            if col in df.columns:
                funnel_col = col
                break
        
        # If no explicit funnel column, try to infer from campaign/placement/ad set names
        if funnel_col is None:
            df_copy = df.copy()
            # Check multiple columns for funnel indicators
            for col in ['Campaign_Name', 'Placement', 'Placement_Name', 'Ad_Set', 'Ad_Group', 'Adset_Name']:
                if col in df_copy.columns:
                    df_copy['Detected_Funnel_Stage'] = df_copy[col].apply(detect_funnel_stage)
                    # If we found some stages, use this column
                    if df_copy['Detected_Funnel_Stage'].nunique() > 1:
                        funnel_col = 'Detected_Funnel_Stage'
                        df = df_copy
                        break
        
        # Analyze by funnel stage if detected
        if funnel_col and funnel_col in df.columns:
            try:
                funnel_stages = df.groupby(funnel_col).agg({
                    'Spend': 'sum' if 'Spend' in df.columns else lambda x: 0,
                    'Impressions': 'sum' if 'Impressions' in df.columns else lambda x: 0,
                    'Clicks': 'sum' if 'Clicks' in df.columns else lambda x: 0,
                    'Conversions': 'sum' if 'Conversions' in df.columns else lambda x: 0,
                    'ROAS': 'mean' if 'ROAS' in df.columns else lambda x: 0
                })
                
                for stage, row in funnel_stages.iterrows():
                    if stage != "Unknown":
                        funnel["by_funnel_stage"][stage] = {
                            "spend": float(row.get('Spend', 0)),
                            "impressions": int(row.get('Impressions', 0)),
                            "clicks": int(row.get('Clicks', 0)),
                            "conversions": int(row.get('Conversions', 0)),
                            "roas": float(row.get('ROAS', 0)),
                            "ctr": (row.get('Clicks', 0) / row.get('Impressions', 1) * 100) if row.get('Impressions', 0) > 0 else 0,
                            "conversion_rate": (row.get('Conversions', 0) / row.get('Clicks', 1) * 100) if row.get('Clicks', 0) > 0 else 0
                        }
            except Exception as e:
                logger.warning(f"Could not analyze by funnel stage: {e}")
        
        # Calculate overall funnel metrics
        if all(col in df.columns for col in ['Impressions', 'Clicks', 'Conversions']):
            total_impressions = df['Impressions'].sum()
            total_clicks = df['Clicks'].sum()
            total_conversions = df['Conversions'].sum()
            
            funnel["stages"] = {
                "awareness": {
                    "metric": "Impressions",
                    "value": int(total_impressions),
                    "percentage": 100.0
                },
                "consideration": {
                    "metric": "Clicks",
                    "value": int(total_clicks),
                    "percentage": (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
                },
                "conversion": {
                    "metric": "Conversions",
                    "value": int(total_conversions),
                    "percentage": (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
                }
            }
            
            # Calculate conversion rates
            funnel["conversion_rates"] = {
                "awareness_to_consideration": (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
                "consideration_to_conversion": (total_conversions / total_clicks * 100) if total_clicks > 0 else 0,
                "awareness_to_conversion": (total_conversions / total_impressions * 100) if total_impressions > 0 else 0
            }
            
            # Identify drop-off points
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            
            if ctr < 1.5:
                funnel["drop_off_points"].append({
                    "stage": "Awareness to Consideration",
                    "issue": f"Low CTR of {ctr:.2f}% (benchmark: 1.5-3.0%)",
                    "recommendation": "Improve ad creative, headlines, and targeting to increase click-through rate"
                })
            
            if conversion_rate < 2.0:
                funnel["drop_off_points"].append({
                    "stage": "Consideration to Conversion",
                    "issue": f"Low conversion rate of {conversion_rate:.2f}%",
                    "recommendation": "Optimize landing pages, improve offer clarity, or refine audience targeting"
                })
        
        # Platform-specific funnel analysis
        if 'Platform' in df.columns:
            platform_funnels = {}
            try:
                platforms = df['Platform'].unique() if hasattr(df['Platform'], 'unique') else df['Platform'].iloc[:, 0].unique()
            except:
                platforms = []
            for platform in platforms:
                # Handle potential duplicate Platform column
                platform_col = df['Platform']
                if isinstance(platform_col, pd.DataFrame):
                    platform_col = platform_col.iloc[:, 0]
                platform_data = df[platform_col == platform]
                if all(col in platform_data.columns for col in ['Impressions', 'Clicks', 'Conversions']):
                    p_impressions = platform_data['Impressions'].sum()
                    p_clicks = platform_data['Clicks'].sum()
                    p_conversions = platform_data['Conversions'].sum()
                    
                    platform_funnels[platform] = {
                        "ctr": (p_clicks / p_impressions * 100) if p_impressions > 0 else 0,
                        "conversion_rate": (p_conversions / p_clicks * 100) if p_clicks > 0 else 0,
                        "overall_conversion": (p_conversions / p_impressions * 100) if p_impressions > 0 else 0
                    }
            
            funnel["by_platform"] = platform_funnels
        
        return funnel
    
    def _analyze_roas_revenue(self, df: pd.DataFrame, metrics: Dict) -> Dict[str, Any]:
        """Analyze ROAS and revenue performance with graceful handling of missing/zero values."""
        roas_analysis = {
            "overall": {},
            "by_platform": {},
            "by_campaign": {},
            "efficiency_tiers": {},
            "revenue_attribution": {},
            "data_quality": {
                "has_roas": False,
                "has_revenue": False,
                "zero_roas_count": 0,
                "missing_data_warning": None
            }
        }
        
        # Check for ROAS and Revenue columns
        has_roas = 'ROAS' in df.columns
        revenue_col = self._get_column(df, 'revenue')
        has_revenue = revenue_col is not None
        
        roas_analysis["data_quality"]["has_roas"] = has_roas
        roas_analysis["data_quality"]["has_revenue"] = has_revenue
        
        # If neither ROAS nor Revenue exists, return early with warning
        if not has_roas and not has_revenue:
            roas_analysis["data_quality"]["missing_data_warning"] = (
                "No ROAS or Revenue data available. Revenue analysis skipped. "
                "Consider adding Revenue or Conversion Value columns for ROI insights."
            )
            logger.warning("ROAS/Revenue analysis skipped: No revenue data available")
            return roas_analysis
        
        if has_roas and 'Spend' in df.columns:
            # Filter out zero and NaN ROAS values
            df_valid = df[(df['ROAS'].notna()) & (df['ROAS'] > 0)].copy()
            zero_roas_count = len(df[df['ROAS'] == 0])
            roas_analysis["data_quality"]["zero_roas_count"] = zero_roas_count
            
            if zero_roas_count > 0:
                logger.info(f"Found {zero_roas_count} records with zero ROAS - excluding from analysis")
            
            if df_valid.empty:
                roas_analysis["data_quality"]["missing_data_warning"] = (
                    f"All ROAS values are zero or missing ({len(df)} records). "
                    "Unable to calculate meaningful ROAS metrics."
                )
                return roas_analysis
            
            # Overall ROAS analysis (using valid data only)
            total_spend = df_valid['Spend'].sum()
            avg_roas = df_valid['ROAS'].mean()
            weighted_roas = (df_valid['ROAS'] * df_valid['Spend']).sum() / total_spend if total_spend > 0 else 0
            
            # Calculate implied revenue
            implied_revenue = total_spend * weighted_roas
            
            roas_analysis["overall"] = {
                "average_roas": float(avg_roas),
                "weighted_roas": float(weighted_roas),
                "total_spend": float(total_spend),
                "implied_revenue": float(implied_revenue),
                "profit": float(implied_revenue - total_spend),
                "profit_margin": float(((implied_revenue - total_spend) / implied_revenue * 100)) if implied_revenue > 0 else 0
            }
            
            # ROAS by platform (use valid data only)
            if 'Platform' in df_valid.columns:
                platform_roas = df_valid.groupby('Platform').agg({
                    'ROAS': 'mean',
                    'Spend': 'sum'
                })
                
                for platform, row in platform_roas.iterrows():
                    if pd.notna(row['ROAS']) and row['ROAS'] > 0:
                        platform_revenue = row['Spend'] * row['ROAS']
                        roas_analysis["by_platform"][platform] = {
                            "roas": float(row['ROAS']),
                            "spend": float(row['Spend']),
                            "revenue": float(platform_revenue),
                            "profit": float(platform_revenue - row['Spend']),
                            "vs_benchmark": self._compare_to_benchmark(platform, row['ROAS'])
                        }
            
            # Efficiency tiers (use valid data only)
            roas_analysis["efficiency_tiers"] = {
                "excellent": {
                    "count": len(df_valid[df_valid['ROAS'] >= 4.5]),
                    "spend": float(df_valid[df_valid['ROAS'] >= 4.5]['Spend'].sum()),
                    "avg_roas": float(df_valid[df_valid['ROAS'] >= 4.5]['ROAS'].mean()) if len(df_valid[df_valid['ROAS'] >= 4.5]) > 0 else 0
                },
                "good": {
                    "count": len(df_valid[(df_valid['ROAS'] >= 3.5) & (df_valid['ROAS'] < 4.5)]),
                    "spend": float(df_valid[(df_valid['ROAS'] >= 3.5) & (df_valid['ROAS'] < 4.5)]['Spend'].sum()),
                    "avg_roas": float(df_valid[(df_valid['ROAS'] >= 3.5) & (df_valid['ROAS'] < 4.5)]['ROAS'].mean()) if len(df_valid[(df_valid['ROAS'] >= 3.5) & (df_valid['ROAS'] < 4.5)]) > 0 else 0
                },
                "needs_improvement": {
                    "count": len(df_valid[df_valid['ROAS'] < 3.5]),
                    "spend": float(df_valid[df_valid['ROAS'] < 3.5]['Spend'].sum()),
                    "avg_roas": float(df_valid[df_valid['ROAS'] < 3.5]['ROAS'].mean()) if len(df_valid[df_valid['ROAS'] < 3.5]) > 0 else 0
                }
            }
        
        return roas_analysis
    
    def _analyze_audience(self, df: pd.DataFrame, metrics: Dict) -> Dict[str, Any]:
        """Analyze audience performance (if data available)."""
        audience_analysis = {
            "available": False,
            "insights": [],
            "recommendations": []
        }
        
        # Check for audience-related columns
        audience_columns = [col for col in df.columns if any(keyword in col.lower() 
                           for keyword in ['audience', 'demographic', 'age', 'gender', 'interest', 'segment'])]
        
        if audience_columns:
            audience_analysis["available"] = True
            audience_analysis["columns_found"] = audience_columns
            audience_analysis["insights"].append({
                "insight": f"Found {len(audience_columns)} audience-related data columns",
                "recommendation": "Analyze performance by audience segment to optimize targeting"
            })
        else:
            audience_analysis["insights"].append({
                "insight": "No audience segmentation data found in current dataset",
                "recommendation": "Consider adding audience data (demographics, interests, behaviors) for deeper analysis"
            })
        
        # Platform-based audience insights
        if 'Platform' in df.columns:
            audience_analysis["platform_strengths"] = {
                "google_ads": "Strong for intent-based audiences (search keywords, in-market)",
                "meta_ads": "Excellent for demographic and interest-based targeting, lookalikes",
                "linkedin_ads": "Best for B2B, job title, company size, industry targeting",
                "dv360": "Programmatic audiences, third-party data, contextual targeting",
                "snapchat_ads": "Young demographics (13-34), mobile-first audiences",
                "cm360": "Cross-device audiences, attribution-based optimization"
            }
        
        return audience_analysis
    
    def _analyze_tactics(self, df: pd.DataFrame, metrics: Dict) -> Dict[str, Any]:
        """Analyze tactical execution and performance."""
        tactics_analysis = {
            "bidding_insights": [],
            "creative_insights": [],
            "placement_insights": [],
            "timing_insights": []
        }
        
        # CTR analysis (creative performance proxy)
        if 'CTR' in df.columns:
            avg_ctr = df['CTR'].mean()
            high_ctr = df[df['CTR'] > 2.5]
            low_ctr = df[df['CTR'] < 1.5]
            
            tactics_analysis["creative_insights"].append({
                "metric": "CTR Analysis",
                "average": f"{avg_ctr:.2f}%",
                "high_performers": len(high_ctr),
                "low_performers": len(low_ctr),
                "recommendation": "Analyze high-CTR creatives and replicate winning elements" if len(high_ctr) > 0 else "Test new creative variations to improve CTR"
            })
        
        # CPA analysis (bidding efficiency)
        if 'CPA' in df.columns:
            avg_cpa = df['CPA'].mean()
            cpa_std = df['CPA'].std()
            
            tactics_analysis["bidding_insights"].append({
                "metric": "CPA Consistency",
                "average": f"${avg_cpa:.2f}",
                "std_deviation": f"${cpa_std:.2f}",
                "recommendation": "High CPA variance suggests inconsistent bidding - consider automated bidding strategies" if cpa_std > avg_cpa * 0.3 else "CPA is consistent - current bidding strategy is working well"
            })
        
        # Platform-specific tactical recommendations
        if 'Platform' in df.columns:
            try:
                platforms = df['Platform'].unique() if hasattr(df['Platform'], 'unique') else df['Platform'].iloc[:, 0].unique()
            except:
                platforms = []
            for platform in platforms:
                platform_tactics = self._get_platform_tactics(platform)
                tactics_analysis["placement_insights"].append({
                    "platform": platform,
                    "recommended_tactics": platform_tactics
                })
        
        # Time-based insights
        if 'Date' in df.columns:
            df['DayOfWeek'] = pd.to_datetime(df['Date']).dt.day_name()
            if 'Conversions' in df.columns:
                day_performance = df.groupby('DayOfWeek')['Conversions'].sum().to_dict()
                best_day = max(day_performance, key=day_performance.get)
                
                tactics_analysis["timing_insights"].append({
                    "metric": "Day of Week Performance",
                    "best_day": best_day,
                    "recommendation": f"Consider increasing bids on {best_day} when conversion rates are highest"
                })
        
        return tactics_analysis
    
    def _compare_to_benchmark(self, platform: str, roas: float) -> str:
        """Compare ROAS to industry benchmarks."""
        benchmarks = {
            "google_ads": (2.0, 4.0),
            "meta_ads": (2.5, 4.5),
            "linkedin_ads": (2.0, 3.5),
            "dv360": (1.5, 3.0),
            "snapchat_ads": (2.0, 3.5),
            "cm360": (1.5, 3.0)
        }
        
        if platform in benchmarks:
            low, high = benchmarks[platform]
            if roas >= high:
                return f"Excellent (above {high}x benchmark)"
            elif roas >= low:
                return f"Good (within {low}-{high}x benchmark)"
            else:
                return f"Below benchmark (target: {low}-{high}x)"
        
        return "No benchmark available"
    
    def _get_platform_tactics(self, platform: str) -> List[str]:
        """Get platform-specific tactical recommendations."""
        tactics = {
            "google_ads": [
                "Use Target ROAS bidding for conversion optimization",
                "Implement responsive search ads with 15 headlines",
                "Leverage audience segments for bid adjustments",
                "Test Performance Max campaigns for full-funnel"
            ],
            "meta_ads": [
                "Create Advantage+ campaigns for automated optimization",
                "Use Lookalike audiences from top converters",
                "Test Reels and Stories placements",
                "Implement dynamic creative optimization"
            ],
            "linkedin_ads": [
                "Target by job title and seniority for B2B",
                "Use Matched Audiences for retargeting",
                "Test Conversation Ads for engagement",
                "Implement lead gen forms for lower friction"
            ],
            "dv360": [
                "Leverage programmatic guaranteed deals",
                "Use contextual targeting for brand safety",
                "Implement frequency capping",
                "Test connected TV placements"
            ],
            "snapchat_ads": [
                "Focus on vertical video creative",
                "Use Snap Pixel for conversion tracking",
                "Test AR lenses for engagement",
                "Target Gen Z with trending content"
            ],
            "cm360": [
                "Implement cross-device attribution",
                "Use floodlight tags for conversion tracking",
                "Leverage audience insights for optimization",
                "Test sequential messaging strategies"
            ]
        }
        
        return tactics.get(platform, ["Platform-specific tactics not available"])
    
    # ==================== RAG-ENHANCED METHODS (EXPERIMENTAL) ====================
    # These methods are isolated and do NOT affect existing functionality
    
    def _initialize_rag_engine(self):
        """Lazy initialization of RAG engine (only when needed).
        
        Uses existing knowledge base from data/knowledge_base.json if available.
        Builds vector store on first use if not already built.
        """
        if hasattr(self, '_rag_engine') and self._rag_engine is not None:
            return self._rag_engine
        
        try:
            from ..knowledge.vector_store import VectorStoreConfig, VectorStoreBuilder, VectorRetriever, HybridRetriever
            from pathlib import Path
            import json
            
            # Check if vector store exists, if not build it from existing knowledge base
            config = VectorStoreConfig()
            
            if not config.index_path.exists() or not config.metadata_path.exists():
                logger.info("Vector store not found. Building from existing knowledge base...")
                
                # Load existing knowledge base
                kb_path = Path("data/knowledge_base.json")
                if kb_path.exists():
                    with open(kb_path, 'r', encoding='utf-8') as f:
                        documents = json.load(f)
                    
                    logger.info(f"Loaded {len(documents)} documents from knowledge base")
                    
                    # Build vector store
                    builder = VectorStoreBuilder(
                        config=config,
                        client=self.client if not self.use_anthropic else None
                    )
                    builder.build_from_documents(documents)
                    logger.info("Vector store built successfully")
                else:
                    logger.warning(f"Knowledge base not found at {kb_path}")
                    self._rag_engine = None
                    return None
            
            # Initialize retrievers
            vector_retriever = VectorRetriever(config=config)
            hybrid_retriever = HybridRetriever(config=config, use_keyword=True, use_rerank=False)
            
            # Create a simple RAG engine wrapper
            class SimpleRAGEngine:
                def __init__(self, vector_retriever, hybrid_retriever):
                    self.vector_retriever = vector_retriever
                    self.hybrid_retriever = hybrid_retriever
            
            self._rag_engine = SimpleRAGEngine(vector_retriever, hybrid_retriever)
            logger.info("RAG engine initialized successfully with existing knowledge base")
            return self._rag_engine
            
        except Exception as e:
            logger.warning(f"Failed to initialize RAG engine: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            self._rag_engine = None
            return None
    
    def _retrieve_rag_context(self, metrics: Dict, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge from RAG system.
        
        Args:
            metrics: Campaign metrics dictionary
            top_k: Number of top knowledge chunks to retrieve
            
        Returns:
            List of relevant knowledge chunks with metadata
        """
        rag_engine = self._initialize_rag_engine()
        if rag_engine is None:
            logger.warning("RAG engine not available, returning empty context")
            return []
        
        try:
            # Build retrieval query from metrics
            overview = metrics.get('overview', {})
            platform_metrics = metrics.get('by_platform', {})
            
            # Construct query based on key metrics
            query_parts = []
            
            # Add performance context
            if overview.get('avg_roas'):
                query_parts.append(f"ROAS {overview['avg_roas']:.2f}x")
            if overview.get('avg_cpa'):
                query_parts.append(f"CPA ${overview['avg_cpa']:.2f}")
            if overview.get('avg_ctr'):
                query_parts.append(f"CTR {overview['avg_ctr']:.2f}%")
            
            # Add platform context
            if platform_metrics:
                platforms = list(platform_metrics.keys())[:3]
                query_parts.append(f"platforms: {', '.join(platforms)}")
            
            # Build retrieval query
            retrieval_query = (
                f"Digital marketing campaign optimization strategies for "
                f"{' '.join(query_parts)}. "
                f"Industry benchmarks, best practices, and tactical recommendations."
            )
            
            logger.info(f"RAG retrieval query: {retrieval_query}")
            
            # Retrieve relevant knowledge using hybrid retriever (vector + keyword)
            if hasattr(rag_engine, 'hybrid_retriever') and rag_engine.hybrid_retriever:
                results = rag_engine.hybrid_retriever.search(retrieval_query, top_k=top_k)
            elif hasattr(rag_engine, 'vector_retriever') and rag_engine.vector_retriever:
                results = rag_engine.vector_retriever.search(retrieval_query, top_k=top_k)
            else:
                logger.warning("No retriever available in RAG engine")
                return []
            
            # Format results
            knowledge_chunks = []
            for result in results:
                knowledge_chunks.append({
                    'content': result.get('text', ''),
                    'source': result.get('metadata', {}).get('title', 'unknown'),
                    'score': result.get('score', 0.0)
                })
            
            logger.info(f"Retrieved {len(knowledge_chunks)} knowledge chunks from RAG")
            return knowledge_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving RAG context: {e}")
            return []
    
    def _build_rag_augmented_prompt(self, 
                                   metrics: Dict, 
                                   insights: List, 
                                   recommendations: List,
                                   rag_context: List[Dict[str, Any]]) -> str:
        """Build prompt augmented with RAG-retrieved knowledge.
        
        Args:
            metrics: Campaign metrics
            insights: Generated insights
            recommendations: Generated recommendations
            rag_context: Retrieved knowledge chunks
            
        Returns:
            RAG-augmented prompt string
        """
        # Build knowledge context section
        knowledge_section = ""
        if rag_context:
            knowledge_section = "\n\n## EXTERNAL KNOWLEDGE & BENCHMARKS\n\n"
            for idx, chunk in enumerate(rag_context, 1):
                source = chunk.get('source', 'unknown')
                content = chunk.get('content', '')
                knowledge_section += f"### Source {idx}: {source}\n{content}\n\n"
        
        # Get base summary data (same as standard method)
        summary_data = self._prepare_summary_data(metrics, insights, recommendations)
        
        # Build RAG-augmented prompt
        prompt = f"""You are an expert digital marketing analyst with access to industry benchmarks and best practices.

{knowledge_section}

## CAMPAIGN DATA

{json.dumps(summary_data, indent=2)}

## INSTRUCTIONS

Generate a comprehensive executive summary that:

1. **Benchmarking**: Compare metrics against industry standards from the external knowledge above
2. **Specific Recommendations**: Provide concrete, actionable tactics based on proven best practices
3. **Source-Backed Insights**: Reference specific benchmarks and sources when making claims
4. **Context-Aware**: Use platform-specific strategies from the knowledge base

### BRIEF SUMMARY (3-4 sentences)
- Start with overall performance vs benchmarks
- Highlight 1-2 key wins with specific numbers
- Note 1 critical optimization opportunity
- End with highest-impact recommendation

### DETAILED SUMMARY (2-3 paragraphs)
- **Performance Analysis**: Compare all key metrics (ROAS, CPA, CTR) against industry benchmarks
- **Platform Insights**: Analyze each platform's performance with specific tactics
- **Optimization Roadmap**: Prioritized action plan with expected impact

**CRITICAL FORMATTING RULES:**
- NO asterisks, underscores, or markdown formatting
- Always add space between numbers and text (e.g., "973K revenue" not "973Krevenue")
- Use clear paragraph breaks
- Keep it professional and data-driven

Generate the executive summary now:"""
        
        return prompt
    
    def _prepare_summary_data(self, metrics: Dict, insights: List, recommendations: List) -> Dict:
        """Prepare summary data dictionary (shared by both standard and RAG methods)."""
        # Convert to JSON-serializable format
        def make_serializable(obj):
            """Convert pandas objects to JSON-serializable types."""
            if isinstance(obj, pd.Series):
                return obj.to_dict()
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict('records')
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            return obj
        
        overview = make_serializable(metrics.get('overview', {}))
        platform_metrics = metrics.get('by_platform', {})
        campaign_metrics = metrics.get('by_campaign', {})
        
        # Find best and worst performers
        best_platform = None
        worst_platform = None
        if platform_metrics:
            platforms_with_roas = {
                p: m.get('roas', 0) 
                for p, m in platform_metrics.items() 
                if m.get('roas', 0) > 0
            }
            if platforms_with_roas:
                best_platform = max(platforms_with_roas.items(), key=lambda x: x[1])
                worst_platform = min(platforms_with_roas.items(), key=lambda x: x[1])
        
        summary_data = {
            'overview': overview,
            'best_platform': {
                'name': best_platform[0] if best_platform else 'N/A',
                'roas': best_platform[1] if best_platform else 0
            },
            'worst_platform': {
                'name': worst_platform[0] if worst_platform else 'N/A',
                'roas': worst_platform[1] if worst_platform else 0
            },
            'top_insights': insights[:5],
            'top_recommendations': recommendations[:5],
            'platform_count': len(platform_metrics),
            'campaign_count': len(campaign_metrics)
        }
        
        return summary_data
    
    def _generate_executive_summary_with_rag(self, 
                                            metrics: Dict, 
                                            insights: List, 
                                            recommendations: List) -> Dict[str, str]:
        """Generate RAG-enhanced executive summary (EXPERIMENTAL - ISOLATED METHOD).
        
        This method does NOT affect the existing _generate_executive_summary method.
        It's a completely separate implementation for A/B testing.
        
        Args:
            metrics: Campaign performance metrics
            insights: List of generated insights
            recommendations: List of recommendations
            
        Returns:
            Dictionary with 'brief' and 'detailed' summaries, plus RAG metadata
        """
        import time
        start_time = time.time()
        
        logger.info("=== GENERATING RAG-ENHANCED EXECUTIVE SUMMARY ===")
        
        try:
            # Step 1: Retrieve relevant knowledge from RAG
            logger.info("Step 1: Retrieving RAG context...")
            rag_context = self._retrieve_rag_context(metrics, top_k=5)
            
            # Step 2: Build RAG-augmented prompt
            logger.info("Step 2: Building RAG-augmented prompt...")
            rag_prompt = self._build_rag_augmented_prompt(
                metrics, insights, recommendations, rag_context
            )
            
            # Step 3: Call LLM with RAG-augmented prompt
            logger.info("Step 3: Calling LLM with RAG context...")
            
            # Use same LLM fallback logic as standard method
            llm_response = None
            tokens_input = 0
            tokens_output = 0
            model_used = "unknown"
            
            # Try Claude Sonnet first (if using Anthropic)
            if self.use_anthropic and self.anthropic_api_key:
                try:
                    from ..utils.anthropic_helpers import call_anthropic_http
                    result = call_anthropic_http(
                        api_key=self.anthropic_api_key,
                        model=self.model,
                        messages=[{"role": "user", "content": rag_prompt}],
                        max_tokens=4000
                    )
                    llm_response = result.get('content', '')
                    tokens_input = result.get('usage', {}).get('input_tokens', 0)
                    tokens_output = result.get('usage', {}).get('output_tokens', 0)
                    model_used = self.model
                    logger.info(f"RAG summary generated with Claude Sonnet ({tokens_input} + {tokens_output} tokens)")
                except Exception as e:
                    logger.warning(f"Claude Sonnet failed for RAG: {e}, trying Gemini...")
            
            # Fallback to Gemini
            if not llm_response and self.gemini_api_key:
                try:
                    genai.configure(api_key=self.gemini_api_key)
                    model = genai.GenerativeModel('gemini-2.0-flash-exp')
                    response = model.generate_content(rag_prompt)
                    llm_response = response.text
                    # Estimate tokens (Gemini doesn't provide exact counts easily)
                    tokens_input = len(rag_prompt.split()) * 1.3
                    tokens_output = len(llm_response.split()) * 1.3
                    model_used = "gemini-2.0-flash-exp"
                    logger.info(f"RAG summary generated with Gemini (~{int(tokens_input)} + {int(tokens_output)} tokens)")
                except Exception as e:
                    logger.warning(f"Gemini failed for RAG: {e}, trying OpenAI...")
            
            # Fallback to OpenAI
            if not llm_response and self.openai_api_key:
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": rag_prompt}],
                        max_tokens=3000,
                        temperature=0.7
                    )
                    llm_response = response.choices[0].message.content
                    tokens_input = response.usage.prompt_tokens
                    tokens_output = response.usage.completion_tokens
                    model_used = "gpt-4o-mini"
                    logger.info(f"RAG summary generated with GPT-4o-mini ({tokens_input} + {tokens_output} tokens)")
                except Exception as e:
                    logger.error(f"All LLMs failed for RAG summary: {e}")
                    raise
            
            if not llm_response:
                raise Exception("No LLM available for RAG summary generation")
            
            # Step 4: Parse and format response
            logger.info("Step 4: Parsing and formatting RAG response...")
            brief_summary, detailed_summary = self._parse_summary_response(llm_response)
            
            # Apply formatting cleanup
            brief_summary = self._strip_italics(brief_summary)
            detailed_summary = self._strip_italics(detailed_summary)
            
            latency = time.time() - start_time
            
            logger.info(f"=== RAG SUMMARY COMPLETE in {latency:.2f}s ===")
            
            return {
                'brief': brief_summary,
                'detailed': detailed_summary,
                'rag_metadata': {
                    'knowledge_sources': [chunk.get('source') for chunk in rag_context],
                    'retrieval_count': len(rag_context),
                    'tokens_input': int(tokens_input),
                    'tokens_output': int(tokens_output),
                    'model': model_used,
                    'latency': latency
                }
            }
            
        except Exception as e:
            logger.error(f"RAG summary generation failed: {e}")
            logger.warning("Falling back to standard summary generation")
            # Fallback to standard method if RAG fails
            return self._generate_executive_summary(metrics, insights, recommendations)
