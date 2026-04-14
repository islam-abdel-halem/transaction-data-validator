"""Analyze restaurant sales data with Pandas and NumPy.

This script loads the Kaggle sales dataset, normalizes the schema,
creates vectorized analytical features, simulates and repairs missing
values, merges city-level currency conversion factors, computes summary
aggregations, and saves the final processed dataset to CSV.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def locate_dataset() -> Path:
    """Locate the Kaggle sales dataset file.

    The assignment references ``Sales-Data-Analysis.csv``. The downloaded
    Kaggle file currently includes a leading numeric prefix, so this helper
    checks a few likely locations and returns the first match.

    Returns:
        A ``Path`` object pointing to the dataset CSV file.

    Raises:
        FileNotFoundError: If the dataset cannot be found locally.
    """
    project_dir = Path(__file__).resolve().parent
    candidate_paths = [
        project_dir / "Sales-Data-Analysis.csv",
        project_dir / "9. Sales-Data-Analysis.csv",
        Path.home()
        / ".cache"
        / "kagglehub"
        / "datasets"
        / "rohitgrewal"
        / "restaurant-sales-data"
        / "versions"
        / "2"
        / "Sales-Data-Analysis.csv",
        Path.home()
        / ".cache"
        / "kagglehub"
        / "datasets"
        / "rohitgrewal"
        / "restaurant-sales-data"
        / "versions"
        / "2"
        / "9. Sales-Data-Analysis.csv",
    ]

    for path in candidate_paths:
        if path.exists():
            return path

    raise FileNotFoundError(
        "Sales-Data-Analysis.csv could not be found. "
        "Download the Kaggle dataset before running this script."
    )


def load_sales_data(csv_path: Path) -> pd.DataFrame:
    """Load the sales dataset and normalize the expected schema.

    Parameters:
        csv_path: The path to the source CSV file.

    Returns:
        A cleaned DataFrame with the required column names.

    Raises:
        ValueError: If one or more required columns are missing.
    """
    dataframe = pd.read_csv(csv_path, parse_dates=["Date"], dayfirst=True)
    dataframe = dataframe.rename(columns={"Order ID": "Identifier"})

    text_columns = [
        "Product",
        "Purchase Type",
        "Payment Method",
        "Manager",
        "City",
    ]
    for column in text_columns:
        if column in dataframe.columns:
            dataframe[column] = dataframe[column].astype(str).str.strip()

    required_columns = [
        "Identifier",
        "Date",
        "Product",
        "Price",
        "Quantity",
        "Purchase Type",
        "Payment Method",
        "Manager",
        "City",
    ]
    missing_columns = [column for column in required_columns if column not in dataframe.columns]

    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    return dataframe


def create_currency_rates() -> pd.DataFrame:
    """Create a city-level currency conversion table.

    Returns:
        A DataFrame containing ``City`` and ``Conversion_Factor`` columns.
    """
    return pd.DataFrame(
        {
            "City": ["London", "Berlin", "Madrid", "Lisbon", "Paris"],
            "Conversion_Factor": [1.28, 1.09, 1.09, 1.09, 1.09],
        }
    )


def transform_sales_data(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Apply cleaning, feature engineering, merging, and aggregation steps.

    Parameters:
        dataframe: The source sales DataFrame.

    Returns:
        A tuple containing:
        - The final processed DataFrame.
        - Total sales per city.
        - Average monthly profit margin.
    """
    transformed = dataframe.copy()

    # Vectorized revenue calculation avoids row-by-row Python loops.
    transformed["Amount"] = transformed["Price"] * transformed["Quantity"]

    # Inject 5% missing values in a reproducible way to simulate incomplete data.
    missing_count = max(1, int(round(len(transformed) * 0.05)))
    rng = np.random.default_rng(seed=42)
    missing_indices = rng.choice(transformed.index.to_numpy(), size=missing_count, replace=False)
    transformed.loc[missing_indices, "Amount"] = np.nan

    # Fill with the mean amount so we preserve rows for later city/month analysis.
    transformed["Amount"] = transformed["Amount"].fillna(transformed["Amount"].mean())

    # Profit margin is computed with a vectorized percentage multiplier.
    transformed["Profit_Margin"] = transformed["Amount"] * 0.15

    currency_rates = create_currency_rates()
    transformed = transformed.merge(currency_rates, on="City", how="left")
    transformed["Conversion_Factor"] = transformed["Conversion_Factor"].fillna(1.0)

    # USD normalization is also fully vectorized for performance.
    transformed["USD_Amount"] = transformed["Amount"] * transformed["Conversion_Factor"]

    total_sales_per_city = (
        transformed.groupby("City", as_index=False)["USD_Amount"]
        .sum()
        .rename(columns={"USD_Amount": "Total_USD_Sales"})
    )

    average_profit_margin_per_month = (
        transformed.groupby(transformed["Date"].dt.to_period("M"))["Profit_Margin"]
        .mean()
        .reset_index()
    )
    average_profit_margin_per_month["Date"] = average_profit_margin_per_month["Date"].astype(str)
    average_profit_margin_per_month = average_profit_margin_per_month.rename(
        columns={"Date": "Month", "Profit_Margin": "Average_Profit_Margin"}
    )

    return transformed, total_sales_per_city, average_profit_margin_per_month


def save_analyzed_data(dataframe: pd.DataFrame, output_path: Path) -> None:
    """Save the processed DataFrame to CSV.

    Parameters:
        dataframe: The processed DataFrame to save.
        output_path: The destination path for the analyzed CSV file.
    """
    dataframe.to_csv(output_path, index=False)


