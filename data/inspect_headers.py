import os
import pandas as pd

data_dir = os.path.dirname(__file__)

for filename in os.listdir(data_dir):
    filepath = os.path.join(data_dir, filename)
    if os.path.isdir(filepath):
        continue
    if not filename.lower().endswith((".csv", ".xlsx", ".xls")):
        continue
    
    print(f"\n{'='*60}")
    print(f"FILE: {filename}")
    print('='*60)
    
    try:
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(filepath, nrows=2)
        else:
            df = pd.read_excel(filepath, nrows=2)
        
        print(f"Columns ({len(df.columns)}): {list(df.columns)}")
        print(f"\nFirst row sample:")
        print(df.iloc[0].to_dict() if len(df) > 0 else "No data rows")
    except Exception as e:
        print(f"Error reading file: {e}")