import streamlit as st
import pandas as pd
from utils.helpers import render_page_header, format_currency
import io

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Converts a pandas DataFrame to a CSV byte string for download."""
    return df.to_csv(index=False).encode('utf-8')

def render_reports(
    inventory: pd.DataFrame,
    suppliers: pd.DataFrame,
    orders: pd.DataFrame,
    shipments: pd.DataFrame
) -> None:
    """
    Renders the Reports and Audit Export page, permitting users to download
    summarized and raw datasets.
    """
    render_page_header("📈 Supply Chain Audit & Reports", "Generate reports and export data from your supply chain.")

    st.subheader("📁 Generate Report Summary")
    report_type = st.selectbox(
        "Choose Report Classification",
        [
            "Inventory Allocation Summary",
            "Supplier Quality & Delay Performance",
            "Customer Fulfillment & Orders Ledger",
            "Logistics Cost & Route Analysis"
        ]
    )

    st.markdown("---")

    if report_type == "Inventory Allocation Summary":
        st.subheader("📋 Inventory Allocation Audit Report")
        if inventory.empty:
            st.warning("No inventory records loaded.")
            return

        total_value = (inventory["Current Stock"] * inventory["Cost"]).sum()
        avg_cost = inventory["Cost"].mean()
        low_stock_items = len(inventory[inventory["Current Stock"] <= inventory["Minimum Stock"]])

        st.markdown(f"""
        ### Executive Inventory Summary
        *   **Total Catalog Items:** {len(inventory)}
        *   **Total Inventory Valuation:** {format_currency(total_value)}
        *   **Average Product Unit Cost:** {format_currency(avg_cost)}
        *   **Out of Stock / Critical Low Stock count:** **{low_stock_items}**
        """)

        st.write("#### Category Valuation Breakdown")
        cat_breakdown = inventory.copy()
        cat_breakdown["Valuation"] = cat_breakdown["Current Stock"] * cat_breakdown["Cost"]
        summary_table = (
            cat_breakdown.groupby("Category")[["Current Stock", "Valuation"]]
            .sum()
            .reset_index()
            .sort_values(by="Valuation", ascending=False)
        )
        summary_table["Valuation"] = summary_table["Valuation"].map(lambda x: format_currency(x))
        st.table(summary_table)

        # Download button
        csv_data = convert_df_to_csv(inventory)
        st.download_button(
            label="📥 Export Raw Inventory dataset (.csv)",
            data=csv_data,
            file_name="inventory_report.csv",
            mime="text/csv"
        )

    elif report_type == "Supplier Quality & Delay Performance":
        st.subheader("📋 Supplier Audit & Performance Report")
        if suppliers.empty:
            st.warning("No supplier records loaded.")
            return

        avg_rating = suppliers["Rating"].mean()
        avg_delay = suppliers["Average Delay"].mean()
        avg_defect = suppliers["Defect Rate"].mean()

        st.markdown(f"""
        ### Executive Supplier Summary
        *   **Active Supplier Partners:** {len(suppliers)}
        *   **Average Supplier Rating:** {avg_rating:.2f} / 5.0 ⭐
        *   **Average Supplier Lead Time / Delay:** {avg_delay:.1f} Days
        *   **Average Defect Rate Percentage:** {avg_defect:.2f}%
        """)

        st.write("#### Location Performance Breakdown")
        loc_breakdown = (
            suppliers.groupby("Location")[["Rating", "Average Delay", "Defect Rate"]]
            .mean()
            .reset_index()
            .sort_values(by="Rating", ascending=False)
        )
        st.dataframe(loc_breakdown, use_container_width=True)

        csv_data = convert_df_to_csv(suppliers)
        st.download_button(
            label="📥 Export Raw Supplier dataset (.csv)",
            data=csv_data,
            file_name="supplier_report.csv",
            mime="text/csv"
        )

    elif report_type == "Customer Fulfillment & Orders Ledger":
        st.subheader("📋 Order Ledger & Delivery Status")
        if orders.empty:
            st.warning("No order records loaded.")
            return

        total_orders = len(orders)
        delivered = len(orders[orders["Status"] == "Delivered"])
        shipped = len(orders[orders["Status"] == "Shipped"])
        pending = len(orders[orders["Status"] == "Pending"])
        cancelled = len(orders[orders["Status"] == "Cancelled"])
        fulfillment_rate = (delivered / total_orders) * 100 if total_orders > 0 else 0.0

        st.markdown(f"""
        ### Executive Order Summary
        *   **Total Transactions Processed:** {total_orders}
        *   **Successful Deliveries:** {delivered} (Fulfillment Rate: **{fulfillment_rate:.1f}%**)
        *   **In-Transit Orders:** {shipped}
        *   **Pending Queue:** {pending}
        *   **Cancelled Orders:** {cancelled}
        """)

        st.write("#### Order Status Overview")
        status_tbl = orders["Status"].value_counts().reset_index()
        status_tbl.columns = ["Fulfillment Status", "Volume Count"]
        st.table(status_tbl)

        csv_data = convert_df_to_csv(orders)
        st.download_button(
            label="📥 Export Raw Orders ledger (.csv)",
            data=csv_data,
            file_name="orders_report.csv",
            mime="text/csv"
        )

    elif report_type == "Logistics Cost & Route Analysis":
        st.subheader("📋 Logistics Cost & Route Analysis Report")
        if shipments.empty:
            st.warning("No shipment records loaded.")
            return

        total_fuel = shipments["Fuel Cost"].sum()
        total_distance = shipments["Distance"].sum()
        avg_delay = shipments["Delay"].mean()

        st.markdown(f"""
        ### Executive Logistics Summary
        *   **Completed Logistical Routes:** {len(shipments)}
        *   **Cumulative Transit Distance:** {total_distance:,} km
        *   **Total Fuel Surcharge Expenses:** {format_currency(total_fuel)}
        *   **Average Dispatch Transit Delay:** {avg_delay:.1f} Days
        """)

        st.write("#### Regional Route Efficiency Breakdown")
        route_efficiency = (
            shipments.groupby("Route")[["Distance", "Fuel Cost", "Delay"]]
            .agg({"Distance": "sum", "Fuel Cost": "sum", "Delay": "mean"})
            .reset_index()
            .sort_values(by="Fuel Cost", ascending=False)
        )
        route_efficiency["Fuel Cost"] = route_efficiency["Fuel Cost"].map(lambda x: format_currency(x))
        st.dataframe(route_efficiency, use_container_width=True)

        csv_data = convert_df_to_csv(shipments)
        st.download_button(
            label="📥 Export Raw Logistics dataset (.csv)",
            data=csv_data,
            file_name="logistics_report.csv",
            mime="text/csv"
        )
