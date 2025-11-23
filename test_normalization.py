"""Test script to verify column normalization works correctly."""
import pandas as pd
from src.utils.data_loader import normalize_campaign_dataframe

# Load the sample data
csv_path = r"C:\Users\asharm08\OneDrive - dentsu\Desktop\sample_data.csv"
df = pd.read_csv(csv_path)

print("=" * 80)
print("ORIGINAL COLUMNS:")
print("=" * 80)
for i, col in enumerate(df.columns, 1):
    print(f"{i}. {col}")

print("\n" + "=" * 80)
print("SAMPLE DATA (first 3 rows):")
print("=" * 80)
print(df.head(3))

# Normalize
df_normalized = normalize_campaign_dataframe(df)

print("\n" + "=" * 80)
print("NORMALIZED COLUMNS:")
print("=" * 80)
for i, col in enumerate(df_normalized.columns, 1):
    print(f"{i}. {col}")

print("\n" + "=" * 80)
print("COLUMN MAPPING:")
print("=" * 80)
for orig, norm in zip(df.columns, df_normalized.columns):
    if orig != norm:
        print(f"✓ '{orig}' → '{norm}'")
    else:
        print(f"  '{orig}' (unchanged)")

print("\n" + "=" * 80)
print("NORMALIZED DATA (first 3 rows):")
print("=" * 80)
print(df_normalized.head(3))

print("\n" + "=" * 80)
print("KEY METRICS:")
print("=" * 80)
print(f"Campaigns: {df_normalized['Campaign_Name'].nunique() if 'Campaign_Name' in df_normalized.columns else 'NOT FOUND'}")
print(f"Platforms: {df_normalized['Platform'].nunique() if 'Platform' in df_normalized.columns else 'NOT FOUND'}")
print(f"Total Spend: ${df_normalized['Spend'].sum():,.2f}" if 'Spend' in df_normalized.columns else "Spend NOT FOUND")
print(f"Total Conversions: {df_normalized['Conversions'].sum():,.0f}" if 'Conversions' in df_normalized.columns else "Conversions NOT FOUND")
print(f"Total Revenue: ${df_normalized['Revenue'].sum():,.2f}" if 'Revenue' in df_normalized.columns else "Revenue NOT FOUND")

print("\n" + "=" * 80)
print("DATA TYPES:")
print("=" * 80)
print(df_normalized.dtypes)
