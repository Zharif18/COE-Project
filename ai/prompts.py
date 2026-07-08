# Prompt templates and context serialization for SupplySense AI

SYSTEM_PROMPT = """
You are "SupplySense AI Coach", an expert Supply Chain Architect and Conversational Advisor.
Your role is to assist logistics manager users in auditing operations, predicting inventory bottlenecks, and advising on supplier procurement strategies.

Operational Rules:
1. Always base your calculations, warnings, and answers on the live Data Context provided below.
2. Be highly specific: mention exact product names, warehouses, supplier IDs, defect rates, and routes.
3. Keep answers concise, actionable, and formatted in clean markdown tables or bullet points.
4. If a metric cannot be deduced from the data tables, say "Data not available" instead of speculating.
5. In addition to answering the prompt, suggest 1 proactive recommendation based on supply chain logic (e.g., "Recommend ordering Webcam-4 from Supplier_002 instead of Supplier_008 due to 2% lower defect rates").

Use standard emoji bullet points for clarity.
"""

def serialize_csv_context(inventory, suppliers, orders, shipments) -> str:
    """
    Serializes pandas DataFrames into a dense, structured, and descriptive text block
    to supply the LLM with all metrics needed for forecasting and auditing.
    """
    summary = []
    
    # 1. INVENTORY SUMMARY
    if not inventory.empty:
        total_skus = len(inventory)
        total_value = (inventory["Current Stock"] * inventory["Cost"]).sum()
        low_stock_df = inventory[inventory["Current Stock"] <= inventory["Minimum Stock"]]
        low_stock_list = []
        for _, r in low_stock_df.iterrows():
            runout_days = r["Current Stock"] / r["Daily Sales"] if r["Daily Sales"] > 0 else float('inf')
            low_stock_list.append(
                f"- SKU: {r['Product']} | Category: {r['Category']} | Current Stock: {r['Current Stock']} (Min req: {r['Minimum Stock']}) | Daily Sales: {r['Daily Sales']} | Est. Runout: {runout_days:.1f} days | Warehouse: {r['Warehouse']}"
            )
            
        summary.append("--- INVENTORY HEALTH SUMMARY ---")
        summary.append(f"- Total active SKUs: {total_skus}")
        summary.append(f"- Total Stock Valuation: ₹{total_value:,.2f}")
        summary.append(f"- Low Stock Alert Count: {len(low_stock_df)}")
        if low_stock_list:
            summary.append("Active Low Stock Items Details:")
            summary.extend(low_stock_list[:15])  # Top 15 critical items to avoid prompt bloat
        else:
            summary.append("- All items have sufficient stock levels.")
        summary.append("")

    # 2. SUPPLIER QUALITY SUMMARY
    if not suppliers.empty:
        total_partners = len(suppliers)
        avg_rating = suppliers["Rating"].mean()
        avg_delay = suppliers["Average Delay"].mean()
        avg_defect = suppliers["Defect Rate"].mean()
        
        # Sort to find outliers
        best_supplier = suppliers.sort_values(by=["Rating", "Average Delay"], ascending=[False, True]).iloc[0]
        worst_supplier = suppliers.sort_values(by=["Rating", "Defect Rate"], ascending=[True, False]).iloc[0]
        
        summary.append("--- SUPPLIER PERFORMANCE SUMMARY ---")
        summary.append(f"- Active Supplier Partners: {total_partners}")
        summary.append(f"- Average Rating: {avg_rating:.2f} / 5.0")
        summary.append(f"- Average Dispatch Delay: {avg_delay:.1f} days")
        summary.append(f"- Average Defect Rate: {avg_defect:.2f}%")
        summary.append(f"- Most Reliable Supplier (Best Rating/Delay): {best_supplier['Supplier']} (Rating: {best_supplier['Rating']} ★, Avg Delay: {best_supplier['Average Delay']}d, Location: {best_supplier['Location']})")
        summary.append(f"- Lowest Rated Supplier: {worst_supplier['Supplier']} (Rating: {worst_supplier['Rating']} ★, Defect Rate: {worst_supplier['Defect Rate']}%, Avg Delay: {worst_supplier['Average Delay']}d)")
        summary.append("")

    # 3. ORDER QUEUES SUMMARY
    if not orders.empty:
        total_orders = len(orders)
        status_counts = orders["Status"].value_counts().to_dict()
        pending_count = status_counts.get("Pending", 0)
        processing_count = status_counts.get("Processing", 0)
        shipped_count = status_counts.get("Shipped", 0)
        cancelled_count = status_counts.get("Cancelled", 0)
        
        summary.append("--- ORDER QUEUE & FULFILLMENT STATUS ---")
        summary.append(f"- Total Orders Processed: {total_orders}")
        summary.append(f"- Pending: {pending_count} | Processing: {processing_count} | Shipped: {shipped_count} | Cancelled: {cancelled_count}")
        
        # Details on pending/processing orders
        unfulfilled = orders[orders["Status"].isin(["Pending", "Processing"])]
        if not unfulfilled.empty:
            summary.append("Critical Unfulfilled Orders Ledger:")
            for _, r in unfulfilled.head(10).iterrows():
                summary.append(f"  * Order {r['Order ID']} for {r['Customer']} | Item: {r['Product']} | Qty: {r['Quantity']} | Status: {r['Status']} | Delivery: {r['Delivery Date']} | Supplier: {r['Supplier']}")
        summary.append("")

    # 4. LOGISTICS & TRANSHIPS SUMMARY
    if not shipments.empty:
        total_shipments = len(shipments)
        delayed_shipments_df = shipments[shipments["Status"] == "Delayed"]
        delayed_count = len(delayed_shipments_df)
        route_fuel = shipments.groupby("Route")["Fuel Cost"].sum().to_dict()
        route_delays = shipments.groupby("Route")["Delay"].mean().to_dict()
        
        summary.append("--- LOGISTICS & TRANSIT SUMMARY ---")
        summary.append(f"- Active Shipments: {total_shipments}")
        summary.append(f"- Delayed Shipments: {delayed_count}")
        
        if delayed_count > 0:
            summary.append("List of Delayed Shipments:")
            for _, r in delayed_shipments_df.head(10).iterrows():
                summary.append(f"  * Shipment {r['Shipment ID']} | Route: {r['Route']} | Distance: {r['Distance']}km | Delay: {r['Delay']} days | Fuel Cost: ₹{r['Fuel Cost']}")
                
        summary.append("Regional Fuel Surcharge distribution:")
        for r, f in route_fuel.items():
            avg_d = route_delays.get(r, 0)
            summary.append(f"  * Region: {r} | Total Fuel: ₹{f:,.2f} | Avg Transit Delay: {avg_d:.1f} days")
        summary.append("")

    return "\n".join(summary)
