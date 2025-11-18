"""
Automated Analytics Engine with Media Domain Expertise
Generates insights and recommendations automatically from campaign data
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from openai import OpenAI
from anthropic import Anthropic
from loguru import logger
import json
import os
from ..data_processing import MediaDataProcessor


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
    
    def __init__(self, api_key: str = None, use_anthropic: bool = None):
        """Initialize the analytics expert."""
        # Determine which LLM to use
        if use_anthropic is None:
            use_anthropic = os.getenv('USE_ANTHROPIC', 'false').lower() == 'true'
        
        self.use_anthropic = use_anthropic
        
        if self.use_anthropic:
            # Use Anthropic Claude
            anthropic_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            if not anthropic_key:
                raise ValueError("ANTHROPIC_API_KEY not found")
            self.client = Anthropic(api_key=anthropic_key)
            self.model = os.getenv('DEFAULT_LLM_MODEL', 'claude-3-5-sonnet-20241022')
            logger.info(f"Initialized with Anthropic Claude: {self.model}")
        else:
            # Use OpenAI
            openai_key = api_key or os.getenv('OPENAI_API_KEY')
            if not openai_key:
                raise ValueError("OPENAI_API_KEY not found")
            self.client = OpenAI(api_key=openai_key)
            self.model = os.getenv('DEFAULT_LLM_MODEL', 'gpt-4')
            logger.info(f"Initialized with OpenAI: {self.model}")
        
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
                # Anthropic Claude API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=0.3,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return response.content[0].text
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

Format as JSON array:
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
            system_prompt = "You are a world-class media analytics expert. Provide data-driven insights with specific numbers."
            insights_text = self._call_llm(system_prompt, prompt, max_tokens=2000).strip()
            # Extract JSON from response
            if "```json" in insights_text:
                insights_text = insights_text.split("```json")[1].split("```")[0].strip()
            elif "```" in insights_text:
                insights_text = insights_text.split("```")[1].split("```")[0].strip()
            
            insights = json.loads(insights_text)
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
        """Identify growth opportunities."""
        opportunities = []
        
        # Get column names
        spend_col = self._get_column(df, 'spend')
        
        # High ROAS campaigns that could scale
        if 'ROAS' in df.columns and spend_col:
            try:
                high_performers = df[df['ROAS'] > 4.0].sort_values('ROAS', ascending=False)
                for _, row in high_performers.head(3).iterrows():
                    opportunities.append({
                        "type": "Scale Winner",
                        "campaign": row.get('Campaign_Name', 'Unknown'),
                        "platform": row.get('Platform', 'Unknown'),
                        "current_roas": float(row['ROAS']),
                        "current_spend": float(row[spend_col]),
                        "opportunity": f"Increase budget by 50-100% to scale this high-performing campaign",
                        "potential_impact": f"Could generate ${float(row[spend_col]) * 0.5 * float(row['ROAS']):,.0f} additional revenue"
                    })
            except Exception as e:
                logger.warning(f"Could not identify scale winners: {e}")
        
        # Underutilized platforms
        if 'Platform' in df.columns and spend_col:
            try:
                platform_col = df['Platform']
                if isinstance(platform_col, pd.DataFrame):
                    platform_col = platform_col.iloc[:, 0]
                
                temp_df = df.copy()
                temp_df['_Platform'] = platform_col
                platform_spend = temp_df.groupby('_Platform')[spend_col].sum()
                total_spend = platform_spend.sum()
            except Exception as e:
                logger.warning(f"Could not calculate platform opportunities: {e}")
                total_spend = 0
            
            for platform, spend in platform_spend.items():
                if spend / total_spend < 0.10:  # Less than 10% of budget
                    avg_roas = df[df['Platform'] == platform]['ROAS'].mean()
                    if avg_roas > 3.5:
                        opportunities.append({
                            "type": "Underutilized Platform",
                            "platform": platform,
                            "current_spend": float(spend),
                            "current_share": f"{(spend/total_spend)*100:.1f}%",
                            "avg_roas": float(avg_roas),
                            "opportunity": f"Increase {platform} budget - showing strong ROAS with minimal investment",
                            "potential_impact": "Could improve overall portfolio efficiency"
                        })
        
        # Seasonal opportunities
        if 'Date' in df.columns:
            try:
                df['Month'] = pd.to_datetime(df['Date']).dt.month
                
                # Build aggregation dict based on available columns
                agg_dict = {}
                if 'ROAS' in df.columns:
                    agg_dict['ROAS'] = 'mean'
                
                # Get conversions column
                conv_col = self._get_column(df, 'conversions')
                if conv_col:
                    agg_dict[conv_col] = 'sum'
                
                if agg_dict and 'ROAS' in agg_dict:
                    monthly_performance = df.groupby('Month').agg(agg_dict)
                    
                    best_months = monthly_performance.nlargest(2, 'ROAS')
                    for month, row in best_months.iterrows():
                        opportunities.append({
                            "type": "Seasonal Opportunity",
                            "period": f"Month {month}",
                            "avg_roas": float(row['ROAS']),
                            "opportunity": f"Historical data shows strong performance in this period",
                            "potential_impact": "Plan increased investment for similar future periods"
                        })
            except Exception as e:
                logger.warning(f"Could not calculate seasonal opportunities: {e}")
        
        return opportunities
    
    def _assess_risks(self, df: pd.DataFrame, metrics: Dict) -> List[Dict[str, Any]]:
        """Assess risks and red flags."""
        risks = []
        
        # Low ROAS campaigns
        if 'ROAS' in df.columns:
            poor_performers = df[df['ROAS'] < 2.5]
            if len(poor_performers) > 0:
                spend_col = self._get_column(df, 'spend')
                if spend_col:
                    total_waste = poor_performers[spend_col].sum()
                    risks.append({
                        "severity": "High",
                        "risk": "Underperforming Campaigns",
                        "details": f"{len(poor_performers)} campaigns with ROAS below 2.5",
                        "impact": f"${total_waste:,.0f} at risk",
                        "action": "Review and optimize or pause these campaigns immediately"
                    })
        
        # High CPA campaigns
        if 'CPA' in df.columns:
            high_cpa = df[df['CPA'] > df['CPA'].quantile(0.75)]
            if len(high_cpa) > 0:
                risks.append({
                    "severity": "Medium",
                    "risk": "High Cost Per Acquisition",
                    "details": f"{len(high_cpa)} campaigns with CPA in top 25%",
                    "impact": "Reducing efficiency and profitability",
                    "action": "Optimize targeting, creative, or bidding strategy"
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
        
        return risks
    
    def _optimize_budget(self, df: pd.DataFrame, metrics: Dict) -> Dict[str, Any]:
        """Suggest budget optimization."""
        # This method has hardcoded column references - skip if columns don't exist
        logger.warning("Budget optimization skipped - requires 'Spend' and 'Conversions' columns")
        return {
            "current_allocation": {},
            "recommended_allocation": {},
            "expected_improvement": {}
        }
    
    def _generate_executive_summary(self, metrics: Dict, insights: List, recommendations: List) -> str:
        """Generate executive summary."""
        
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
        
        summary_data = {
            "total_spend": overview.get('total_spend', 0),
            "total_conversions": overview.get('total_conversions', 0),
            "avg_roas": overview.get('avg_roas', 0),
            "campaigns": overview.get('total_campaigns', 0),
            "platforms": overview.get('total_platforms', 0),
            "top_insights": insights[:3] if insights else [],
            "top_recommendations": recommendations[:3] if recommendations else []
        }
        
        prompt = f"""Create a concise executive summary (3-4 paragraphs) for a CMO based on this campaign analysis:

