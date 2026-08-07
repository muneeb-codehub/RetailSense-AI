import pandas as pd
from sqlalchemy import create_engine
import os

DB_URL = "postgresql://postgres:admin123@localhost:5432/retailsense"
engine = create_engine(DB_URL)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

files = {
    "train":        "train.csv",
    "stores":       "stores.csv",
    "oil":          "oil.csv",
    "holidays":     "holidays_events.csv",
    "transactions": "transactions.csv",
}

print("🚀 Loading data into PostgreSQL...\n")

for table, filename in files.items():
    path = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        continue
    
    print(f"📂 Loading {filename}...")
    df = pd.read_csv(path)
    
    # Date columns fix
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    df.to_sql(table, engine, if_exists="replace", index=False)
    print(f"✅ {table}: {len(df):,} rows loaded\n")

print("🎉 All data loaded successfully!")