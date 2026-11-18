
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent
CLEAN_FILE = (
    BASE_DIR / "data" / "processed" / "startup_funding_cleaned.csv"
)
OUTPUT_DIR = BASE_DIR / "visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


df = pd.read_csv(CLEAN_FILE, low_memory=False)

# Standardize column names
df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.lower()
    .str.replace(r"[^a-z0-9]+", "_", regex=True)
    .str.strip("_")
)

print("Loaded CSV columns:", df.columns.tolist())

print("Loaded file:", CLEAN_FILE)
print("Available columns:", df.columns.tolist())
print(df.head())

# Clean funding amount if the column exists
if "amount_in_usd" in df.columns:
    df["amount_in_usd"] = pd.to_numeric(
        df["amount_in_usd"],
        errors="coerce"
    )
else:
    raise ValueError(
        "Funding amount column not found. "
        f"Available columns: {df.columns.tolist()}"
    )

# Handle the date column safely
if "date" in df.columns:
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        dayfirst=True
    )
    df["year"] = df["date"].dt.year

elif "date" in df.columns.str.lower():
    # Normally handled by the column-name standardization above.
    pass

else:
    print(
        "WARNING: No date column found. "
        "Year-based visualizations cannot be created."
    )
    df["year"] = pd.NA



def save_chart(filename):
    """Save the current chart and close the figure."""
    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / filename,
        dpi=150,
        bbox_inches="tight"
    )
    plt.close()
    print("Chart saved:", filename)


# 1. Total funding by year
yearly = (
    df.dropna(subset=["year"])
    .groupby("year")["amount_in_usd"]
    .sum()
    .reset_index()
    .sort_values("year")
)

yearly = yearly[yearly["amount_in_usd"] > 0]

if not yearly.empty:
    plt.figure(figsize=(10, 5))
    sns.lineplot(
        data=yearly,
        x="year",
        y="amount_in_usd",
        marker="o"
    )
    plt.title("Total Recorded Startup Funding by Year")
    plt.xlabel("Year")
    plt.ylabel("Funding Amount")
    save_chart("01_funding_by_year.png")


# 2. Top 10 industries by number of records
if "industry_vertical" in df.columns:
    industry_counts = (
        df["industry_vertical"]
        .fillna("Unknown")
        .replace("", "Unknown")
        .value_counts()
        .head(10)
        .sort_values()
    )

    if not industry_counts.empty:
        plt.figure(figsize=(10, 6))
        industry_counts.plot(kind="barh")
        plt.title("Top 10 Industries by Funding Records")
        plt.xlabel("Number of Records")
        plt.ylabel("Industry")
        save_chart("02_top_industries.png")


# 3. Top 10 cities by number of records
if "city_location" in df.columns:
    city_counts = (
        df["city_location"]
        .fillna("Unknown")
        .replace("", "Unknown")
        .value_counts()
        .head(10)
        .sort_values()
    )

    if not city_counts.empty:
        plt.figure(figsize=(10, 6))
        city_counts.plot(kind="barh")
        plt.title("Top 10 Cities by Funding Records")
        plt.xlabel("Number of Records")
        plt.ylabel("City")
        save_chart("03_top_cities.png")


# 4. Investment types
if "investment_type" in df.columns:
    investment_counts = (
        df["investment_type"]
        .fillna("Unknown")
        .replace("", "Unknown")
        .value_counts()
        .head(10)
        .sort_values()
    )

    if not investment_counts.empty:
        plt.figure(figsize=(10, 6))
        investment_counts.plot(kind="barh")
        plt.title("Most Common Investment Types")
        plt.xlabel("Number of Records")
        plt.ylabel("Investment Type")
        save_chart("04_investment_types.png")


# 5. Funding amount distribution
positive_amounts = df.loc[
    df["amount_in_usd"] > 0,
    "amount_in_usd"
].dropna()

if not positive_amounts.empty:
    plt.figure(figsize=(10, 5))
    sns.histplot(x=positive_amounts, bins=40)
    plt.xscale("log")
    plt.title("Distribution of Funding Amounts (Log Scale)")
    plt.xlabel("Funding Amount")
    plt.ylabel("Number of Records")
    save_chart("05_funding_distribution.png")


# 6. Median funding by investment type
if "investment_type" in df.columns:
    median_funding = (
        df[df["amount_in_usd"] > 0]
        .groupby("investment_type")["amount_in_usd"]
        .median()
        .dropna()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )

    if not median_funding.empty:
        plt.figure(figsize=(10, 6))
        median_funding.plot(kind="barh")
        plt.title("Top Investment Types by Median Funding")
        plt.xlabel("Median Funding Amount")
        plt.ylabel("Investment Type")
        save_chart("06_median_funding_by_investment_type.png")


# 7. Funding amount by year
box_data = df.dropna(subset=["year", "amount_in_usd"]).copy()
box_data = box_data[box_data["amount_in_usd"] > 0]

if not box_data.empty:
    plt.figure(figsize=(12, 6))
    sns.boxplot(
        data=box_data,
        x="year",
        y="amount_in_usd"
    )
    plt.yscale("log")
    plt.xticks(rotation=45)
    plt.title("Funding Amounts by Year (Log Scale)")
    plt.xlabel("Year")
    plt.ylabel("Funding Amount")
    save_chart("07_funding_by_year_boxplot.png")


print("\nAll available visualizations have been generated.")
print("Output folder:", OUTPUT_DIR)
