
from pathlib import Path
import pandas as pd

# File locations
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "raw" / "startup_funding.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_FILE)

print("\n========== STARTUP FUNDING DATA UNDERSTANDING ==========")

# 1. Dataset dimensions
print("\n1. Dataset Shape")
print("Number of rows:", df.shape[0])
print("Number of columns:", df.shape[1])

# 2. Column names
print("\n2. Column Names")
print(df.columns.tolist())

# 3. First five records
print("\n3. First Five Records")
print(df.head())

# 4. Last five records
print("\n4. Last Five Records")
print(df.tail())

# 5. Data types and non-null counts
print("\n5. Dataset Information")
df.info()

# 6. Statistical summary
print("\n6. Statistical Summary")
print(df.describe(include="all").T)

# 7. Missing values
print("\n7. Missing Values")
missing = pd.DataFrame({
    "Missing_Count": df.isna().sum(),
    "Missing_Percentage": (df.isna().mean() * 100).round(2)
})
print(missing)

missing.to_csv(
    OUTPUT_DIR / "initial_missing_values.csv"
)

# 8. Duplicate rows
print("\n8. Exact Duplicate Rows")
print(df.duplicated().sum())

# 9. Unique values in each column
print("\n9. Unique Values Per Column")
print(df.nunique(dropna=True))

# 10. Save a basic profile
profile = pd.DataFrame({
    "Column": df.columns,
    "Data_Type": [str(dtype) for dtype in df.dtypes],
    "Non_Null_Count": df.notna().sum().values,
    "Missing_Count": df.isna().sum().values,
    "Unique_Values": df.nunique(dropna=True).values
})

profile.to_csv(
    OUTPUT_DIR / "dataset_profile.csv",
    index=False
)

print("\nAnalysis complete.")
print("Reports saved in:", OUTPUT_DIR)
