import streamlit as st
import pandas as pd
from utils.metrics import get_inventory_metrics
from utils.charts import create_bar_chart, create_pie_chart
from utils.helpers import render_page_header

def render_inventory(inventory: pd.DataFrame) -> None:
    """
    Renders the Inventory Management page with search functionality,
    low stock alerts, warehouse distribution, and statistics.
    """
    render_page_header("📦 Inventory Management", "Monitor inventory levels across warehouses.")

    if inventory.empty:
        st.error("No inventory data found. Please check inventory.csv.")
        return

    # 1. Calculate granular inventory metrics
    stats = get_inventory_metrics(inventory)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Items", stats["total_items"])
    col2.metric("Low Stock Items", stats["low_stock"], delta="-12% from last week" if stats["low_stock"] > 0 else "Optimal", delta_color="inverse")
    col3.metric("Average Stock Level", stats["avg_stock"])
    
    # Render total inventory valuation as a premium statistic
    col4.metric("Inventory Valuation", f"₹{stats['total_value']:,.0f}")

    st.markdown("---")

    # 2. Filters Row
    left, right = st.columns([2, 1])

    with left:
        search = st.text_input("🔍 Search Product", placeholder="Type product name...")

    with right:
        category_options = ["All"] + sorted(inventory["Category"].unique().tolist())
        category = st.selectbox("Category Filter", category_options)

    # 3. Filter DataFrame
    df_filtered = inventory.copy()

    if search:
        df_filtered = df_filtered[
            df_filtered["Product"].str.contains(search, case=False)
        ]

    if category != "All":
        df_filtered = df_filtered[
            df_filtered["Category"] == category
        ]

    # Display Data Table with custom column configurations
    st.subheader("📋 Inventory Directory")
    
    max_stock = int(inventory["Current Stock"].max()) if not inventory.empty else 100
    st.dataframe(
        df_filtered,
        use_container_width=True,
        height=320,
        column_config={
            "Current Stock": st.column_config.ProgressColumn(
                "Current Stock",
                help="Actual units available in warehouse",
                format="%d",
                min_value=0,
                max_value=max_stock,
            ),
            "Minimum Stock": st.column_config.NumberColumn("Min Safety Stock", format="%d units"),
            "Daily Sales": st.column_config.NumberColumn("Daily Velocity", format="%d units/day"),
            "Cost": st.column_config.NumberColumn("Unit Cost (INR)", format="₹%d"),
            "Warehouse": st.column_config.TextColumn("Warehouse Hub")
        }
    )

    st.markdown("---")

    # 4. Stock Allocation Charts
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("📊 Stock by Product")
        if not df_filtered.empty:
            fig1 = create_bar_chart(
                df_filtered, 
                x="Product", 
                y="Current Stock", 
                color="Category"
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("No records match filters.")

    with col_chart2:
        st.subheader("🥧 Category Distribution")
        if not df_filtered.empty:
            fig2 = create_pie_chart(df_filtered, names="Category")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No records match filters.")

    st.markdown("---")

    # 5. Low Stock & Warehouse Distribution Reports
    col_report1, col_report2 = st.columns(2)

    with col_report1:
        st.subheader("⚠️ Low Stock Items Alert")
        low_stock_df = inventory[inventory["Current Stock"] <= inventory["Minimum Stock"]]
        if not low_stock_df.empty:
            st.dataframe(
                low_stock_df, 
                use_container_width=True,
                column_config={
                    "Current Stock": st.column_config.NumberColumn("Stock", format="%d ⚠️"),
                    "Minimum Stock": st.column_config.NumberColumn("Min Buffer"),
                    "Cost": st.column_config.NumberColumn("Unit Cost", format="₹%d")
                }
            )
        else:
            st.success("✅ All stock levels are within safe operational limits.")

    with col_report2:
        st.subheader("🏭 Warehouse Distribution")
        if not inventory.empty:
            warehouse_summary = (
                inventory.groupby("Warehouse")["Current Stock"]
                .sum()
                .reset_index()
            )
            fig3 = create_bar_chart(
                warehouse_summary,
                x="Warehouse",
                y="Current Stock",
                color="Warehouse"
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("No inventory distribution records available.")
