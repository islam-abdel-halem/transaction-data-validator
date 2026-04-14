"""Create static and interactive sales visualizations for Phase 5.

This script loads the analyzed sales dataset, prepares a region field for
interactive coloring, creates a Matplotlib sales trend plot, generates a
Seaborn correlation heatmap, and exports a Plotly scatter chart as HTML.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import pandas as pd
import plotly.express as px
import seaborn as sns
from matplotlib import pyplot as plt


def load_analyzed_data(filepath: Path) -> pd.DataFrame:
    """Load the analyzed sales CSV file into a DataFrame.

    Parameters:
        filepath: Path to ``analyzed_sales.csv``.

    Returns:
        A DataFrame with ``Date`` parsed as datetime and a derived
        ``Region`` column for interactive visualization.
    """
    dataframe = pd.read_csv(filepath, parse_dates=["Date"])
    return add_region_column(dataframe)


def add_region_column(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Add a derived region category when the dataset does not include one.

    The analyzed Phase 4 dataset contains ``City`` rather than ``Region``.
    To satisfy the plotting requirement without mutating earlier project
    outputs, this function derives a region label from each city.

    Parameters:
        dataframe: The source analyzed DataFrame.

    Returns:
        A copy of the DataFrame with a ``Region`` column.
    """
    city_to_region = {
        "London": "Northern Europe",
        "Berlin": "Central Europe",
        "Paris": "Western Europe",
        "Madrid": "Southern Europe",
        "Lisbon": "Southern Europe",
    }

    enriched = dataframe.copy()
    enriched["Region"] = enriched["City"].map(city_to_region).fillna("Other")
    return enriched


def create_sales_trend_plot(dataframe: pd.DataFrame, output_path: Path) -> None:
    """Create and save a Matplotlib line plot of sales over time.

    Parameters:
        dataframe: The analyzed sales DataFrame.
        output_path: Destination for the PNG image.
    """
    daily_sales = dataframe.groupby("Date", as_index=False)["USD_Amount"].sum()

    plt.figure(figsize=(11, 6))
    plt.plot(
        daily_sales["Date"],
        daily_sales["USD_Amount"],
        color="#1f77b4",
        linewidth=2.5,
        label="Daily USD Sales",
    )
    plt.title("Sales Trend Over Time", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Total Sales (USD)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def create_correlation_heatmap(dataframe: pd.DataFrame, output_path: Path) -> None:
    """Create and save a Seaborn heatmap for numeric correlations.

    Parameters:
        dataframe: The analyzed sales DataFrame.
        output_path: Destination for the PNG image.
    """
    numeric_columns = [
        "Price",
        "Quantity",
        "Amount",
        "Profit_Margin",
        "Conversion_Factor",
        "USD_Amount",
    ]
    correlation_matrix = dataframe[numeric_columns].corr()

    plt.figure(figsize=(9, 7))
    sns.heatmap(
        correlation_matrix,
        annot=True,
        cmap="YlGnBu",
        fmt=".2f",
        linewidths=0.5,
        square=True,
        cbar_kws={"shrink": 0.85},
    )
    plt.title("Correlation Matrix of Sales Metrics", fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def create_interactive_scatter(dataframe: pd.DataFrame, output_path: Path) -> None:
    """Create and save a Plotly scatter plot for transaction exploration.

    Parameters:
        dataframe: The analyzed sales DataFrame.
        output_path: Destination for the standalone HTML file.
    """
    figure = px.scatter(
        dataframe,
        x="USD_Amount",
        y="Profit_Margin",
        color="Region",
        hover_data={
            "Identifier": True,
            "City": True,
            "Product": True,
            "Date": True,
            "USD_Amount": ":.2f",
            "Profit_Margin": ":.2f",
        },
        title="Interactive Sales vs Profit Margin by Region",
        labels={
            "USD_Amount": "USD Amount",
            "Profit_Margin": "Profit Margin",
        },
        opacity=0.8,
    )
    figure.update_traces(marker={"size": 10, "line": {"width": 0.5, "color": "white"}})
    figure.update_layout(template="plotly_white", legend_title_text="Region")
    figure.write_html(output_path, full_html=True, include_plotlyjs=True)


