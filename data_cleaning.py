
from pathlib import Path
import re
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "raw" / "startup_funding.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def standardize_column_name(name):
    """Convert column names to lowercase snake_case."""
    name = str(name).strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def convert_amount(value):
    """Convert common funding amount strings into numbers."""
    if pd.isna(value):
        return np.nan

    text = str(value).strip()

    if text.lower() in {"", "nan", "none", "null", "n/a", "na", "-"}:
        return np.nan

    text = text.replace(",", "")
    text = text.replace("$", "").replace("₹", "").replace("€", "")
    text = re.sub(
        r"(?i)\b(usd|inr|rs\.?|rupees?)\b",
        "",
        text
    ).strip()

    # Support suffixes such as 5K, 2.5M, and 1B.
    match = re.fullmatch(
        r"(-?\d+(?:\.\d+)?)\s*([KMB])?",
        text,
        flags=re.IGNORECASE
    )

    if match:
        number = float(match.group(1))
        suffix = (match.group(2) or "").upper()
        multiplier = {
            "K": 1_000,
            "M": 1_000_000,
            "B": 1_000_000_000
        }.get(suffix, 1)

        return number * multiplier

    # Unknown formats stay missing instead of guessing.
    return np.nan


# Load original dataset
df = pd.read_csv(DATA_FILE)

print("Original dataset shape:", df.shape)

# 1. Standardize column names
df.columns = [standardize_column_name(c) for c in df.columns]

# 2. Rename common column variations
rename_map = {
    "startup": "startup_name",
    "name": "startup_name",
    "vertical": "industry_vertical",
    "industry": "industry_vertical",
    "city": "city_location",
    "location": "city_location",
    "investors": "investors_name",
    "investor_name": "investors_name",
    "investment": "investment_type",
    "investmentntype": "investment_type",
    "amount": "amount_in_usd",
    "funding_amount": "amount_in_usd"
}

df.rename(
    columns={
        column: rename_map[column]
        for column in df.columns
        if column in rename_map
    },
    inplace=True
)

# Keep a source row ID so records can be traced.
df.insert(0, "source_record_id", range(1, len(df) + 1))

# 3. Clean whitespace and empty text
for column in df.select_dtypes(include=["object", "string"]).columns:
    df[column] = df[column].astype("string").str.strip()
    df[column] = df[column].replace(
        {"": pd.NA, "nan": pd.NA, "None": pd.NA, "null": pd.NA}
    )

# 4. Clean date column
if "date" in df.columns:
    df["date_raw"] = df["date"]

    date_text = (
        df["date"]
        .astype("string")
        .str.strip()
        .str.replace(r"[./]", "-", regex=True)
    )

    df["date"] = pd.to_datetime(
        date_text,
        errors="coerce",
        dayfirst=True,
        format="mixed"
    )

    df["year"] = df["date"].dt.year.astype("Int64")
    df["month_number"] = df["date"].dt.month.astype("Int64")
    df["month_name"] = df["date"].dt.month_name()
    df["quarter"] = (
        df["date"].dt.to_period("Q").astype("string")
        .replace("<NA>", pd.NA)
    )

# 5. Clean funding amount
if "amount_in_usd" in df.columns:
    df["amount_raw"] = df["amount_in_usd"]
    df["amount_in_usd"] = df["amount_in_usd"].map(convert_amount)

# 6. Standardize selected text fields
if "startup_name" in df.columns:
    df["startup_name"] = df["startup_name"].str.strip()

if "city_location" in df.columns:
    df["city_location"] = df["city_location"].replace({
        "Bengaluru": "Bangalore",
        "bangalore": "Bangalore",
        "Delhi NCR": "New Delhi",
        "Gurgaon": "Gurugram"
    })

if "industry_vertical" in df.columns:
    df["industry_vertical"] = (
        df["industry_vertical"].astype("string").str.strip().str.title()
    )

if "investment_type" in df.columns:
    df["investment_type"] = (
        df["investment_type"].astype("string").str.strip().str.title()
    )

# 7. Flag possible duplicates without deleting them
check_columns = [
    column for column in df.columns
    if column not in ["source_record_id", "possible_duplicate"]
]

df["possible_duplicate"] = df.duplicated(
    subset=check_columns,
    keep=False
)

# 8. Save missing-values report
missing_report = pd.DataFrame({
    "Missing_Count": df.isna().sum(),
    "Missing_Percentage": (df.isna().mean() * 100).round(2)
})

missing_report.to_csv(
    OUTPUT_DIR / "cleaned_missing_values_report.csv"
)

# 9. Save cleaned dataset and duplicate review
df.to_csv(
    OUTPUT_DIR / "startup_funding_cleaned.csv",
    index=False
)

df[df["possible_duplicate"]].to_csv(
    OUTPUT_DIR / "possible_duplicate_records.csv",
    index=False
)

# 10. Display cleaning summary
print("\n========== DATA CLEANING SUMMARY ==========")
print("Rows retained:", len(df))
print("Columns after cleaning:", len(df.columns))
print("Possible duplicate rows flagged:", int(df["possible_duplicate"].sum()))

if "date" in df.columns:
    print("Missing or invalid dates:", int(df["date"].isna().sum()))

if "amount_in_usd" in df.columns:
    print(
        "Missing or unparsed amounts:",
        int(df["amount_in_usd"].isna().sum())
    )

print("\nCleaned data saved to:")
print(OUTPUT_DIR / "startup_funding_cleaned.csv")
print("Cleaning complete.")