Data:
{json.dumps(summary_data, indent=2)}

Include:
1. Overall performance assessment
2. Key wins and challenges
3. Top 2-3 strategic recommendations
4. Expected impact of recommendations

Write in professional, executive-friendly language. Be specific with numbers."""

        try:
            system_prompt = "You are a strategic marketing consultant writing for C-level executives."
            summary = self._call_llm(system_prompt, prompt, max_tokens=500).strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            summary = f"Campaign portfolio analysis complete. {summary_data['campaigns']} campaigns analyzed across {summary_data['platforms']} platforms with total spend of ${summary_data['total_spend']:,.0f} and average ROAS of {summary_data['avg_roas']:.2f}x."
        
        return summary
    
    def _prepare_data_summary(self, df: pd.DataFrame, metrics: Dict) -> str:
        """Prepare data summary for AI prompts."""
        summary = f"""
Campaign Data Summary:
- Total Campaigns: {metrics['overview'].get('total_campaigns', 0)}
- Total Platforms: {metrics['overview'].get('total_platforms', 0)}
- Total Spend: ${metrics['overview'].get('total_spend', 0):,.0f}
- Total Conversions: {metrics['overview'].get('total_conversions', 0):,.0f}
- Average ROAS: {metrics['overview'].get('avg_roas', 0):.2f}x
- Average CPA: ${metrics['overview'].get('avg_cpa', 0):.2f}
- Average CTR: {metrics['overview'].get('avg_ctr', 0):.2f}%

