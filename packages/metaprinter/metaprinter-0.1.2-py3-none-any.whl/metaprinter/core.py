import json
import polars as pl
import pandas as pd
import os
from pathlib import Path
from io import StringIO
import sys


def print_metadata(df, meta, show_all_columns=True, max_width=222):
    """
    Print a comprehensive metadata summary for SPSS data loaded with pyreadstat.
    
    Parameters:
    -----------
    df : polars.DataFrame or pandas.DataFrame
        The dataframe containing the SPSS data
    meta : pyreadstat metadata object
        The metadata object returned by pyreadstat.read_sav()
    show_all_columns : bool, default True
        Whether to show all columns without truncation
    max_width : int, default 222
        Maximum table width in characters
    
    Returns:
    --------
    polars.DataFrame
        The metadata summary table for further use if needed
    """
    
    # Convert to Polars if it's a Pandas DataFrame
    if isinstance(df, pd.DataFrame):
        df = pl.from_pandas(df)
    
    # Count categorical labels for each variable
    cat_counts = {
        var: len(labels)
        for var, labels in meta.variable_value_labels.items()
    }
    
    # Create pretty-formatted JSON strings for value labels
    value_labels_pretty = [
        json.dumps(
            meta.variable_value_labels.get(col, {}), 
            indent=2, 
            ensure_ascii=False
        ) if meta.variable_value_labels.get(col) else ""
        for col in df.columns
    ]
    
    # Build the comprehensive metadata summary
    summary = pl.DataFrame({
        "column": df.columns,
        "dtype": df.dtypes,
        "column_n": [
            len(df[c].drop_nulls()) 
            for c in df.columns
        ],
        "n_uniques": [
            df[c].drop_nulls().n_unique() 
            for c in df.columns
        ],
        "n_categories": [
            cat_counts.get(c, 0) 
            for c in df.columns
        ],
        "column_label": meta.column_labels,  # Using the list directly as you suggested
        "value_labels": value_labels_pretty,
    })
    
    # Print file-level metadata header
    print("=" * 60)
    print("SPSS FILE METADATA")
    print("=" * 60)
    print(f"File encoding   : {meta.file_encoding!r}")
    print(f"Number of cols  : {meta.number_columns}")
    print(f"Number of rows  : {meta.number_rows}")
    print(f"Table name      : {meta.table_name!r}")
    print(f"File label      : {meta.file_label!r}")
    print(f"Notes           : {meta.notes!r}")
    print()
    
    print("VARIABLE METADATA")
    print("=" * 60)
    
    # Configure display options and print the summary table
    config_options = {
        'tbl_width_chars': max_width,
        'fmt_str_lengths': 5000
    }
    
    if show_all_columns:
        config_options.update({
            'tbl_cols': -1,
            'tbl_rows': -1
        })
    
    with pl.Config(**config_options):
        print(summary)
    
    return summary


