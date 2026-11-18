
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CLEAN_FILE = (
    BASE_DIR / "data" / "processed" / "startup_funding_cleaned.csv"
)
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "eda"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CLEAN_FILE, low_memory=False)

print("\n========== STARTUP FUNDING EDA ==========")
print("\nDataset shape:", df.shape)

# 1. Overall data information
print("\nColumn names:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

# 2. Numeric descriptive statistics
print("\nNumeric summary:")
print(df.select_dtypes(include="number").describe().T)

# 3. Funding KPIs
if "amount_in_usd" in df.columns:
    df["amount_in_usd"] = pd.to_numeric(
        df["amount_in_usd"],
        errors="coerce"
    )

    valid_amounts = df.loc[
        df["amount_in_usd"] > 0,
        "amount_in_usd"
    ].dropna()

    print("\n========== FUNDING KPIs ==========")
    print("Records with positive funding:", len(valid_amounts))

    if not valid_amounts.empty:
        print(f"Total recorded funding: {valid_amounts.sum():,.2f}")
        print(f"Average funding: {valid_amounts.mean():,.2f}")
        print(f"Median funding: {valid_amounts.median():,.2f}")
        print(f"Maximum funding: {valid_amounts.max():,.2f}")
        print(f"Minimum positive funding: {valid_amounts.min():,.2f}")

# 4. Industry analysis
if "industry_vertical" in df.columns:
    industry_summary = (
        df.groupby("industry_vertical", dropna=False)
        .agg(
            funding_records=("source_record_id", "count"),
            unique_startups=("startup_name", "nunique"),
            total_funding=("amount_in_usd", "sum"),
            median_funding=("amount_in_usd", "median")
        )
        .sort_values("funding_records", ascending=False)
        .reset_index()
    )

    industry_summary.to_csv(
        OUTPUT_DIR / "industry_summary.csv",
        index=False
    )

    print("\nTop 10 industries by number of records:")
    print(industry_summary.head(10).to_string(index=False))

# 5. City analysis
if "city_location" in df.columns:
    city_summary = (
        df.groupby("city_location", dropna=False)
        .agg(
            funding_records=("source_record_id", "count"),
            unique_startups=("startup_name", "nunique"),
            total_funding=("amount_in_usd", "sum"),
            median_funding=("amount_in_usd", "median")
        )
        .sort_values("funding_records", ascending=False)
        .reset_index()
    )

    city_summary.to_csv(
        OUTPUT_DIR / "city_summary.csv",
        index=False
    )

    print("\nTop 10 cities by number of records:")
    print(city_summary.head(10).to_string(index=False))

# 6. Investment type analysis
if "investment_type" in df.columns:
    investment_summary = (
        df.groupby("investment_type", dropna=False)
        .agg(
            funding_records=("source_record_id", "count"),
            total_funding=("amount_in_usd", "sum"),
            average_funding=("amount_in_usd", "mean"),
            median_funding=("amount_in_usd", "median")
        )
        .sort_values("funding_records", ascending=False)
        .reset_index()
    )

    investment_summary.to_csv(
        OUTPUT_DIR / "investment_type_summary.csv",
        index=False
    )

    print("\nInvestment type summary:")
    print(investment_summary.head(10).to_string(index=False))

# 7. Startup analysis
if "startup_name" in df.columns:
    startup_summary = (
        df.groupby("startup_name", dropna=False)
        .agg(
            funding_records=("source_record_id", "count"),
            total_funding=("amount_in_usd", "sum"),
            median_funding=("amount_in_usd", "median")
        )
        .sort_values("funding_records", ascending=False)
        .reset_index()
    )

    startup_summary.to_csv(
        OUTPUT_DIR / "startup_summary.csv",
        index=False
    )

    print("\nStartups with the most funding records:")
    print(startup_summary.head(10).to_string(index=False))

# 8. Yearly analysis
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = df["date"].dt.year

    yearly_summary = (
        df.dropna(subset=["year"])
        .groupby("year")
        .agg(
            funding_records=("source_record_id", "count"),
            unique_startups=("startup_name", "nunique"),
            total_funding=("amount_in_usd", "sum"),
            median_funding=("amount_in_usd", "median")
        )
        .reset_index()
        .sort_values("year")
    )

    yearly_summary.to_csv(
        OUTPUT_DIR / "annual_summary.csv",
        index=False
    )

    print("\nYearly funding summary:")
    print(yearly_summary.to_string(index=False))

# 9. Missing-value report
missing_report = pd.DataFrame({
    "Missing_Count": df.isna().sum(),
    "Missing_Percentage": (df.isna().mean() * 100).round(2)
})

missing_report.to_csv(
    OUTPUT_DIR / "eda_missing_values.csv"
)

print("\nEDA complete.")
print("Summary files saved in:", OUTPUT_DIR)
