import streamlit as st
import pandas as pd
from utils.metrics import get_supplier_metrics
from utils.charts import create_scatter_plot, create_bar_chart
from utils.helpers import render_page_header

def render_suppliers(suppliers: pd.DataFrame) -> None:
    """
    Renders the Supplier Management and Analysis page, featuring
    performance index ratings, defect rates, and delay distributions.
    """
    render_page_header("🏭 Supplier Management", "Analyze supplier ratings, delivery times, and defect rates.")

    if suppliers.empty:
        st.error("No supplier records found. Please check suppliers.csv.")
        return

    # 1. Supplier KPIs
    stats = get_supplier_metrics(suppliers)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Partners", stats["total"])
    col2.metric("Average Rating", f"{stats['avg_rating']} ⭐")
    col3.metric("Average Delay", f"{stats['avg_delay']} Days")
    col4.metric("Avg Defect Rate", f"{stats['avg_defect_rate']}%")

    st.markdown("---")

    # 2. Filters Row
    left, right = st.columns([2, 1])

    with left:
        search = st.text_input("🔍 Search Supplier Name", placeholder="Supplier_...")
    with right:
        location_options = ["All"] + sorted(suppliers["Location"].unique().tolist())
        location = st.selectbox("Location Filter", location_options)

    # 3. Filter DataFrame
    df_filtered = suppliers.copy()
    if search:
        df_filtered = df_filtered[
            df_filtered["Supplier"].str.contains(search, case=False)
        ]
    if location != "All":
        df_filtered = df_filtered[
            df_filtered["Location"] == location
        ]

    # Show data directory with custom column configs
    st.subheader("📋 Supplier Directory")
    
    max_defect = float(suppliers["Defect Rate"].max()) if not suppliers.empty else 5.0
    st.dataframe(
        df_filtered, 
        use_container_width=True, 
        height=320,
        column_config={
            "Rating": st.column_config.NumberColumn("Reputation", format="%.2f ⭐"),
            "Average Delay": st.column_config.NumberColumn("Transit Delay", format="%d days"),
            "Defect Rate": st.column_config.ProgressColumn(
                "Defect Rate",
                help="Average percentage of defective parts received",
                format="%.2f%%",
                min_value=0,
                max_value=max_defect
            ),
            "Cost Index": st.column_config.ProgressColumn(
                "Cost Index",
                help="Supplier relative cost bracket (0-100)",
                format="%d",
                min_value=0,
                max_value=100
            ),
            "Location": st.column_config.TextColumn("Hub Location")
        }
    )

    st.markdown("---")

    # 4. Graphs Section
    left_chart, right_chart = st.columns(2)

    with left_chart:
        st.subheader("📊 Supplier Cost Index Comparison")
        if not df_filtered.empty:
            fig1 = create_bar_chart(
                df_filtered.sort_values(by="Cost Index", ascending=False).head(15),
                x="Supplier",
                y="Cost Index",
                color="Location"
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("No records to visualize.")

    with right_chart:
        st.subheader("⚠️ Defect Rate vs Delay Risk Matrix")
        if not df_filtered.empty:
            fig2 = create_scatter_plot(
                df_filtered,
                x="Average Delay",
                y="Defect Rate",
                size="Cost Index",
                color="Rating",
                hover_name="Supplier"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No records to visualize.")
            
    st.markdown("---")
    
    # 5. Highlight top underperforming suppliers
    st.subheader("🚨 Risk Review: Underperforming Suppliers")
    critical_suppliers = suppliers[
        (suppliers["Defect Rate"] > 3.0) | (suppliers["Average Delay"] > 7) | (suppliers["Rating"] < 3.5)
    ]
    if not critical_suppliers.empty:
        st.dataframe(
            critical_suppliers, 
            use_container_width=True,
            column_config={
                "Rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                "Defect Rate": st.column_config.NumberColumn("Defect Rate", format="%.2f%% ⚠️"),
                "Average Delay": st.column_config.NumberColumn("Delay", format="%d days 🚨")
            }
        )
    else:
        st.success("🎉 All suppliers meet the threshold requirements for ratings, delays, and defect rates.")
