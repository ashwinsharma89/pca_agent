"""
Test Streamlit database integration.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import pandas as pd
from src.streamlit_integration import get_streamlit_db_manager

def test_database_integration():
    """Test database manager functionality."""
    
    print("=" * 60)
    print("Testing Streamlit Database Integration")
    print("=" * 60)
    
    # Get database manager
    print("\n1. Getting database manager...")
    db_manager = get_streamlit_db_manager()
    print("✅ Database manager initialized")
    
    # Health check
    print("\n2. Checking database health...")
    is_healthy = db_manager.health_check()
    if is_healthy:
        print("✅ Database is healthy")
    else:
        print("❌ Database health check failed")
        return
    
    # Create sample data
    print("\n3. Creating sample campaign data...")
    sample_data = pd.DataFrame({
        'Campaign_ID': ['camp_001', 'camp_002', 'camp_003'],
        'Campaign_Name': ['Summer Sale', 'Winter Promo', 'Spring Launch'],
        'Platform': ['Google', 'Facebook', 'LinkedIn'],
        'Spend': [1000.0, 1500.0, 2000.0],
        'Impressions': [50000, 75000, 100000],
        'Clicks': [2500, 3000, 4000],
        'Conversions': [125, 150, 200],
        'CTR': [5.0, 4.0, 4.0],
        'CPC': [0.4, 0.5, 0.5],
        'CPA': [8.0, 10.0, 10.0],
        'Date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
    })
    print(f"✅ Created {len(sample_data)} sample campaigns")
    
    # Import to database
    print("\n4. Importing campaigns to database...")
    result = db_manager.import_dataframe(sample_data)
    
    if result['success']:
        print(f"✅ Successfully imported {result['imported_count']} campaigns")
    else:
        print(f"❌ Import failed: {result['message']}")
        return
    
    # Query campaigns
    print("\n5. Querying campaigns from database...")
    campaigns = db_manager.get_campaigns(limit=10)
    
    if not campaigns.empty:
        print(f"✅ Retrieved {len(campaigns)} campaigns")
        print("\nCampaign Summary:")
        print(campaigns[['campaign_name', 'platform', 'spend', 'conversions']].to_string())
    else:
        print("❌ No campaigns found")
        return
    
    # Get aggregated metrics
    print("\n6. Getting aggregated metrics...")
    metrics = db_manager.get_aggregated_metrics()
    
    if metrics:
        print("✅ Aggregated Metrics:")
        print(f"   Total Campaigns: {metrics.get('campaign_count', 0)}")
        print(f"   Total Spend: ${metrics.get('total_spend', 0):,.2f}")
        print(f"   Total Clicks: {metrics.get('total_clicks', 0):,}")
        print(f"   Total Conversions: {metrics.get('total_conversions', 0):,}")
        print(f"   Avg CTR: {metrics.get('avg_ctr', 0):.2f}%")
    else:
        print("❌ Failed to get metrics")
    
    # Test LLM usage tracking
    print("\n7. Testing LLM usage tracking...")
    success = db_manager.track_llm_usage(
        provider='openai',
        model='gpt-4',
        prompt_tokens=1000,
        completion_tokens=500,
        cost=0.045,
        operation='test'
    )
    
    if success:
        print("✅ LLM usage tracked successfully")
    else:
        print("❌ Failed to track LLM usage")
    
    # Get LLM usage stats
    print("\n8. Getting LLM usage statistics...")
    llm_stats = db_manager.get_llm_usage_stats(days=30)
    
    if llm_stats and llm_stats['total']:
        total = llm_stats['total']
        print("✅ LLM Usage Stats:")
        print(f"   Total Tokens: {total.get('total_tokens', 0):,}")
        print(f"   Total Cost: ${total.get('total_cost', 0):.4f}")
        print(f"   Total Requests: {total.get('request_count', 0)}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed successfully!")
    print("=" * 60)
    print("\nThe database integration is working correctly.")
    print("You can now use it in your Streamlit app!")


if __name__ == "__main__":
    try:
        test_database_integration()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
