import pandas as pd
from typing import Dict, Any

def get_dashboard_kpis(
    inventory: pd.DataFrame,
    suppliers: pd.DataFrame,
    orders: pd.DataFrame,
    shipments: pd.DataFrame
) -> Dict[str, Dict[str, Any]]:
    """
    Calculates dynamic KPI values and status deltas for the dashboard view.

    Returns:
        Dict: A dictionary containing metrics and their display deltas/labels.
    """
    # 1. Inventory Metric
    inv_count = len(inventory)
    low_stock_count = 0
    if not inventory.empty:
        low_stock_count = len(inventory[inventory["Current Stock"] <= inventory["Minimum Stock"]])
        inv_delta = f"{low_stock_count} Low Stock"
    else:
        inv_delta = "No data"

    # 2. Suppliers Metric
    sup_count = len(suppliers)
    if not suppliers.empty:
        avg_rating = suppliers["Rating"].mean()
        sup_delta = f"Avg Rating: {avg_rating:.1f} ★"
    else:
        sup_delta = "No data"

    # 3. Orders Metric
    ord_count = len(orders)
    if not orders.empty:
        pending_orders = len(orders[orders["Status"] == "Pending"])
        ord_delta = f"{pending_orders} Pending"
    else:
        ord_delta = "No data"

    # 4. Shipments Metric
    ship_count = len(shipments)
    if not shipments.empty:
        delayed_ships = len(shipments[shipments["Status"] == "Delayed"])
        ship_delta = f"{delayed_ships} Delayed"
    else:
        ship_delta = "No data"

    return {
        "inventory": {"value": inv_count, "delta": inv_delta, "delta_color": "inverse" if low_stock_count > 0 else "normal"},
        "suppliers": {"value": sup_count, "delta": sup_delta, "delta_color": "normal"},
        "orders": {"value": ord_count, "delta": ord_delta, "delta_color": "normal"},
        "shipments": {"value": ship_count, "delta": ship_delta, "delta_color": "inverse" if delayed_ships > 0 else "normal"},
    }

def get_inventory_metrics(inventory: pd.DataFrame) -> Dict[str, Any]:
    """Calculates granular inventory metrics."""
    if inventory.empty:
        return {"total_items": 0, "low_stock": 0, "avg_stock": 0.0, "warehouses": 0, "total_value": 0.0}
        
    low_stock = len(inventory[inventory["Current Stock"] <= inventory["Minimum Stock"]])
    avg_stock = inventory["Current Stock"].mean()
    warehouses = inventory["Warehouse"].nunique()
    total_value = (inventory["Current Stock"] * inventory["Cost"]).sum()
    
    return {
        "total_items": len(inventory),
        "low_stock": low_stock,
        "avg_stock": round(avg_stock, 1),
        "warehouses": warehouses,
        "total_value": total_value
    }

def get_supplier_metrics(suppliers: pd.DataFrame) -> Dict[str, Any]:
    """Calculates granular supplier performance metrics."""
    if suppliers.empty:
        return {"total": 0, "avg_rating": 0.0, "avg_delay": 0.0, "avg_defect_rate": 0.0}
        
    return {
        "total": len(suppliers),
        "avg_rating": round(suppliers["Rating"].mean(), 2),
        "avg_delay": round(suppliers["Average Delay"].mean(), 1),
        "avg_defect_rate": round(suppliers["Defect Rate"].mean(), 2)
    }

def get_shipment_metrics(shipments: pd.DataFrame) -> Dict[str, Any]:
    """Calculates logistics and shipment metrics."""
    if shipments.empty:
        return {"total": 0, "delayed": 0, "in_transit": 0, "fuel_cost": 0.0, "avg_distance": 0.0}
        
    return {
        "total": len(shipments),
        "delayed": len(shipments[shipments["Status"] == "Delayed"]),
        "in_transit": len(shipments[shipments["Status"] == "In Transit"]),
        "fuel_cost": shipments["Fuel Cost"].sum(),
        "avg_distance": round(shipments["Distance"].mean(), 1)
    }

def get_order_metrics(orders: pd.DataFrame) -> Dict[str, Any]:
    """Calculates order fulfillment metrics."""
    if orders.empty:
        return {"total": 0, "pending": 0, "shipped": 0, "delivered": 0, "cancelled": 0, "qty": 0}
        
    return {
        "total": len(orders),
        "pending": len(orders[orders["Status"] == "Pending"]),
        "shipped": len(orders[orders["Status"] == "Shipped"]),
        "delivered": len(orders[orders["Status"] == "Delivered"]),
        "cancelled": len(orders[orders["Status"] == "Cancelled"]),
        "qty": orders["Quantity"].sum()
    }
