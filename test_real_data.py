"""
Comprehensive Test Script for PCA Agent Q&A System
Tests with real data and validates all capabilities
"""
import pandas as pd
import os
from dotenv import load_dotenv
from src.query_engine import NaturalLanguageQueryEngine
from loguru import logger
import sys

# Load environment
load_dotenv()

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

def load_real_data():
    """Load real campaign data from multiple sources."""
    logger.info("Loading real campaign data...")
    
    # Try multiple data sources
    data_paths = [
        r"C:\Users\asharm08\OneDrive - dentsu\Desktop\AI_Agent\Data\Sitevisit.csv",
        r"data\sample_multi_campaign_database.csv",
        r"data\campaign_data.csv"
    ]
    
    for path in data_paths:
        if os.path.exists(path):
            logger.success(f"Found data at: {path}")
            df = pd.read_csv(path)
            logger.info(f"Loaded {len(df)} rows with {len(df.columns)} columns")
            logger.info(f"Columns: {', '.join(df.columns.tolist())}")
            return df, path
    
    logger.warning("No real data found. Creating sample data...")
    return create_sample_data(), "generated_sample"

def create_sample_data():
    """Create comprehensive sample data for testing."""
    import numpy as np
    from datetime import datetime, timedelta
    
    np.random.seed(42)
    
    # Generate 90 days of data
    dates = [datetime.now() - timedelta(days=x) for x in range(90, 0, -1)]
    
    campaigns = ['Q4_Holiday_2024', 'Black_Friday_2024', 'Cyber_Monday_2024', 
                 'Brand_Awareness_Q4', 'Retargeting_Q4']
    platforms = ['google_ads', 'meta_ads', 'linkedin_ads']
    devices = ['mobile', 'desktop', 'tablet']
    
    data = []
    for date in dates:
        for campaign in campaigns:
            for platform in platforms:
                # Simulate realistic metrics with trends
                day_factor = (90 - (datetime.now() - date).days) / 90  # Declining trend
                
                impressions = int(np.random.normal(50000, 10000) * day_factor)
                clicks = int(impressions * np.random.uniform(0.015, 0.035))
                conversions = int(clicks * np.random.uniform(0.02, 0.06))
                spend = np.random.uniform(3000, 8000) * day_factor
                revenue = spend * np.random.uniform(2.5, 5.5)
                
                data.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Campaign_Name': campaign,
                    'Platform': platform,
                    'Device_Type': np.random.choice(devices),
                    'Impressions': impressions,
                    'Clicks': clicks,
                    'CTR': (clicks / impressions * 100) if impressions > 0 else 0,
                    'Conversions': conversions,
                    'Spend': round(spend, 2),
                    'Revenue': round(revenue, 2),
                    'CPC': round(spend / clicks, 2) if clicks > 0 else 0,
                    'CPA': round(spend / conversions, 2) if conversions > 0 else 0,
                    'ROAS': round(revenue / spend, 2) if spend > 0 else 0,
                })
    
    df = pd.DataFrame(data)
    logger.success(f"Created sample data: {len(df)} rows")
    return df

def test_basic_queries(engine):
    """Test basic analytical queries."""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: BASIC QUERIES")
    logger.info("="*80)
    
    questions = [
        "What is the total spend across all campaigns?",
        "Which campaign had the highest ROAS?",
        "Show me the top 5 campaigns by conversions",
    ]
    
    results = []
    for i, q in enumerate(questions, 1):
        logger.info(f"\n[{i}] Question: {q}")
        result = engine.ask(q)
        
        if result['success']:
            logger.success(f"✓ Answer: {result['answer'][:200]}...")
            logger.info(f"  Rows returned: {len(result['results'])}")
            results.append(('PASS', q))
        else:
            logger.error(f"✗ Error: {result['error']}")
            results.append(('FAIL', q))
    
    return results

def test_temporal_comparisons(engine):
    """Test temporal comparison queries."""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: TEMPORAL COMPARISONS")
    logger.info("="*80)
    
    questions = [
        "Compare campaign performance between the last 2 weeks vs. the previous 2 weeks",
        "Show me the week-over-week trend for conversions over the last 2 months",
        "How did our CTR in the last month compare to the month before?",
    ]
    
    results = []
    for i, q in enumerate(questions, 1):
        logger.info(f"\n[{i}] Question: {q}")
        result = engine.ask(q)
        
        if result['success']:
            logger.success(f"✓ SQL Generated")
            logger.info(f"  SQL: {result['sql_query'][:150]}...")
            
            # Validate aggregation (should not have AVG for rate metrics)
            sql_lower = result['sql_query'].lower()
            if 'avg(ctr)' in sql_lower or 'avg(roas)' in sql_lower or 'avg(cpc)' in sql_lower:
                logger.warning("⚠ WARNING: Found AVG on rate metric (should use SUM aggregates)")
                results.append(('WARN', q))
            else:
                logger.success("✓ Correct aggregation (no AVG on rate metrics)")
                results.append(('PASS', q))
        else:
            logger.error(f"✗ Error: {result['error']}")
            results.append(('FAIL', q))
    
    return results

