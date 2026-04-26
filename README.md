# Livestock demand, production, and emissions trends

This repository reproduces the figure showing global trends in animal-source food demand, livestock production, and livestock-related greenhouse gas emissions associated with meat production.

## Study period

The analysis covers **2010–2023**, using the available FAOSTAT data in the included raw files.

## Data

Raw FAOSTAT files are stored in `data/raw/` with neutral filenames:

- `FAOSTAT_FBS.csv` — Food Balance Sheets (FBS)
- `FAOSTAT_QCL.csv` — Production (QCL)
- `FAOSTAT_GT.csv` — Emissions Totals (GT)

The data correspond to the latest available FAOSTAT release at the time of analysis.

## Variables and selections

### Demand: Food Balance Sheets (FBS)

Element:

- `Food supply quantity (kg/capita/yr)`

Items:

- `Bovine Meat`
- `Pigmeat`
- `Poultry Meat`
- `Mutton & Goat Meat`
- `Meat, Other`

Aggregation:

1. Sum selected meat categories within each country-year.
2. Average the resulting country-level per-capita totals across reporting countries for each year.

The resulting demand series is an **unweighted mean national per-capita meat supply indicator**, not a population-weighted global per-capita estimate.

### Production: Production (QCL)

Element:

- `Production`

Items:

- `Meat of cattle with the bone, fresh or chilled`
- `Meat of pig with the bone, fresh or chilled`
- `Meat of chickens, fresh or chilled`
- `Meat of ducks, fresh or chilled`
- `Meat of geese, fresh or chilled`
- `Meat of turkeys, fresh or chilled`
- `Meat of sheep, fresh or chilled`
- `Meat of goat, fresh or chilled`
- `Meat of buffalo, fresh or chilled`
- `Horse meat, fresh or chilled`
- `Meat of camels, fresh or chilled`
- `Meat of other domestic camelids, fresh or chilled`
- `Meat of asses, fresh or chilled`
- `Meat of mules, fresh or chilled`
- `Other meat of mammals, fresh or chilled`

Production values are summed across selected items and reporting countries by year.

### Emissions: Emissions Totals (GT)

Element:

- `Emissions (CO2eq) (AR5)`

Items:

- `Enteric Fermentation`
- `Manure Management`
- `Manure applied to Soils`
- `Manure left on Pasture`

Emissions values are summed across selected sources and reporting countries by year.

## Reproduce the figure

Install dependencies:

```bash
pip install -r requirements.txt
```

Run from the repository root:

```bash
python scripts/make_livestock_trends.py
```

If running inside a Jupyter notebook, prefix the command with `!`:

```python
!python scripts/make_livestock_trends.py
```

## Outputs

The script writes:

- `data/processed/livestock_trends_index_long.csv`
- `data/processed/livestock_trends_index_wide.csv`
- `figures/livestock_trends_figure.pdf`
- `figures/livestock_trends_figure.png`

## Interpretation

The series are indexed to 2010 = 100 to compare relative trends across variables with different units. The figure is intended to illustrate system-level persistence and divergence in trends, not to construct a strict accounting identity between demand, production, and emissions.

## Scope

This analysis focuses on livestock systems associated with meat production. The demand and production variables include only meat categories, and emissions are constructed from sources primarily linked to these systems (e.g., enteric fermentation and manure management).

Dairy production—including milk and derived products such as butter and cheese—is not explicitly included. Including these products would increase the absolute levels of demand, production, and emissions, but would not alter the overall upward trends observed over time. The results therefore provide a focused view of livestock trends centered on meat production.

