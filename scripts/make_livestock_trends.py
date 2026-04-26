"""
Reproduce Figure: Global trends in animal-source food demand, livestock production,
and livestock-related greenhouse gas emissions.

This script reads raw FAOSTAT CSV files from data/raw/, constructs annual demand,
production, and emissions series, normalizes each series to 2010 = 100, and exports
processed data and figure files.

Run from the repository root:
    python scripts/make_livestock_trends.py

If running inside a Jupyter notebook, use:
    !python scripts/make_livestock_trends.py
"""

from pathlib import Path
from typing import Iterable

import pandas as pd
import matplotlib.pyplot as plt


# -----------------------------
# Project paths
# -----------------------------
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "figures"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

FBS_FILE = RAW_DIR / "FAOSTAT_FBS.csv"
QCL_FILE = RAW_DIR / "FAOSTAT_QCL.csv"
GT_FILE = RAW_DIR / "FAOSTAT_GT.csv"

START_YEAR = 2010
END_YEAR = 2023
BASE_YEAR = 2010


# -----------------------------
# FAOSTAT selections
# -----------------------------
FBS_ELEMENT = "Food supply quantity (kg/capita/yr)"
FBS_ITEMS = [
    "Bovine Meat",
    "Pigmeat",
    "Poultry Meat",
    "Mutton & Goat Meat",
    "Meat, Other",
]

QCL_ELEMENT = "Production"
QCL_ITEMS = [
    "Meat of cattle with the bone, fresh or chilled",
    "Meat of pig with the bone, fresh or chilled",
    "Meat of chickens, fresh or chilled",
    "Meat of ducks, fresh or chilled",
    "Meat of geese, fresh or chilled",
    "Meat of turkeys, fresh or chilled",
    "Meat of sheep, fresh or chilled",
    "Meat of goat, fresh or chilled",
    "Meat of buffalo, fresh or chilled",
    "Horse meat, fresh or chilled",
    "Meat of camels, fresh or chilled",
    "Meat of other domestic camelids, fresh or chilled",
    "Meat of asses, fresh or chilled",
    "Meat of mules, fresh or chilled",
    "Other meat of mammals, fresh or chilled",
]

GT_ELEMENT = "Emissions (CO2eq) (AR5)"
GT_ITEMS = [
    "Enteric Fermentation",
    "Manure Management",
    "Manure applied to Soils",
    "Manure left on Pasture",
]


def validate_items(df: pd.DataFrame, column: str, expected: Iterable[str], label: str) -> None:
    """Raise an informative error if any selected FAOSTAT items are missing."""
    available = set(df[column].dropna().unique())
    missing = [item for item in expected if item not in available]
    if missing:
        raise ValueError(
            f"Missing {label} items in column '{column}': {missing}\n"
            f"Available items include: {sorted(list(available))[:50]}"
        )


def validate_years(df: pd.DataFrame, label: str) -> None:
    """Confirm that all years in the study period are present."""
    available_years = set(df["Year"].dropna().astype(int).unique())
    expected_years = set(range(START_YEAR, END_YEAR + 1))
    missing = sorted(expected_years - available_years)
    if missing:
        raise ValueError(f"{label} is missing years in {START_YEAR}-{END_YEAR}: {missing}")


def filter_years(df: pd.DataFrame) -> pd.DataFrame:
    """Restrict a dataframe to the study period."""
    return df[(df["Year"] >= START_YEAR) & (df["Year"] <= END_YEAR)].copy()


def normalize_to_base(df: pd.DataFrame, value_col: str = "Value") -> pd.DataFrame:
    """Normalize a time series to BASE_YEAR = 100."""
    base_values = df.loc[df["Year"] == BASE_YEAR, value_col]
    if base_values.empty:
        raise ValueError(f"Base year {BASE_YEAR} not found in series.")
    base = float(base_values.iloc[0])
    if base == 0:
        raise ValueError(f"Base year {BASE_YEAR} value is zero; cannot normalize.")

    out = df.copy()
    out["Index"] = out[value_col] / base * 100
    return out