def test_strategic_analysis(engine):
    """Test strategic analysis queries."""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: STRATEGIC ANALYSIS")
    logger.info("="*80)
    
    questions = [
        "Identify performance anomalies in the last 2 months using statistical outliers",
        "Identify top 20% of campaigns driving 80% of results (Pareto analysis)",
        "Calculate performance volatility (CPA standard deviation) for each campaign",
    ]
    
    results = []
    for i, q in enumerate(questions, 1):
        logger.info(f"\n[{i}] Question: {q}")
        result = engine.ask(q)
        
        if result['success']:
            logger.success(f"✓ Answer generated")
            logger.info(f"  Answer: {result['answer'][:200]}...")
            
            # Check for advanced SQL patterns
            sql_lower = result['sql_query'].lower()
            if 'stddev' in sql_lower or 'percentile' in sql_lower or 'percent_rank' in sql_lower:
                logger.success("✓ Uses advanced statistical functions")
            
            results.append(('PASS', q))
        else:
            logger.error(f"✗ Error: {result['error']}")
            results.append(('FAIL', q))
    
    return results

def test_insights_and_recommendations(engine):
    """Test insight and recommendation generation."""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: INSIGHTS & RECOMMENDATIONS")
    logger.info("="*80)
    
    questions = [
        ("INSIGHT", "What's the underlying story behind our campaign performance in the last 2 months?"),
        ("RECOMMENDATION", "How should we reallocate our budget next month to maximize conversions?"),
    ]
    
    results = []
    for q_type, q in questions:
        logger.info(f"\n[{q_type}] Question: {q}")
        result = engine.ask(q)
        
        if result['success']:
            answer = result['answer']
            logger.success(f"✓ {q_type} generated")
            logger.info(f"  Length: {len(answer)} characters")
            
            # Validate structure
            if q_type == "RECOMMENDATION":
                required_sections = ['Recommendation:', 'Rationale:', 'Expected Impact:', 'Implementation:']
                found_sections = sum(1 for section in required_sections if section in answer)
                
                if found_sections >= 3:
                    logger.success(f"✓ Structured recommendation ({found_sections}/4 sections)")
                    results.append(('PASS', q))
                else:
                    logger.warning(f"⚠ Missing sections ({found_sections}/4)")
                    results.append(('WARN', q))
            else:
                # For insights, check for depth
                if len(answer) > 200:
                    logger.success("✓ Detailed insight (>200 chars)")
                    results.append(('PASS', q))
                else:
                    logger.warning("⚠ Insight seems brief")
                    results.append(('WARN', q))
        else:
            logger.error(f"✗ Error: {result['error']}")
            results.append(('FAIL', q))
    
    return results

def print_summary(all_results):
    """Print test summary."""
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    
    total = len(all_results)
    passed = sum(1 for status, _ in all_results if status == 'PASS')
    warned = sum(1 for status, _ in all_results if status == 'WARN')
    failed = sum(1 for status, _ in all_results if status == 'FAIL')
    
    logger.info(f"\nTotal Tests: {total}")
    logger.success(f"✓ Passed: {passed}")
    if warned > 0:
        logger.warning(f"⚠ Warnings: {warned}")
    if failed > 0:
        logger.error(f"✗ Failed: {failed}")
    
    pass_rate = (passed / total * 100) if total > 0 else 0
    logger.info(f"\nPass Rate: {pass_rate:.1f}%")
    
    if pass_rate >= 80:
        logger.success("\n🎉 SYSTEM READY FOR PRODUCTION!")
    elif pass_rate >= 60:
        logger.warning("\n⚠️ SYSTEM NEEDS SOME FIXES")
    else:
        logger.error("\n❌ SYSTEM NEEDS MAJOR WORK")
    
    return pass_rate

def main():
    """Run all tests."""
    logger.info("="*80)
    logger.info("PCA AGENT Q&A SYSTEM - COMPREHENSIVE TEST")
    logger.info("="*80)
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        logger.error("\n❌ ERROR: OpenAI API key not found!")
        logger.info("Please set OPENAI_API_KEY in .env file")
        return
    
    # Load data
    df, source = load_real_data()
    logger.info(f"\nData source: {source}")
    logger.info(f"Date range: {df['Date'].min()} to {df['Date'].max()}" if 'Date' in df.columns else "No date column")
    
    # Initialize engine
    logger.info("\n🤖 Initializing Q&A Engine...")
    engine = NaturalLanguageQueryEngine(api_key)
    engine.load_data(df)
    logger.success("✓ Engine ready!")
    
    # Run all tests
    all_results = []
    
    all_results.extend(test_basic_queries(engine))
    all_results.extend(test_temporal_comparisons(engine))
    all_results.extend(test_strategic_analysis(engine))
    all_results.extend(test_insights_and_recommendations(engine))
    
    # Print summary
    pass_rate = print_summary(all_results)
    
    # Save results
    results_df = pd.DataFrame(all_results, columns=['Status', 'Question'])
    results_df.to_csv('test_results.csv', index=False)
    logger.info(f"\n💾 Results saved to: test_results.csv")
    
    return pass_rate

if __name__ == "__main__":
    try:
        pass_rate = main()
        sys.exit(0 if pass_rate >= 80 else 1)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
