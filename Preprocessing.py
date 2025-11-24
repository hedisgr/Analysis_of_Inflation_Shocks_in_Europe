import pandas as pd
import numpy as np


# ---------------------------------------------------
# Sheet index ranges per main category (for detailed file)
# ---------------------------------------------------

SHEETS_INDEX_FOOD = range(1, 76)
SHEETS_INDEX_HOUSING_ENERGY = range(76, 109)   # non-overlapping with transport
SHEETS_INDEX_TRANSPORT = range(109, 151)


# ---------------------------------------------------
# Functions
# ---------------------------------------------------

def cleaning_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw data extracted from a single Excel sheet.

    This function removes redundant columns, reshapes the data from wide to long format, 
    and enforces consistent data types to facilitate downstream concatenation.

    Args:
        df (pd.DataFrame): Raw DataFrame containing data from one Excel sheet.

    Returns:
        pd.DataFrame: A cleaned, long-format DataFrame ready for merging and analysis.
    """
    
    # Filter out redundant columns (Excel merged columns), 
    # replace specific Excel placeholders (':', 'd') with NaN, and 
    # reshape the dataset from wide to long format for analytical readiness.

    df = (
        df.iloc[:, [0] + [i for i in range(len(df.columns.to_list())) if i % 2 != 0]]
          .replace(":", np.nan)
          .replace("d", np.nan)
          .reset_index(drop=True)
          .rename(columns={"TIME": "Country"})
          .melt(
              id_vars="Country",
              var_name="Date",
              value_name="HICP"
          )
    )
    
    # Enforce strict data types and remove incomplete observations.
    df["Country"] = df["Country"].astype(str)
    df["Date"] = pd.to_datetime(df["Date"])
    df["HICP"] = pd.to_numeric(df["HICP"], errors="coerce")
    df.dropna(inplace=True)

    return df


def load_summary(file_path: str, columns_map: dict, summary_sheet: str = "Summary") -> pd.DataFrame:
    """
    Load and clean the 'Summary' sheet of an Excel workbook.

    Parameters
    ----------
    file_path : str
        Path to the Excel file.
    columns_map : dict
        Mapping from raw column names (e.g. 'Unnamed: 1') to cleaned names
        (e.g. 'sheet_name', 'description').
    summary_sheet : str, optional
        Name of the summary sheet, by default 'Summary'.

    Returns
    -------
    pd.DataFrame
        Cleaned summary DataFrame with renamed columns.
    """
    df = pd.read_excel(file_path, sheet_name=summary_sheet)

    cols_to_keep = list(columns_map.keys())
    df = (
        df
        # Remove header/info rows (e.g. 'Contents')
        .loc[df[cols_to_keep[0]] != "Contents", cols_to_keep]
        .dropna()
        .reset_index(drop=True)
        .rename(columns=columns_map)
    )
    return df

def map_sheet_to_category(sheet_name: str) -> str:
    """
    Map an Excel sheet name like 'Sheet 23' to a main COICOP category
    based on its numeric index.

    Parameters
    ----------
    sheet_name : str
        Sheet name, assumed to end with an integer index (e.g. 'Sheet 23').

    Returns
    -------
    str
        One of: 'Food', 'Housing & Energy', 'Transport', or 'Other'.
    """
    try:
        idx = int(sheet_name.split()[-1])
    except Exception:
        return "Other"

    if idx in SHEETS_INDEX_FOOD:
        return "Food"
    if idx in SHEETS_INDEX_HOUSING_ENERGY:
        return "Housing & Energy"
    if idx in SHEETS_INDEX_TRANSPORT:
        return "Transport"
    return "Other"


# ---------------------------------------------------
# Loader functions
# ---------------------------------------------------

def load_main_dataset(file_main: str) -> pd.DataFrame:
    """
    Load and clean the main HICP dataset:
    all EU countries & categories (dataset_all_eu_comp_2020.xlsx).

    Parameters
    ----------
    file_main : str
        Path to the main Excel file.

    Returns
    -------
    pd.DataFrame
        Long-format DataFrame with columns:
        ['Country', 'Date', 'HICP', 'label'].
    """
    summary_main = load_summary(
        file_path=file_main,
        columns_map={
            "Unnamed: 1": "sheet_name",
            "Unnamed: 3": "base",
            "Unnamed: 4": "description",
        },
    )

    sheet_names_main = summary_main["sheet_name"].tolist()
    descriptions_main = summary_main["description"].tolist()

    # In this workbook, the actual header row for data starts at row index 8
    main_header_row = [8]

    all_frames_main = []

    for sheet_name, label in zip(sheet_names_main, descriptions_main):
        sheet_df = pd.read_excel(file_main, sheet_name=sheet_name, header=main_header_row)
        clean_df = cleaning_dataframe(sheet_df)
        clean_df["label"] = label
        all_frames_main.append(clean_df)

    df_all = pd.concat(all_frames_main, axis=0, ignore_index=True)
    return df_all


def load_detailed_dataset(file_details: str):
    """
    Load and clean the detailed dataset by subcategory (details_per_cat.xlsx).

    Parameters
    ----------
    file_details : str
        Path to the detailed Excel file.

    Returns
    -------
    tuple
        (df_all_items, df_food, df_housing_energy, df_transport)
    """
    summary_details = load_summary(
        file_path=file_details,
        columns_map={
            "Unnamed: 1": "sheet_name",
            "Unnamed: 3": "base",
            "Unnamed: 4": "description",
        },
    )

    sheet_names_details = summary_details["sheet_name"].tolist()
    descriptions_details = summary_details["description"].tolist()

    details_header_row = [8]

    all_frames_items = []

    for sheet_name, label in zip(sheet_names_details, descriptions_details):
        sheet_df = pd.read_excel(file_details, sheet_name=sheet_name, header=details_header_row)
        clean_df = cleaning_dataframe(sheet_df)
        clean_df["label"] = label
        clean_df["Category"] = map_sheet_to_category(sheet_name)
        all_frames_items.append(clean_df)

    df_all_items = pd.concat(all_frames_items, axis=0, ignore_index=True)

    # Convenience DataFrames by main category
    df_food = df_all_items[df_all_items["Category"] == "Food"].copy()
    df_housing_energy = df_all_items[df_all_items["Category"] == "Housing & Energy"].copy()
    df_transport = df_all_items[df_all_items["Category"] == "Transport"].copy()

    return df_all_items, df_food, df_housing_energy, df_transport


def load_weights_dataset(file_weights: str) -> pd.DataFrame:
    """
    Load and clean the COICOP weights dataset (dataset_weigths.xlsx).

    Parameters
    ----------
    file_weights : str
        Path to the weights Excel file.

    Returns
    -------
    pd.DataFrame
        Long-format DataFrame with columns:
        ['Country', 'Date', 'HICP', 'label'] for the weights.
    """
    summary_weights = load_summary(
        file_path=file_weights,
        columns_map={
            "Unnamed: 1": "sheet_name",
            "Unnamed: 3": "description",
        },
    )

    sheet_names_weights = summary_weights["sheet_name"].tolist()
    descriptions_weights = summary_weights["description"].tolist()

    weights_header_row = [7]

    weight_frames = []

    for sheet_name, label in zip(sheet_names_weights, descriptions_weights):
        sheet_df = pd.read_excel(file_weights, sheet_name=sheet_name, header=weights_header_row)
        clean_df = cleaning_dataframe(sheet_df)
        clean_df["label"] = label
        weight_frames.append(clean_df)

    df_weights = pd.concat(weight_frames, axis=0, ignore_index=True)
    return df_weights


# ---------------------------------------------------
# High-level loader
# ---------------------------------------------------

def load_all_data(
    file_main: str = r"eu_hicp_datasets\hicp_main_categories_eu.xlsx",
    file_details: str = r"eu_hicp_datasets\hicp_subcategories_eu.xlsx",
    file_weights: str = r"eu_hicp_datasets\coicop_weights_eu.xlsx",
):
    """
    Load all datasets (main HICP, detailed items, and weights) in one call.

    Parameters
    ----------
    file_main : str, optional
        Path to the main HICP dataset.
    file_details : str, optional
        Path to the detailed subcategory dataset.
    file_weights : str, optional
        Path to the COICOP weights dataset.

    Returns
    -------
    dict
        Dictionary containing:
            - 'df_all'
            - 'df_all_items'
            - 'df_food'
            - 'df_housing_energy'
            - 'df_transport'
            - 'df_weights'
    """
    df_all = load_main_dataset(file_main)
    df_all_items, df_food, df_housing_energy, df_transport = load_detailed_dataset(file_details)
    df_weights = load_weights_dataset(file_weights)

    return {
        "df_all": df_all,
        "df_all_items": df_all_items,
        "df_food": df_food,
        "df_housing_energy": df_housing_energy,
        "df_transport": df_transport,
        "df_weights": df_weights,
    }
