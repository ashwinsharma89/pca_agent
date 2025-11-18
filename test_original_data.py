"""
Test with original data (column names with spaces)
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
    print("🧪 TESTING: Original Data (with spaces in column names)")
    print("="*80 + "\n")
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("❌ OpenAI API key not found!")
        return
    
    # Load ORIGINAL data (with spaces)
    logger.info("Loading original data...")
    data_path = r"C:\Users\asharm08\OneDrive - dentsu\Desktop\AI_Agent\Data\Sitevisit.csv"
    
    if not os.path.exists(data_path):
        logger.error(f"❌ Data file not found: {data_path}")
        return
    
    df = pd.read_csv(data_path)
    logger.success(f"✓ Loaded {len(df)} rows")
    logger.info(f"✓ Columns (first 5): {df.columns.tolist()[:5]}")
    
    # Check for spaces in column names
    has_spaces = any(' ' in col for col in df.columns)
    logger.info(f"✓ Has spaces in column names: {has_spaces}")
    
    # Initialize engine
    logger.info("🤖 Initializing Q&A Engine...")
    engine = NaturalLanguageQueryEngine(api_key)
    engine.load_data(df)
    logger.success("✓ Engine ready!\n")
    
    # Test questions that were failing
    questions = [
        "Which campaigns have the highest ROAS?",
        "What is the total spend by channel?",
        "Show me top 5 campaigns by conversions"
    ]
    
    for i, question in enumerate(questions, 1):
        logger.info(f"\n[Question {i}] {question}")
        
        try:
            result = engine.ask(question)
            
            if result['success']:
                logger.success("✅ SUCCESS!")
                logger.info(f"  SQL: {result['sql_query'][:100]}...")
                logger.info(f"  Rows returned: {len(result['results'])}")
            else:
                logger.error(f"❌ FAILED: {result['error']}")
        
        except Exception as e:
            logger.error(f"❌ ERROR: {e}")
    
    logger.info("\n" + "="*80)
    logger.info("Test complete!")
    logger.info("="*80)

if __name__ == "__main__":
    main()
