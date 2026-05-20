"""
ETL Module — File loading, DataFrame cleaning, column standardization.
All functions are null-safe and never drop rows.
"""
import pandas as pd
import numpy as np
from config.constants import DROP_COLUMNS, COLUMN_ALIASES


def load_file(uploaded_file):
    """Load an uploaded file (Excel or CSV) into a raw DataFrame.
    Always loads with dtype=str to prevent type inference issues.
    Returns empty DataFrame on failure.
    """
    try:
        name = getattr(uploaded_file, "name", str(uploaded_file)).lower()
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, dtype=str, keep_default_na=False)
        else:
            df = pd.read_excel(
                uploaded_file, dtype=str, engine="openpyxl",
                keep_default_na=False,
            )
        return df
    except Exception as e:
        print(f"[ETL] Error loading file: {e}")
        return pd.DataFrame()


def load_file_sheet(path, sheet_name=None):
    """Load a local Excel file by path, optionally specifying sheet name.
    Always loads with dtype=str.
    """
    try:
        kwargs = {"dtype": str, "engine": "openpyxl", "keep_default_na": False}
        if sheet_name:
            kwargs["sheet_name"] = sheet_name
        return pd.read_excel(path, **kwargs)
    except Exception as e:
        print(f"[ETL] Error loading file {path}: {e}")
        return pd.DataFrame()


def clean_dataframe(df):
    """Clean a raw DataFrame:
    1. Drop known junk columns (Star ID.1 etc.)
    2. Rename columns via COLUMN_ALIASES
    3. Strip whitespace from all string columns
    4. Create _NAME_CLEAN (uppercase) from Name column
    5. Never drops any rows.
    Returns cleaned DataFrame (copy).
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    # 1. Drop known junk columns
    for col in DROP_COLUMNS:
        if col in df.columns:
            df.drop(columns=[col], inplace=True, errors="ignore")

    # 2. Rename columns using alias dictionary
    rename_map = {}
    for col in df.columns:
        stripped = str(col).strip()
        if stripped in COLUMN_ALIASES and COLUMN_ALIASES[stripped] not in df.columns:
            rename_map[col] = COLUMN_ALIASES[stripped]
        elif stripped != col:
            rename_map[col] = stripped
    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    # 3. Strip whitespace from all string columns
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()
            # Replace empty strings and 'nan' with actual NaN
            df[col] = df[col].replace({"": np.nan, "nan": np.nan, "None": np.nan})

    # 4. Create _NAME_CLEAN column
    if "Name" in df.columns:
        df["_NAME_CLEAN"] = (
            df["Name"]
            .fillna("")
            .astype(str)
            .str.upper()
            .str.strip()
        )
    else:
        df["_NAME_CLEAN"] = ""

    return df


def standardize_columns(df, expected_cols):
    """Ensure all expected columns exist in the DataFrame.
    Missing columns are filled with NaN. Extra columns are kept.
    Never drops rows. Never crashes on missing columns.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=expected_cols)

    df = df.copy()
    for col in expected_cols:
        if col not in df.columns:
            df[col] = np.nan
    return df
