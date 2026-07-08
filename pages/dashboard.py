import streamlit as st
import pandas as pd
from utils.metrics import get_dashboard_kpis
from utils.charts import create_bar_chart, create_pie_chart, create_scatter_plot, create_histogram
from utils.helpers import render_page_header
from ai.gemini import get_ai_response, has_api_key

def render_dashboard(
    inventory: pd.DataFrame,
    suppliers: pd.DataFrame,
    orders: pd.DataFrame,
    shipments: pd.DataFrame
) -> None:
    """
    Renders the SupplySense AI dashboard page with key metrics, charts,
    and a quick AI insight feature.
    """
    render_page_header("📦 SupplySense AI Dashboard", "AI-Powered Supply Chain Monitoring")

    # 1. Dynamic KPI Metrics
    kpis = get_dashboard_kpis(inventory, suppliers, orders, shipments)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Inventory Items", 
        kpis["inventory"]["value"], 
        kpis["inventory"]["delta"], 
        delta_color=kpis["inventory"]["delta_color"]
    )
    col2.metric(
        "Suppliers", 
        kpis["suppliers"]["value"], 
        kpis["suppliers"]["delta"], 
        delta_color=kpis["suppliers"]["delta_color"]
    )
    col3.metric(
        "Orders", 
        kpis["orders"]["value"], 
        kpis["orders"]["delta"], 
        delta_color=kpis["orders"]["delta_color"]
    )
    col4.metric(
        "Shipments", 
        kpis["shipments"]["value"], 
        kpis["shipments"]["delta"], 
        delta_color=kpis["shipments"]["delta_color"]
    )

    st.markdown("---")

    # 2. Key Charts: Inventory & Shipments
    left, right = st.columns((2, 1))

    with left:
        st.subheader("📦 Inventory Levels")
        if not inventory.empty:
            fig1 = create_bar_chart(
                inventory, 
                x="Product", 
                y="Current Stock", 
                color="Category", 
                text="Current Stock", 
                height=450
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("No inventory data loaded.")

    with right:
        st.subheader("🚚 Shipment Status")
        if not shipments.empty:
            fig2 = create_pie_chart(shipments, names="Status", height=400)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No shipment data loaded.")

    st.markdown("---")

    # 3. Secondary Charts: Suppliers & Orders
    left2, right2 = st.columns(2)

    with left2:
        st.subheader("🏭 Supplier Performance")
        if not suppliers.empty:
            fig3 = create_scatter_plot(
                suppliers,
                x="Average Delay",
                y="Rating",
                size="Cost Index",
                color="Rating",
                hover_name="Supplier",
                height=450
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("No supplier data loaded.")

    with right2:
        st.subheader("📈 Order Quantity")
        if not orders.empty:
            fig4 = create_histogram(orders, x="Quantity", height=450)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("No order data loaded.")

    st.markdown("---")

    # 4. Interactive Quick AI Insight
    st.subheader("🤖 Quick AI Insight")
    question = st.text_input(
        "Ask a quick question about your Supply Chain (e.g., 'Which products have low stock?'):",
        key="dashboard_ai_input"
    )

    if question:
        with st.spinner("AI is analyzing local data..."):
            # Fetch response combining cached local datasets as context
            response = get_ai_response(
                prompt=question,
                inventory=inventory,
                suppliers=suppliers,
                orders=orders,
                shipments=shipments
            )
            
            if has_api_key():
                st.success("🤖 **Gemini AI Response:**")
            else:
                st.info("🤖 **Local SupplySense Advisor Response:** (Demo Mode without Gemini Key)")
            
            st.write(response)
