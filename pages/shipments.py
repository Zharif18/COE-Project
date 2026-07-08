import streamlit as st
import pandas as pd
from utils.metrics import get_shipment_metrics
from utils.charts import create_bar_chart, create_pie_chart, create_scatter_plot
from utils.helpers import render_page_header, format_short_currency, style_status_column

def render_shipments(shipments: pd.DataFrame) -> None:
    """
    Renders the Shipments Logistics and Tracking page with status distribution,
    route analysis, delays, and fuel expenses.
    """
    render_page_header("🚚 Shipments & Logistics", "Track delivery status, routes, fuel expenses, and delays.")

    if shipments.empty:
        st.error("No shipment records found. Please check shipments.csv.")
        return

    # 1. Logistics KPIs
    stats = get_shipment_metrics(shipments)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Shipments", stats["total"])
    col2.metric("In Transit", stats["in_transit"])
    col3.metric("Delayed Shipments", stats["delayed"], delta="Requires attention" if stats["delayed"] > 0 else "Optimal", delta_color="inverse")
    col4.metric("Total Fuel Cost", format_short_currency(stats["fuel_cost"]))

    st.markdown("---")

    # 2. Filters Row
    left, right = st.columns(2)
    with left:
        route_options = ["All"] + sorted(shipments["Route"].unique().tolist())
        route = st.selectbox("Filter by Route Region", route_options)
    with right:
        status_options = ["All"] + sorted(shipments["Status"].unique().tolist())
        status = st.selectbox("Filter by Delivery Status", status_options)

    # 3. Filter DataFrame
    df_filtered = shipments.copy()
    if route != "All":
        df_filtered = df_filtered[df_filtered["Route"] == route]
    if status != "All":
        df_filtered = df_filtered[df_filtered["Status"] == status]

    # Show data directory with custom columns and status highlights
    st.subheader("📋 Logistics Audit Ledger")
    
    color_map = {
        'Delivered': '#10B981',
        'In Transit': '#38BDF8',
        'Pending': '#F59E0B',
        'Delayed': '#EF4444'
    }
    
    styled_df = style_status_column(df_filtered, "Status", color_map)

    st.dataframe(
        styled_df, 
        use_container_width=True, 
        height=280,
        column_config={
            "Distance": st.column_config.NumberColumn("Distance", format="%d km"),
            "Fuel Cost": st.column_config.NumberColumn("Fuel Surcharge", format="₹%d"),
            "Delay": st.column_config.NumberColumn("Delay Time", format="%d days"),
            "Shipment Date": st.column_config.TextColumn("Dispatch Date"),
            "Route": st.column_config.TextColumn("Transit Route")
        }
    )

    st.markdown("---")

    # 4. Graphs Section
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("📊 Fuel Cost Allocation by Route")
        if not df_filtered.empty:
            fuel_summary = df_filtered.groupby("Route")["Fuel Cost"].sum().reset_index()
            fig1 = create_bar_chart(fuel_summary, x="Route", y="Fuel Cost", color="Route")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("No records to visualize.")

    with col_chart2:
        st.subheader("🥧 Delivery Route Allocation")
        if not df_filtered.empty:
            fig2 = create_pie_chart(df_filtered, names="Route")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No records to visualize.")
            
    st.markdown("---")
    
    # 5. Delay vs Distance analysis scatter plot
    st.subheader("📈 Route Distance vs Delivery Delay Analysis")
    if not df_filtered.empty:
        fig3 = create_scatter_plot(
            df_filtered,
            x="Distance",
            y="Delay",
            color="Status",
            hover_name="Shipment ID",
            height=450
        )
        st.plotly_chart(fig3, use_container_width=True)
