import os
import streamlit as st
import pandas as pd
from pathlib import Path
from typing import List, Dict

# Expected CSV schemas
EXPECTED_SCHEMAS: Dict[str, List[str]] = {
    "inventory.csv": [
        "Product",
        "Category",
        "Current Stock",
        "Minimum Stock",
        "Warehouse",
        "Daily Sales",
        "Cost"
    ],
    "suppliers.csv": [
        "Supplier",
        "Location",
        "Average Delay",
        "Defect Rate",
        "Rating",
        "Cost Index"
    ],
    "orders.csv": [
        "Order ID",
        "Customer",
        "Product",
        "Quantity",
        "Status",
        "Delivery Date",
        "Supplier"
    ],
    "shipments.csv": [
        "Shipment ID",
        "Route",
        "Distance",
        "Status",
        "Delay",
        "Fuel Cost",
        "Shipment Date"
    ]
}

DATA_DIR = Path("data")

def validate_dataframe(df: pd.DataFrame, filename: str) -> bool:
    """Checks if the loaded DataFrame matches the required schema columns."""
    if filename not in EXPECTED_SCHEMAS:
        return True
    
    expected_cols = EXPECTED_SCHEMAS[filename]
    missing_cols = [col for col in expected_cols if col not in df.columns]
    
    if missing_cols:
        st.error(f"❌ Schema validation failed for `{filename}`. Missing columns: {', '.join(missing_cols)}")
        return False
    return True

def get_file_mtime(filename: str) -> float:
    """Returns the modification time of the file on disk to invalidate cached runs."""
    file_path = DATA_DIR / filename
    if file_path.exists():
        return os.path.getmtime(file_path)
    return 0.0

@st.cache_data(show_spinner="Syncing datasets...")
def _load_csv_cached(filename: str, mtime: float) -> pd.DataFrame:
    """
    Internal cached loading function. Streamlit tracks the 'mtime' parameter
    to detect when the file is modified on disk.
    """
    file_path = DATA_DIR / filename
    try:
        df = pd.read_csv(file_path)
        if validate_dataframe(df, filename):
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Failed to parse `{filename}`: {str(e)}")
        return pd.DataFrame()

def load_csv(filename: str) -> pd.DataFrame:
    """
    Exposed loader endpoint. Validates existence and queries cached values
    while checking for file changes.
    """
    file_path = DATA_DIR / filename
    if not file_path.exists():
        st.error(f"⚠️ Error: File `{file_path}` not found.")
        return pd.DataFrame()
        
    mtime = get_file_mtime(filename)
    return _load_csv_cached(filename, mtime)

def clear_data_cache():
    """Manually flushes Streamlit's data loading cache."""
    st.cache_data.clear()
