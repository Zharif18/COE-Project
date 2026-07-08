import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict

@st.cache_data
def _read_css_cached(file_path_str: str) -> str:
    """Reads a CSS file's contents from disk with caching to reduce disk reads."""
    path = Path(file_path_str)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return ""

def load_css(css_file_path: str) -> None:
    """
    Safely loads a CSS stylesheet and injects it into Streamlit's markdown.
    Uses cached disk reads for performance.
    """
    css_content = _read_css_cached(css_file_path)
    if not css_content:
        # Fallback to lowercase assets folder
        fallback_path = Path("assets") / Path(css_file_path).name
        css_content = _read_css_cached(str(fallback_path))
        
    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

def format_currency(value: float) -> str:
    """Formats float values to Indian Rupees (INR) currency formatting."""
    return f"₹{value:,.2f}"

def format_short_currency(value: float) -> str:
    """Formats float values to short currency (e.g. ₹1.2M, ₹45K)."""
    if value >= 1_000_000:
        return f"₹{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"₹{value/1_000:.1f}K"
    return f"₹{value:.2f}"

def format_percent(value: float) -> str:
    """Formats float values to percentages."""
    return f"{value:.1f}%"

def render_page_header(title: str, subtitle: str) -> None:
    """Standardizes headers across all pages."""
    st.title(title)
    st.caption(subtitle)
    st.markdown("---")

def style_status_column(df: pd.DataFrame, col_name: str, color_map: Dict[str, str]):
    """
    Applies custom HTML color mapping to a specific column in a Pandas DataFrame.
    Gracefully handles pandas version differences (Pandas 2.0 uses 'style.map',
    while older versions use 'style.applymap').
    
    Args:
        df (pd.DataFrame): Target dataframe.
        col_name (str): Column to style (e.g., 'Status').
        color_map (dict): Dict mapping column values to HEX colors (e.g., {'Delivered': '#10B981'}).
        
    Returns:
        Styler object representing the styled DataFrame.
    """
    if col_name not in df.columns:
        return df.style

    def apply_color(val):
        color = color_map.get(val, '')
        if color:
            return f'color: {color}; font-weight: 600;'
        return ''

    try:
        # Pandas >= 2.0.0
        return df.style.map(apply_color, subset=[col_name])
    except AttributeError:
        # Pandas < 2.0.0
        return df.style.applymap(apply_color, subset=[col_name])
