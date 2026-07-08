import streamlit as st
import pandas as pd
from utils.metrics import get_order_metrics
from utils.charts import create_bar_chart, create_pie_chart
from utils.helpers import render_page_header, style_status_column

def render_orders(orders: pd.DataFrame) -> None:
    """
    Renders the Customer Orders tracking page with filters and fulfillment status.
    """
    render_page_header("🛒 Customer Orders Ledger", "Monitor customer order queues, quantities, and delivery status.")

    if orders.empty:
        st.error("No orders found. Please check orders.csv.")
        return

    # 1. Orders KPIs
    stats = get_order_metrics(orders)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Bookings", stats["total"])
    col2.metric("Pending Queue", stats["pending"])
    col3.metric("Shipped In Transit", stats["shipped"])
    col4.metric("Delivered Orders", stats["delivered"])
    col5.metric("Cancelled Volume", stats["cancelled"])

    st.markdown("---")

    # 2. Filters Row
    left, middle, right = st.columns([1.5, 1.5, 1])
    with left:
        search_customer = st.text_input("🔍 Search Customer Name", placeholder="Customer_...")
    with middle:
        search_product = st.text_input("🔍 Search Product Name", placeholder="Product_...")
    with right:
        status_options = ["All"] + sorted(orders["Status"].unique().tolist())
        status = st.selectbox("Status Filter", status_options)

    # 3. Filter DataFrame
    df_filtered = orders.copy()
    if search_customer:
        df_filtered = df_filtered[df_filtered["Customer"].str.contains(search_customer, case=False)]
    if search_product:
        df_filtered = df_filtered[df_filtered["Product"].str.contains(search_product, case=False)]
    if status != "All":
        df_filtered = df_filtered[df_filtered["Status"] == status]

    # Show data directory with status badge highlights
    st.subheader("📋 Orders Registry")
    
    color_map = {
        'Delivered': '#10B981',
        'Shipped': '#38BDF8',
        'Pending': '#F59E0B',
        'Processing': '#F59E0B',
        'Cancelled': '#EF4444'
    }
    
    styled_df = style_status_column(df_filtered, "Status", color_map)
    st.dataframe(styled_df, use_container_width=True, height=280)

    st.markdown("---")

    # 4. Visualization Charts
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("🥧 Order Status Distribution")
        if not df_filtered.empty:
            fig1 = create_pie_chart(df_filtered, names="Status")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("No records to visualize.")

    with col_chart2:
        st.subheader("📊 Orders Volume by Product Category")
        if not df_filtered.empty:
            category_totals = df_filtered.groupby("Product")["Quantity"].sum().reset_index()
            fig2 = create_bar_chart(category_totals, x="Product", y="Quantity", color="Product")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No records to visualize.")
