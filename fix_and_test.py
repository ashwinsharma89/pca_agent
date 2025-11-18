"""
Quick fix for column name issues and re-run tests
"""
import pandas as pd
import os

# Load the CSV
csv_path = r"C:\Users\asharm08\OneDrive - dentsu\Desktop\AI_Agent\Data\Sitevisit.csv"

print("Loading CSV...")
df = pd.read_csv(csv_path)

print(f"Original columns: {df.columns.tolist()[:10]}...")

# Fix column names: replace spaces with underscores
df.columns = df.columns.str.replace(' ', '_')

print(f"Fixed columns: {df.columns.tolist()[:10]}...")

# Save to PCA_Agent data folder
output_path = "data/sitevisit_fixed.csv"
os.makedirs('data', exist_ok=True)
df.to_csv(output_path, index=False)

print(f"✓ Saved fixed CSV to: {output_path}")
print(f"  Rows: {len(df)}")
print(f"  Columns: {len(df.columns)}")

# Now run the test with the fixed data
print("\n" + "="*80)
print("Running tests with fixed data...")
print("="*80 + "\n")

from test_real_data import main
import sys

# Temporarily override the data path
original_load = __import__('test_real_data').load_real_data

def load_fixed_data():
    return df, output_path

__import__('test_real_data').load_real_data = load_fixed_data

# Run tests
try:
    pass_rate = main()
    sys.exit(0 if pass_rate >= 80 else 1)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
