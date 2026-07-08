import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, List

# Standard Color Palette for SupplySense AI
THEME_COLORS = {
    "background": "#161B22",
    "text": "white",
    "primary": "#00D4FF",
    "secondary": "#7B61FF",
    "accent": "#FF4B4B",
    "grid": "#2D333B"
}

def apply_plot_theme(fig: go.Figure) -> go.Figure:
    """
    Applies unified dark theme styling to a Plotly figure.

    Args:
        fig (go.Figure): The input Plotly figure.

    Returns:
        go.Figure: Styled Plotly figure.
    """
    fig.update_layout(
        paper_bgcolor=THEME_COLORS["background"],
        plot_bgcolor=THEME_COLORS["background"],
        font=dict(family="Poppins, sans-serif", color=THEME_COLORS["text"]),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)"
        )
    )
    
    # Update axes if they exist in the figure type
    fig.update_xaxes(
        showgrid=True, 
        gridcolor=THEME_COLORS["grid"], 
        linecolor=THEME_COLORS["grid"],
        zeroline=False
    )
    fig.update_yaxes(
        showgrid=True, 
        gridcolor=THEME_COLORS["grid"], 
        linecolor=THEME_COLORS["grid"],
        zeroline=False
    )
    
    return fig

def create_bar_chart(
    df: pd.DataFrame, 
    x: str, 
    y: str, 
    color: Optional[str] = None, 
    text: Optional[str] = None,
    height: int = 400,
    title: Optional[str] = None
) -> go.Figure:
    """Creates a standardized bar chart."""
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        text=text,
        height=height,
        title=title,
        color_discrete_sequence=[THEME_COLORS["primary"], THEME_COLORS["secondary"]]
    )
    if text:
        fig.update_traces(textposition="outside")
    return apply_plot_theme(fig)

def create_pie_chart(
    df: pd.DataFrame, 
    names: str, 
    values: Optional[str] = None,
    hole: float = 0.6,
    height: int = 400,
    title: Optional[str] = None
) -> go.Figure:
    """Creates a standardized pie/donut chart."""
    fig = px.pie(
        df,
        names=names,
        values=values,
        hole=hole,
        height=height,
        title=title,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    return apply_plot_theme(fig)

def create_scatter_plot(
    df: pd.DataFrame, 
    x: str, 
    y: str, 
    size: Optional[str] = None, 
    color: Optional[str] = None, 
    hover_name: Optional[str] = None,
    height: int = 450,
    title: Optional[str] = None
) -> go.Figure:
    """Creates a standardized scatter plot."""
    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=size,
        color=color,
        hover_name=hover_name,
        height=height,
        title=title,
        color_continuous_scale="Viridis"
    )
    return apply_plot_theme(fig)

def create_histogram(
    df: pd.DataFrame, 
    x: str, 
    nbins: int = 20, 
    color_discrete_sequence: Optional[List[str]] = None,
    height: int = 400,
    title: Optional[str] = None
) -> go.Figure:
    """Creates a standardized histogram."""
    colors = color_discrete_sequence or [THEME_COLORS["primary"]]
    fig = px.histogram(
        df,
        x=x,
        nbins=nbins,
        height=height,
        title=title,
        color_discrete_sequence=colors
    )
    return apply_plot_theme(fig)