def build_demand_series(fbs: pd.DataFrame) -> pd.DataFrame:
    """
    Construct the demand series from FAOSTAT Food Balance Sheets.

    FBS values are reported in kg/capita/year and should not be summed directly
    across countries. The aggregation therefore uses two steps:
      1. Sum selected meat categories within each country-year.
      2. Average those country-year totals across reporting countries for each year.

    The result is an unweighted mean national per-capita meat-supply indicator,
    not a population-weighted global per-capita estimate.
    """
    validate_items(fbs, "Item", FBS_ITEMS, "FBS")
    validate_years(fbs, "FBS")

    fbs = filter_years(fbs)
    fbs_filtered = fbs[
        (fbs["Element"] == FBS_ELEMENT) &
        (fbs["Item"].isin(FBS_ITEMS))
    ].copy()

    # Step 1: sum selected meat categories within each country-year.
    fbs_country = fbs_filtered.groupby(["Area", "Year"], as_index=False)["Value"].sum()

    # Step 2: average country-level totals across reporting countries for each year.
    fbs_agg = fbs_country.groupby("Year", as_index=False)["Value"].mean()

    fbs_agg["Series"] = "Demand: mean national per-capita meat supply"
    fbs_agg["Unit"] = "kg/capita/year"
    return fbs_agg


def build_production_series(qcl: pd.DataFrame) -> pd.DataFrame:
    """Construct global livestock meat production by summing selected QCL items."""
    validate_items(qcl, "Item", QCL_ITEMS, "QCL")
    validate_years(qcl, "QCL")

    qcl = filter_years(qcl)
    qcl_filtered = qcl[
        (qcl["Element"] == QCL_ELEMENT) &
        (qcl["Item"].isin(QCL_ITEMS))
    ].copy()

    qcl_agg = qcl_filtered.groupby("Year", as_index=False)["Value"].sum()
    qcl_agg["Series"] = "Production: total livestock meat output"
    qcl_agg["Unit"] = "; ".join(sorted(qcl_filtered["Unit"].dropna().unique()))
    return qcl_agg


def build_emissions_series(gt: pd.DataFrame) -> pd.DataFrame:
    """Construct livestock-related GHG emissions by summing selected GT items."""
    validate_items(gt, "Item", GT_ITEMS, "GT")
    validate_years(gt, "GT")

    gt = filter_years(gt)
    gt_filtered = gt[
        (gt["Element"] == GT_ELEMENT) &
        (gt["Item"].isin(GT_ITEMS))
    ].copy()

    gt_agg = gt_filtered.groupby("Year", as_index=False)["Value"].sum()
    gt_agg["Series"] = "Emissions: livestock-related greenhouse gases"
    gt_agg["Unit"] = "; ".join(sorted(gt_filtered["Unit"].dropna().unique()))
    return gt_agg


def main() -> None:
    """Run the full data-processing and figure-generation pipeline."""
    fbs = pd.read_csv(FBS_FILE)
    qcl = pd.read_csv(QCL_FILE)
    gt = pd.read_csv(GT_FILE)

    demand = build_demand_series(fbs)
    production = build_production_series(qcl)
    emissions = build_emissions_series(gt)

    demand_norm = normalize_to_base(demand)
    production_norm = normalize_to_base(production)
    emissions_norm = normalize_to_base(emissions)

    processed_long = pd.concat(
        [demand_norm, production_norm, emissions_norm],
        ignore_index=True
    )[["Year", "Series", "Value", "Unit", "Index"]]
    processed_long.to_csv(PROCESSED_DIR / "livestock_trends_index_long.csv", index=False)

    processed_wide = processed_long.pivot(index="Year", columns="Series", values="Index")
    processed_wide.to_csv(PROCESSED_DIR / "livestock_trends_index_wide.csv")

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(
        demand_norm["Year"],
        demand_norm["Index"],
        label="Per capita animal-source food demand",
    )
    ax.plot(
        production_norm["Year"],
        production_norm["Index"],
        label="Total livestock production",
    )
    ax.plot(
        emissions_norm["Year"],
        emissions_norm["Index"],
        label="Livestock-related greenhouse gas emissions",
    )

    ax.set_xlabel("Year")
    ax.set_ylabel("Index (2010 = 100)")
    ax.set_title("Global Trends in Livestock Demand, Production, and Emissions")
    ax.legend(loc="upper left", frameon=False)


    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "livestock_trends_figure.pdf", dpi=300, bbox_inches="tight")
    fig.savefig(FIGURES_DIR / "livestock_trends_figure.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    print("Reproducibility run complete.")
    print(f"Study period: {START_YEAR}-{END_YEAR}")
    print(f"Processed data written to: {PROCESSED_DIR}")
    print(f"Figures written to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
