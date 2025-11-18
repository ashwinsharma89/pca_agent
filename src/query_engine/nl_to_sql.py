"""
Natural Language to SQL Query Engine
Converts natural language questions into SQL queries using LLM
"""
import duckdb
import pandas as pd
from typing import Dict, Any, Optional, List
from openai import OpenAI
from loguru import logger


class NaturalLanguageQueryEngine:
    """Engine to convert natural language questions to SQL queries and execute them."""
    
    def __init__(self, api_key: str):
        """
        Initialize the query engine.
        
        Args:
            api_key: OpenAI API key for LLM
        """
        self.client = OpenAI(api_key=api_key)
        self.conn = None
        self.schema_info = None
        logger.info("Initialized NaturalLanguageQueryEngine")
    
    def load_data(self, df: pd.DataFrame, table_name: str = "campaigns"):
        """
        Load data into DuckDB.
        
        Args:
            df: DataFrame with campaign data
            table_name: Name for the table
        """
        # Convert Date column to datetime if it exists
        df_copy = df.copy()
        date_columns = [col for col in df_copy.columns if 'date' in col.lower()]
        for col in date_columns:
            try:
                df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
                logger.info(f"Converted {col} to datetime")
            except:
                logger.warning(f"Could not convert {col} to datetime")
        
        self.conn = duckdb.connect(':memory:')
        self.conn.register(table_name, df_copy)
        
        # Store schema information
        self.schema_info = {
            "table_name": table_name,
            "columns": df_copy.columns.tolist(),
            "dtypes": df_copy.dtypes.to_dict(),
            "sample_data": df_copy.head(3).to_dict('records')
        }
        
        logger.info(f"Loaded {len(df_copy)} rows into table '{table_name}'")
    
    def generate_sql(self, question: str) -> str:
        """
        Convert natural language question to SQL query.
        
        Args:
            question: Natural language question
            
        Returns:
            SQL query string
        """
        schema_description = self._get_schema_description()
        
        prompt = f"""You are a SQL expert specializing in marketing campaign analytics. Convert the following natural language question into a DuckDB SQL query.

Database Schema:
{schema_description}

🔴 CRITICAL AGGREGATION RULES - NEVER VIOLATE:

For calculated/rate metrics (CTR, CPC, CPM, CPA, ROAS, Conversion Rate), you MUST:
✓ ALWAYS compute from aggregates: SUM(numerator) / SUM(denominator)
✗ NEVER use AVG() on pre-calculated rate columns

Examples:
- CTR = (SUM(Clicks) / NULLIF(SUM(Impressions), 0)) * 100
- CPC = SUM(Spend) / NULLIF(SUM(Clicks), 0)
- CPM = (SUM(Spend) / NULLIF(SUM(Impressions), 0)) * 1000
- CPA = SUM(Spend) / NULLIF(SUM(Conversions), 0)
- ROAS = SUM(Revenue) / NULLIF(SUM(Spend), 0)  [or use Conversion_Value if Revenue not available]
- Conversion_Rate = (SUM(Conversions) / NULLIF(SUM(Clicks), 0)) * 100

⏰ TEMPORAL COMPARISON PATTERNS:

Understand these time phrases and map to SQL:
- "last 2 weeks" → WHERE Date >= CURRENT_DATE - INTERVAL 14 DAY
- "previous 2 weeks" → WHERE Date >= CURRENT_DATE - INTERVAL 28 DAY AND Date < CURRENT_DATE - INTERVAL 14 DAY
- "last month" → WHERE Date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL 1 MONTH)
- "last 2 months" → WHERE Date >= CURRENT_DATE - INTERVAL 60 DAY
- "last 6 months" → WHERE Date >= CURRENT_DATE - INTERVAL 180 DAY
- "last 2 years" → WHERE Date >= CURRENT_DATE - INTERVAL 730 DAY
- "couple of months" → treat as 2 months (60 days)
- "week-over-week" → GROUP BY DATE_TRUNC('week', Date)
- "month-over-month" → GROUP BY DATE_TRUNC('month', Date)
- "Q3 vs Q2" → use QUARTER(Date) or DATE_TRUNC('quarter', Date)
- "year-over-year" → compare same period across different years using YEAR(Date)

For comparisons ("last X vs previous X"):
- Use CASE WHEN to create period labels
- Calculate metrics separately for each period
- Use CTEs or subqueries for clarity

📊 MULTI-DIMENSIONAL ANALYSIS:

- Channel analysis: GROUP BY Platform or Channel
- Funnel analysis: Calculate conversion rates between stages
- Segment analysis: GROUP BY demographic/audience columns
- Creative analysis: GROUP BY creative_variant, ad_copy, subject_line columns
- Time analysis: GROUP BY hour, day_of_week, or use DATE_TRUNC

🎯 ADVANCED PATTERNS:

- ROI calculation: (SUM(Revenue) - SUM(Spend)) / NULLIF(SUM(Spend), 0)
- Budget variance: SUM(Actual_Spend) - SUM(Budgeted_Spend)
- Growth rate: ((current - previous) / NULLIF(previous, 0)) * 100
- Drop-off rate: (stage1_count - stage2_count) / NULLIF(stage1_count, 0) * 100

📝 SQL BEST PRACTICES:

- Use NULLIF to prevent division by zero
- Cast Date columns: CAST(Date AS DATE) or TRY_CAST(Date AS DATE)
- Use CTEs for complex multi-step queries
- Round decimals appropriately: ROUND(value, 2)
- Use descriptive column aliases
- For percentages, multiply by 100
- Column names are case-sensitive
- ⚠️ IMPORTANT: If column names contain underscores (e.g., Ad_Type, Device_Type), use them AS-IS without quotes
- ⚠️ If a column name is a SQL keyword (Type, Order, Group), wrap it in double quotes: "Type"
- Always reference columns exactly as they appear in the schema

🔬 ADVANCED ANALYTICAL PATTERNS:

**Anomaly Detection:**
- Use STDDEV() and AVG() to identify outliers: WHERE metric > AVG(metric) + 2*STDDEV(metric)
- Window functions for moving averages: AVG(metric) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
- Percent change from baseline: ((current - baseline) / NULLIF(baseline, 0)) * 100

**Cohort Analysis:**
- Use DATE_TRUNC to group by acquisition period
- Self-joins or window functions to compare cohorts
- Retention analysis: COUNT(DISTINCT user_id) by time period

**Trend Analysis:**
- Linear regression slope: REGR_SLOPE(y, x) for trend direction
- Moving averages: AVG(metric) OVER (ORDER BY date ROWS BETWEEN n PRECEDING AND CURRENT ROW)
- Growth rate: ((current - previous) / NULLIF(previous, 0)) * 100
- Cumulative metrics: SUM(metric) OVER (ORDER BY date)

**Statistical Analysis:**
- Standard deviation: STDDEV(metric) for volatility
- Variance: VARIANCE(metric)
- Percentiles: PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY metric) for median
- Correlation: CORR(metric1, metric2)

**Efficiency Analysis:**
- Pareto analysis: Use window functions with PERCENT_RANK() or cumulative sums
- Efficiency frontier: Rank by multiple criteria (volume AND efficiency)
- Marginal analysis: Compare incremental performance at different levels

**Segmentation:**
- CASE WHEN for bucketing (high/medium/low performers)
- NTILE(n) for equal-sized segments
- Clustering by multiple dimensions

**Forecasting Patterns:**
- Historical averages with trend adjustment
- Seasonality detection: GROUP BY DAYOFWEEK(Date) or MONTH(Date)
- Extrapolation: Use historical growth rates to project forward

**Multi-Touch Attribution:**
- Use ARRAY_AGG or STRING_AGG to track journey paths
- Window functions to identify first/last touch: FIRST_VALUE(), LAST_VALUE()
- Count touchpoints: COUNT(*) OVER (PARTITION BY user_id)

**Strategic Insights:**
- Scenario analysis: Use CASE WHEN to model different budget levels
- Optimization: Identify top performers with RANK() or ROW_NUMBER()
- Risk analysis: Calculate concentration with cumulative percentages

Question: {question}

SQL Query:"""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a SQL expert that converts natural language to SQL queries. Return only the SQL query without any markdown formatting or explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Clean up the query (remove markdown code blocks if present)
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        # Sanitize SQL query to fix common issues
        sql_query = self._sanitize_sql(sql_query)
        
        logger.info(f"Generated SQL: {sql_query}")
        return sql_query
    
    def _sanitize_sql(self, sql_query: str) -> str:
        """
        Sanitize SQL query to fix common issues.
        
        Args:
            sql_query: Original SQL query
            
        Returns:
            Sanitized SQL query
        """
        import re
        
        # Check if we need to use quoted column names (spaces in original data)
        # Look at the actual schema to determine the format
        if self.schema_info and 'columns' in self.schema_info:
            columns = self.schema_info['columns']
            
            # If columns have spaces, we need to quote them in SQL
            has_spaces = any(' ' in col for col in columns)
            
            if has_spaces:
                # Replace underscored versions with quoted space versions
                patterns = [
                    (r'\bTotal_Spent\b', '"Total Spent"'),
                    (r'\bSite_Visit\b', '"Site Visit"'),
                    (r'\bAd_Type\b', '"Ad Type"'),
                    (r'\bDevice_Type\b', '"Device Type"'),
                    (r'\bCampaign_Name\b', '"Campaign_Name"'),  # This one might have underscore
                ]
            else:
                # Replace space versions with underscored versions
                patterns = [
                    (r'\bAd Type\b', 'Ad_Type'),
                    (r'\bDevice Type\b', 'Device_Type'),
                    (r'\bTotal Spent\b', 'Total_Spent'),
                    (r'\bSite Visit\b', 'Site_Visit'),
                ]
            
            for pattern, replacement in patterns:
                sql_query = re.sub(pattern, replacement, sql_query, flags=re.IGNORECASE)
        
        return sql_query
    
    def execute_query(self, sql_query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results.
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            DataFrame with query results
        """
        try:
            result = self.conn.execute(sql_query).fetchdf()
            logger.info(f"Query executed successfully, returned {len(result)} rows")
            return result
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask a natural language question and get results.
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with SQL query, results, and metadata
        """
        import time
        
        try:
            start_time = time.time()
            
            # Generate SQL
            sql_query = self.generate_sql(question)
            
            # Execute query
            results = self.execute_query(sql_query)
            
            # Generate natural language answer
            answer = self._generate_answer(question, results)
            
            execution_time = time.time() - start_time
            
            return {
                "question": question,
                "sql_query": sql_query,
                "results": results,
                "answer": answer,
                "execution_time": execution_time,
                "success": True,
                "error": None
            }
        
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return {
                "question": question,
                "sql_query": None,
                "results": None,
                "answer": None,
                "success": False,
                "error": str(e)
            }
    
    def _get_schema_description(self) -> str:
        """Generate a description of the database schema."""
        if not self.schema_info:
            return "No schema information available"
        
        desc = f"Table: {self.schema_info['table_name']}\n\n"
        desc += "Columns:\n"
        
        for col in self.schema_info['columns']:
            dtype = str(self.schema_info['dtypes'][col])
            desc += f"  - {col} ({dtype})\n"
        
        desc += "\nSample Data (first 3 rows):\n"
        for i, row in enumerate(self.schema_info['sample_data'], 1):
            desc += f"  Row {i}: {row}\n"
        
        return desc
    
    def _generate_answer(self, question: str, results: pd.DataFrame) -> str:
        """
        Generate strategic insights and recommendations from query results.
        
        Args:
            question: Original question
            results: Query results
            
        Returns:
            Strategic analysis with insights and recommendations
        """
        if results.empty:
            return "No results found for your question."
        
        # Convert results to text summary
        results_text = results.to_string(index=False, max_rows=20)
        
        # Determine if this is an insight or recommendation question
        is_insight_question = any(keyword in question.lower() for keyword in [
            'why', 'what explains', 'root cause', 'underlying', 'story', 'pattern', 
            'hidden', 'surprising', 'counterintuitive', 'narrative', 'drivers'
        ])
        
        is_recommendation_question = any(keyword in question.lower() for keyword in [
            'recommend', 'should we', 'how should', 'what should', 'suggest', 
            'optimize', 'improve', 'action plan', 'strategy', 'roadmap'
        ])
        
        if is_recommendation_question:
            system_prompt = """You are a strategic marketing analyst providing actionable recommendations.

For RECOMMENDATIONS, you MUST:
✓ Be specific and actionable (not vague suggestions)
✓ Quantify expected impact where possible
✓ Consider implementation difficulty and timeline
✓ Assess risks and trade-offs
✓ Prioritize by potential business impact
✓ Provide clear success metrics

Format your recommendation as:
**Recommendation:** [Clear, specific action]
**Rationale:** [Data-driven evidence]
**Expected Impact:** [Quantified outcomes, e.g., "15-20% CPA reduction"]
**Implementation:** [How to execute, timeline]
**Risks:** [What could go wrong]
**Success Metrics:** [How to measure]
**Priority:** [High/Medium/Low]"""
            
            user_prompt = f"""Based on the data below, provide a strategic recommendation.

Question: {question}

Data:
{results_text}

Provide a structured, actionable recommendation:"""
            max_tokens = 500
            
        elif is_insight_question:
            system_prompt = """You are a strategic marketing analyst uncovering deep insights.

For INSIGHTS, you MUST:
✓ Go beyond surface-level observations
✓ Connect multiple data points into coherent narratives
✓ Identify "so what" implications for business
✓ Distinguish correlation from causation
✓ Provide confidence levels for conclusions
✓ Explain the "why" behind patterns
✓ Compare against benchmarks when relevant

Provide insights that tell a story and reveal the underlying drivers of performance."""
            
            user_prompt = f"""Based on the data below, provide strategic insights that explain the underlying story.

Question: {question}

Data:
{results_text}

Provide deep insights with context and business implications:"""
            max_tokens = 400
            
        else:
            # Standard analytical answer
            system_prompt = "You are a data analyst providing clear, insightful answers with business context."
            user_prompt = f"""Based on the following query results, provide a clear answer with context.

Question: {question}

Query Results:
{results_text}

Provide an informative answer with key takeaways:"""
            max_tokens = 300
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content.strip()
    
    def get_suggested_questions(self) -> List[str]:
        """Get suggested questions based on the data schema."""
        return [
            # Temporal Comparisons
            "Compare campaign performance between the last 2 weeks vs. the previous 2 weeks",
            "Show me the week-over-week trend for conversions over the last 2 months",
            "How did our CTR in the last month compare to the month before?",
            "What's the month-over-month growth in leads for the past 6 months?",
            "Compare Q3 2024 vs Q2 2024 performance for ROAS and CPA",
            
            # Channel & Performance Analysis
            "Which marketing channel generated the highest ROI?",
            "Compare the cost per acquisition (CPA) across different channels",
            "Which platform performs best in terms of ROAS? Calculate from total revenue and spend",
            "Show me the top 5 campaigns by conversions with their ROAS",
            
            # Funnel & Conversion Analysis
            "What was the conversion rate at each stage: impressions to clicks to conversions?",
            "Calculate the click-through rate and conversion rate for each platform",
            "Where did we see the highest drop-off in the funnel?",
            
            # Budget & ROI Analysis
            "Calculate the return on ad spend (ROAS) for each campaign",
            "What is the total spend vs total revenue across all campaigns?",
            "Which channel should we invest more in based on ROAS performance?",
            
            # Creative & Timing
            "What were the best performing days for campaign engagement?",
            "Show me performance trends by day of week",
            
            # Comparative Analysis
            "Compare new vs returning customer conversion metrics",
            "How did different audience segments perform in terms of engagement rate?"
        ]
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


class QueryTemplates:
    """Pre-built query templates for common questions."""
    
    @staticmethod
    def get_templates() -> Dict[str, str]:
        """Get dictionary of query templates."""
        return {
            "top_campaigns_by_roas": """
                SELECT Campaign_Name, Platform, ROAS, Spend, Conversions
                FROM campaigns
                ORDER BY ROAS DESC
                LIMIT 10
            """,
            
            "total_spend_by_platform": """
                SELECT Platform, 
                       SUM(Spend) as Total_Spend,
                       SUM(Conversions) as Total_Conversions,
                       ROUND(SUM(Revenue) / NULLIF(SUM(Spend), 0), 2) as ROAS,
                       ROUND(SUM(Spend) / NULLIF(SUM(Conversions), 0), 2) as CPA
                FROM campaigns
                GROUP BY Platform
                ORDER BY Total_Spend DESC
            """,
            
            "campaign_performance_summary": """
                SELECT Campaign_Name,
                       COUNT(DISTINCT Platform) as Platforms,
                       SUM(Spend) as Total_Spend,
                       SUM(Conversions) as Total_Conversions,
                       ROUND(SUM(Revenue) / NULLIF(SUM(Spend), 0), 2) as ROAS,
                       ROUND(SUM(Spend) / NULLIF(SUM(Conversions), 0), 2) as CPA,
                       ROUND((SUM(Clicks) / NULLIF(SUM(Impressions), 0)) * 100, 2) as CTR
                FROM campaigns
                GROUP BY Campaign_Name
                ORDER BY Total_Spend DESC
            """,
            
            "monthly_trends": """
                SELECT DATE_TRUNC('month', CAST(Date AS DATE)) as Month,
                       SUM(Spend) as Total_Spend,
                       SUM(Conversions) as Total_Conversions,
                       ROUND(SUM(Revenue) / NULLIF(SUM(Spend), 0), 2) as ROAS,
                       ROUND(SUM(Spend) / NULLIF(SUM(Conversions), 0), 2) as CPA
                FROM campaigns
                GROUP BY Month
                ORDER BY Month
            """,
            
            "platform_comparison": """
                SELECT Platform,
                       COUNT(*) as Campaign_Count,
                       SUM(Impressions) as Total_Impressions,
                       SUM(Clicks) as Total_Clicks,
                       ROUND((SUM(Clicks) / NULLIF(SUM(Impressions), 0)) * 100, 2) as CTR,
                       ROUND(SUM(Spend) / NULLIF(SUM(Clicks), 0), 2) as CPC,
                       ROUND((SUM(Spend) / NULLIF(SUM(Impressions), 0)) * 1000, 2) as CPM,
                       SUM(Conversions) as Total_Conversions,
                       SUM(Spend) as Total_Spend,
                       ROUND(SUM(Spend) / NULLIF(SUM(Conversions), 0), 2) as CPA,
                       ROUND(SUM(Revenue) / NULLIF(SUM(Spend), 0), 2) as ROAS
                FROM campaigns
                GROUP BY Platform
                ORDER BY Total_Spend DESC
            """,
            
            "best_worst_performers": """
                (SELECT 'Top 5' as Category, Campaign_Name, Platform, ROAS, Spend
                 FROM campaigns
                 ORDER BY ROAS DESC
                 LIMIT 5)
                UNION ALL
                (SELECT 'Bottom 5' as Category, Campaign_Name, Platform, ROAS, Spend
                 FROM campaigns
                 ORDER BY ROAS ASC
                 LIMIT 5)
            """,
            
            "efficiency_analysis": """
                SELECT Campaign_Name,
                       Platform,
                       Spend,
                       Conversions,
                       CPA,
                       ROAS,
                       CASE 
                           WHEN ROAS >= 4.0 THEN 'Excellent'
                           WHEN ROAS >= 3.0 THEN 'Good'
                           WHEN ROAS >= 2.0 THEN 'Average'
                           ELSE 'Needs Improvement'
                       END as Performance_Category
                FROM campaigns
                ORDER BY ROAS DESC
            """
        }
