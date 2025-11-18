"""
Test automated analysis with the fix
"""
import pandas as pd
import os
from dotenv import load_dotenv
from src.analytics import MediaAnalyticsExpert
from loguru import logger
import sys

# Load environment
load_dotenv()

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

def main():
    print("="*80)
    print("🧪 TESTING: Automated Analysis (Fixed)")
    print("="*80 + "\n")
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("❌ OpenAI API key not found!")
        return
    
    # Load data
    logger.info("Loading data...")
    data_path = r"C:\Users\asharm08\OneDrive - dentsu\Desktop\AI_Agent\Data\Sitevisit.csv"
    
    if not os.path.exists(data_path):
        logger.error(f"❌ Data file not found: {data_path}")
        return
    
    df = pd.read_csv(data_path)
    logger.success(f"✓ Loaded {len(df)} rows")
    
    # Initialize analytics expert
    logger.info("🤖 Initializing Analytics Expert...")
    try:
        expert = MediaAnalyticsExpert(api_key=api_key)
        logger.success("✓ Expert initialized!\n")
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {e}")
        return
    
    # Run automated analysis
    logger.info("🔍 Running automated analysis...")
    logger.info("This may take 30-60 seconds...\n")
    
    try:
        analysis = expert.analyze_all(df)
        
        logger.success("✅ ANALYSIS COMPLETE!\n")
        
        print("="*80)
        print("📊 ANALYSIS RESULTS")
        print("="*80)
        
        # Executive Summary
        if 'executive_summary' in analysis:
            print("\n📝 Executive Summary:")
            print(analysis['executive_summary'])
        
        # Metrics
        if 'metrics' in analysis and 'overall_kpis' in analysis['metrics']:
            print("\n📈 Overall KPIs:")
            kpis = analysis['metrics']['overall_kpis']
            for key, value in kpis.items():
                print(f"  - {key}: {value}")
        
        # Insights count
        if 'insights' in analysis:
            print(f"\n💡 Insights Generated: {len(analysis['insights'])}")
        
        # Recommendations count
        if 'recommendations' in analysis:
            print(f"🎯 Recommendations Generated: {len(analysis['recommendations'])}")
        
        print("\n" + "="*80)
        logger.success("✅ Test passed! Automated analysis works!")
        print("="*80)
        
    except Exception as e:
        logger.error(f"❌ ANALYSIS FAILED: {e}")
        import traceback
        print("\nFull error:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