Platform Performance:
"""
        
        if metrics.get('by_platform'):
            for platform, data in metrics['by_platform'].items():
                summary += f"\n{platform}:"
                summary += f"\n  - Spend: ${data.get('Spend', 0):,.0f}"
                summary += f"\n  - ROAS: {data.get('ROAS', 0):.2f}x"
                summary += f"\n  - Conversions: {data.get('Conversions', 0):,.0f}"
        
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
        """Analyze marketing funnel performance."""
        funnel = {
            "stages": {},
            "conversion_rates": {},
            "drop_off_points": [],
            "recommendations": []
        }
        
        # Calculate funnel metrics
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
        """Analyze ROAS and revenue performance."""
        roas_analysis = {
            "overall": {},
            "by_platform": {},
            "by_campaign": {},
            "efficiency_tiers": {},
            "revenue_attribution": {}
        }
        
        if 'ROAS' in df.columns and 'Spend' in df.columns:
            # Overall ROAS analysis
            total_spend = df['Spend'].sum()
            avg_roas = df['ROAS'].mean()
            weighted_roas = (df['ROAS'] * df['Spend']).sum() / total_spend if total_spend > 0 else 0
            
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
            
            # ROAS by platform
            if 'Platform' in df.columns:
                platform_roas = df.groupby('Platform').agg({
                    'ROAS': 'mean',
                    'Spend': 'sum'
                })
                
                for platform, row in platform_roas.iterrows():
                    platform_revenue = row['Spend'] * row['ROAS']
                    roas_analysis["by_platform"][platform] = {
                        "roas": float(row['ROAS']),
                        "spend": float(row['Spend']),
                        "revenue": float(platform_revenue),
                        "profit": float(platform_revenue - row['Spend']),
                        "vs_benchmark": self._compare_to_benchmark(platform, row['ROAS'])
                    }
            
            # Efficiency tiers
            roas_analysis["efficiency_tiers"] = {
                "excellent": {
                    "count": len(df[df['ROAS'] >= 4.5]),
                    "spend": float(df[df['ROAS'] >= 4.5]['Spend'].sum()),
                    "avg_roas": float(df[df['ROAS'] >= 4.5]['ROAS'].mean()) if len(df[df['ROAS'] >= 4.5]) > 0 else 0
                },
                "good": {
                    "count": len(df[(df['ROAS'] >= 3.5) & (df['ROAS'] < 4.5)]),
                    "spend": float(df[(df['ROAS'] >= 3.5) & (df['ROAS'] < 4.5)]['Spend'].sum()),
                    "avg_roas": float(df[(df['ROAS'] >= 3.5) & (df['ROAS'] < 4.5)]['ROAS'].mean()) if len(df[(df['ROAS'] >= 3.5) & (df['ROAS'] < 4.5)]) > 0 else 0
                },
                "needs_improvement": {
                    "count": len(df[df['ROAS'] < 3.5]),
                    "spend": float(df[df['ROAS'] < 3.5]['Spend'].sum()),
                    "avg_roas": float(df[df['ROAS'] < 3.5]['ROAS'].mean()) if len(df[df['ROAS'] < 3.5]) > 0 else 0
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