def export_metadata(df, meta, filename=None, show_all_columns=True, max_width=222):
    """
    Export SPSS metadata summary to a text file in the downloads folder.
    
    Parameters:
    -----------
    df : polars.DataFrame or pandas.DataFrame
        The dataframe containing the SPSS data
    meta : pyreadstat metadata object
        The metadata object returned by pyreadstat.read_sav()
    filename : str, optional
        Custom filename (without extension). If None, uses "metadata_summary"
    show_all_columns : bool, default True
        Whether to show all columns without truncation
    max_width : int, default 222
        Maximum table width in characters
    
    Returns:
    --------
    str
        The full path where the file was saved
    """
    
    # Convert to Polars if it's a Pandas DataFrame
    if isinstance(df, pd.DataFrame):
        df = pl.from_pandas(df)
    
    # Count categorical labels for each variable
    cat_counts = {
        var: len(labels)
        for var, labels in meta.variable_value_labels.items()
    }
    
    # Create pretty-formatted JSON strings for value labels
    value_labels_pretty = [
        json.dumps(
            meta.variable_value_labels.get(col, {}), 
            indent=2, 
            ensure_ascii=False
        ) if meta.variable_value_labels.get(col) else ""
        for col in df.columns
    ]
    
    # Build the comprehensive metadata summary
    summary = pl.DataFrame({
        "column": df.columns,
        "dtype": df.dtypes,
        "column_n": [
            len(df[c].drop_nulls()) 
            for c in df.columns
        ],
        "n_uniques": [
            df[c].drop_nulls().n_unique() 
            for c in df.columns
        ],
        "n_categories": [
            cat_counts.get(c, 0) 
            for c in df.columns
        ],
        "column_label": meta.column_labels,
        "value_labels": value_labels_pretty,
    })
    
    # Determine the downloads folder path
    downloads_path = Path.home() / "Downloads"
    if not downloads_path.exists():
        # Fallback to current directory if Downloads folder doesn't exist
        downloads_path = Path.cwd()
    
    # Set filename
    if filename is None:
        filename = "metadata_summary"
    
    # Ensure .txt extension
    if not filename.endswith('.txt'):
        filename = f"{filename}.txt"
    
    full_path = downloads_path / filename
    
    # Capture the output that would normally go to stdout
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    try:
        # Generate the same output as the print function
        print("=" * 60)
        print("SPSS FILE METADATA")
        print("=" * 60)
        print(f"File encoding   : {meta.file_encoding!r}")
        print(f"Number of cols  : {meta.number_columns}")
        print(f"Number of rows  : {meta.number_rows}")
        print(f"Table name      : {meta.table_name!r}")
        print(f"File label      : {meta.file_label!r}")
        print(f"Notes           : {meta.notes!r}")
        print()
        
        print("VARIABLE METADATA")
        print("=" * 60)
        
        # Configure display options and capture the summary table
        config_options = {
            'tbl_width_chars': max_width,
            'fmt_str_lengths': 5000
        }
        
        if show_all_columns:
            config_options.update({
                'tbl_cols': -1,
                'tbl_rows': -1
            })
        
        with pl.Config(**config_options):
            print(summary)
        
        # Get the captured content
        content = captured_output.getvalue()
        
    finally:
        # Restore stdout
        sys.stdout = old_stdout
    
    # Write to file
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Metadata summary exported successfully to: {full_path}")
        return str(full_path)
        
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return None


def print_and_export_metadata(df, meta, export_filename=None, show_all_columns=True, max_width=222):
    """
    Convenience function that both prints and exports SPSS metadata summary.
    
    Parameters:
    -----------
    df : polars.DataFrame or pandas.DataFrame
        The dataframe containing the SPSS data
    meta : pyreadstat metadata object
        The metadata object returned by pyreadstat.read_sav()
    export_filename : str, optional
        Custom filename for export (without extension). If None, uses "metadata_summary"
    show_all_columns : bool, default True
        Whether to show all columns without truncation
    max_width : int, default 222
        Maximum table width in characters
    
    Returns:
    --------
    tuple
        (polars.DataFrame, str) - The metadata summary table and export file path
    """
    
    # Print to console
    summary = print_metadata(df, meta, show_all_columns, max_width)
    
    # Export to file
    export_path = export_metadata(df, meta, export_filename, show_all_columns, max_width)
    
    return summary, export_path


# Example usage:
# import pyreadstat
# 
# # Load SPSS data
# df, meta = pyreadstat.read_sav('your_file.sav')
# 
# # Option 1: Just print (original function)
# metadata_summary = print_metadata(df, meta)
# 
# # Option 2: Just export to file
# export_path = export_metadata(df, meta)
# 
# # Option 3: Both print and export
# summary, export_path = print_and_export_metadata(df, meta)
# 
# # Option 4: Export with custom filename
# export_path = export_metadata(df, meta, filename="my_custom_metadata")