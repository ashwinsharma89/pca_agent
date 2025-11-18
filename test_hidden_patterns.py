"""
Quick test for the "hidden patterns" question
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

def main():
    print("="*80)
    print("🧪 TESTING: Hidden Patterns Question")
    print("="*80 + "\n")
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("❌ OpenAI API key not found!")
        return
    
    # Load data
    logger.info("Loading data...")
    data_path = "data/sitevisit_fixed.csv"
    
    if not os.path.exists(data_path):
        logger.error(f"❌ Data file not found: {data_path}")
        logger.info("Run fix_and_test.py first to create the fixed data file")
        return
    
    df = pd.read_csv(data_path)
    logger.success(f"✓ Loaded {len(df)} rows")
    
    # Initialize engine
    logger.info("🤖 Initializing Q&A Engine...")
    engine = NaturalLanguageQueryEngine(api_key)
    engine.load_data(df)
    logger.success("✓ Engine ready!\n")
    
    # Test the problematic question
    question = "What hidden patterns exist in our top-performing campaigns?"
    
    logger.info(f"Question: {question}\n")
    
    try:
        result = engine.ask(question)
        
        if result['success']:
            logger.success("✅ SUCCESS! Query executed without errors\n")
            
            print("="*80)
            print("📝 ANSWER")
            print("="*80)
            print(result['answer'])
            print()
            
            print("="*80)
            print("🔧 GENERATED SQL")
            print("="*80)
            print(result['sql_query'])
            print()
            
            print("="*80)
            print(f"📊 RESULTS ({len(result['results'])} rows)")
            print("="*80)
            if len(result['results']) > 0:
                print(result['results'].head(10).to_string(index=False))
                if len(result['results']) > 10:
                    print(f"\n... and {len(result['results']) - 10} more rows")
            else:
                print("No results (may be due to date filtering)")
            print()
            
        else:
            logger.error(f"❌ FAILED: {result['error']}")
            
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
