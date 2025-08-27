# SPSS Metadata Printer 📊

Easy-to-use Python package for extracting, viewing, and exporting metadata from SPSS files with beautiful formatting.

## ✨ Features

- 📋 **Pretty-print comprehensive SPSS metadata** to console
- 💾 **Export metadata summaries** to text files automatically saved to Downloads
- 🔄 **Support for Pandas and Polars** DataFrames
- 📊 **Detailed variable information** including labels, types, and value mappings
- 🎨 **Beautiful table formatting** with configurable width and display options

## 🚀 Quick Start

### Installation

```bash
pip install metaprinter
```

### Basic Usage

```python
import pyreadstat
from metaprinter import print_metadata, export_metadata

# Load your SPSS file
df, meta = pyreadstat.read_sav('data.sav')

# Display beautiful metadata summary
summary = print_metadata(df, meta)

# Export to Downloads/metadata_summary.txt
export_path = export_metadata(df, meta)
```

**Output Preview:**
```
============================================================
SPSS FILE METADATA
============================================================
File encoding   : 'UTF-8'
Number of cols  : 25
Number of rows  : 100
Table name      : 'Table'
File label      : 'Customer Satisfaction Survey'
Notes           : 'Notes'

VARIABLE METADATA
============================================================
┌───────────────┬─────────┬──────────┬───────────┬──────────────┬─────────────────────┬─────────────────────┐
│ column        ┆ dtype   ┆ column_n ┆ n_uniques ┆ n_categories ┆ column_label        ┆ value_labels        │
│ ---           ┆ ---     ┆ ---      ┆ ---       ┆ ---          ┆ ---                 ┆ ---                 │
│ str           ┆ str     ┆ i64      ┆ i64       ┆ i64          ┆ str                 ┆ str                 │
╞═══════════════╪═════════╪══════════╪═══════════╪══════════════╪═════════════════════╪═════════════════════╡
│ respondent_id ┆ Int64   ┆ 1547     ┆ 1547      ┆ 0            ┆ Respondent ID       ┆                     │
│ satisfaction  ┆ Int64   ┆ 1523     ┆ 5         ┆ 5            ┆ Satisfaction Level  ┆ {                   │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "1": "Very Low",  │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "2": "Low",       │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "3": "Neutral",   │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "4": "High",      │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "5": "Very High"  │
│               ┆         ┆          ┆           ┆              ┆                     ┆ }                   │
│ age           ┆ Int64   ┆ 1534     ┆ 6         ┆ 6            ┆ Age Group Category  ┆ {                   │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "1": "18-25",     │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "2": "26-35",     │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "3": "36-45",     │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "4": "46-55",     │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "5": "56-65",     │
│               ┆         ┆          ┆           ┆              ┆                     ┆   "6": "65+"        │
│               ┆         ┆          ┆           ┆              ┆                     ┆ }                   │
│ ...           ┆ ...     ┆ ...      ┆ ...       ┆ ...          ┆ ...                 ┆ ...                 │
└───────────────┴─────────┴──────────┴───────────┴──────────────┴─────────────────────┴─────────────────────┘
```

**Advanced Configuration:**

```python
# Customize table width for narrow displays
print_metadata(df, meta, max_width=120)

# Control column truncation
print_metadata(df, meta, show_all_columns=False)
```