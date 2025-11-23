"""
Quick test to debug SQL generation
"""
import pandas as pd
from src.query_engine.nl_to_sql import NaturalLanguageQueryEngine
import os
from dotenv import load_dotenv

load_dotenv()

# Create sample data matching your CSV
data = {
    'Campaign': ['Campaign A', 'Campaign B', 'Campaign C'],
    'Funnel': ['Awareness', 'Consideration', 'Conversion'],
    'Spend': [1000, 2000, 3000],
    'Clicks': [100, 200, 300],
    'Impressions': [10000, 20000, 30000],
    'Conversions': [10, 20, 30]
}
df = pd.DataFrame(data)

print("Sample data:")
print(df)
print("\nColumns:", df.columns.tolist())

# Initialize engine
api_key = os.getenv('OPENAI_API_KEY')
engine = NaturalLanguageQueryEngine(api_key)
engine.load_data(df)

# Test query
question = "sort by funnel performance"
print(f"\n{'='*60}")
print(f"Testing question: {question}")
print(f"{'='*60}\n")

try:
    result = engine.ask(question)
    print("\n✅ SUCCESS!")
    print(f"SQL: {result['sql_query']}")
    print(f"\nResults:\n{result['results']}")
    print(f"\nAnswer: {result['answer']}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
