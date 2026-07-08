import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.helpers import render_page_header, format_currency, style_status_column
from utils.charts import apply_plot_theme, THEME_COLORS

@st.cache_data(show_spinner="Running forecasting algorithms...")
def fit_forecast(historical_df: pd.DataFrame, days_to_predict: int = 30):
    """
    Fits a model to historical daily demand and predicts future demand.
    Tries Prophet, then Scikit-Learn LinearRegression, then Numpy Polyfit.
    Caches outputs to avoid running fit algorithms on every page interaction.
    """
    df = historical_df.sort_values('ds').reset_index(drop=True)
    
    if len(df) < 3:
        mean_val = df['y'].mean() if len(df) > 0 else 5.0
        future_dates = pd.date_range(start=datetime.now().date(), periods=days_to_predict, freq='D')
        forecast = pd.DataFrame({'ds': future_dates, 'yhat': [max(0.1, mean_val)] * days_to_predict})
        return forecast, "Baseline Mean (Insufficient historical points)"

    # 1. Try Prophet Time Series Forecasting
    try:
        from prophet import Prophet
        import logging
        logging.getLogger('prophet').setLevel(logging.ERROR)
        
        m = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=False)
        m.fit(df)
        
        future = m.make_future_dataframe(periods=days_to_predict, include_history=False)
        forecast_all = m.predict(future)
        forecast = forecast_all[['ds', 'yhat']].tail(days_to_predict).copy()
        forecast['yhat'] = forecast['yhat'].clip(lower=0)
        return forecast, "Prophet Time Series Model"
    except Exception:
        pass

    # 2. Try Scikit-Learn Linear Regression
    try:
        from sklearn.linear_model import LinearRegression
        
        start_date = df['ds'].min()
        df['x'] = (df['ds'] - start_date).dt.days
        X = df[['x']].values
        y = df['y'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        last_date = df['ds'].max()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_to_predict, freq='D')
        future_x = (future_dates - start_date).dt.days.values.reshape(-1, 1)
        predictions = model.predict(future_x)
        
        forecast = pd.DataFrame({'ds': future_dates, 'yhat': predictions})
        forecast['yhat'] = forecast['yhat'].clip(lower=0)
        return forecast, "Scikit-Learn Linear Regression Model"
    except Exception:
        pass

    # 3. Fallback: Numpy Polyfit Linear Regression
    start_date = df['ds'].min()
    df['x'] = (df['ds'] - start_date).dt.days
    x = df['x'].values
    y = df['y'].values
    
    slope, intercept = np.polyfit(x, y, 1)
    
    last_date = df['ds'].max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_to_predict, freq='D')
    future_x = (future_dates - start_date).dt.days.values
    predictions = slope * future_x + intercept
    
    forecast = pd.DataFrame({'ds': future_dates, 'yhat': predictions})
    forecast['yhat'] = forecast['yhat'].clip(lower=0)
    return forecast, "Numpy Heuristic Linear Model"

def render_forecast(inventory: pd.DataFrame, orders: pd.DataFrame, suppliers: pd.DataFrame) -> None:
    """
    Renders the Predictive Forecasting screen, computing demand forecasts,
    inventory depletion curves, stock-out timelines, and reorder signals.
    """
    render_page_header("📈 Predictive Forecasting & Risk Engine", "Simulate future demand curves, inventory burn rates, and replenishment triggers.")

    if inventory.empty or orders.empty:
        st.error("Missing core inventory or orders datasets. Unable to generate forecasts.")
        return

    # 1. Compile Global Stockout Risks Directory (SaaS Feel)
    st.subheader("📋 Global Risk & Replenishment Ledger")
    
    product_supplier_map = {}
    if not orders.empty:
        prod_sup = orders.groupby(["Product", "Supplier"]).size().reset_index(name="count")
        idx = prod_sup.groupby("Product")["count"].idxmax()
        typical_sups = prod_sup.loc[idx]
        product_supplier_map = dict(zip(typical_sups["Product"], typical_sups["Supplier"]))

    supplier_delay_map = {}
    if not suppliers.empty:
        supplier_delay_map = dict(zip(suppliers["Supplier"], suppliers["Average Delay"]))

    global_records = []
    for _, row in inventory.iterrows():
        prod = row["Product"]
        stock = row["Current Stock"]
        sales = row["Daily Sales"]
        
        days_remaining = np.inf if sales == 0 else stock / sales
        typical_sup = product_supplier_map.get(prod, "N/A")
        lead_time = supplier_delay_map.get(typical_sup, 4) if typical_sup != "N/A" else 4
        
        safety_stock = sales * 3
        reorder_point = (sales * lead_time) + safety_stock
        
        status = "✅ Stable"
        if stock <= safety_stock:
            status = "🚨 Stockout Imminent"
        elif stock <= reorder_point:
            status = "⚠️ Reorder Triggered"
            
        global_records.append({
            "Product": prod,
            "Category": row["Category"],
            "Current Stock": stock,
            "Daily Velocity": sales,
            "Days Remaining": round(days_remaining, 1) if days_remaining != np.inf else 999,
            "Typical Supplier": typical_sup,
            "Lead Time": lead_time,
            "Reorder Point": reorder_point,
            "Risk Status": status
        })

    global_df = pd.DataFrame(global_records)

    # Global KPI row
    reorders_needed = len(global_df[global_df["Risk Status"] != "✅ Stable"])
    critical_stockouts = len(global_df[global_df["Risk Status"] == "🚨 Stockout Imminent"])
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Catalog Checked", len(global_df))
    c2.metric("Replenishments Required", reorders_needed, delta=f"{critical_stockouts} Critical" if critical_stockouts > 0 else None, delta_color="inverse")
    c3.metric("Safety Buffer Standard", "3 Days Sales")
    
    # Calculate total value at risk
    val_at_risk = 0.0
    if not inventory.empty:
        at_risk_skus = global_df[global_df["Risk Status"] == "🚨 Stockout Imminent"]["Product"].tolist()
        val_at_risk = (inventory[inventory["Product"].isin(at_risk_skus)]["Current Stock"] * inventory[inventory["Product"].isin(at_risk_skus)]["Cost"]).sum()
    c4.metric("Capital Valuation at Risk", f"₹{val_at_risk:,.0f}")

    # Display Risk table
    color_map = {
        '✅ Stable': '#10B981',
        '⚠️ Reorder Triggered': '#F59E0B',
        '🚨 Stockout Imminent': '#EF4444'
    }
    styled_global = style_status_column(global_df, "Risk Status", color_map)

    st.dataframe(
        styled_global,
        use_container_width=True,
        height=260,
        column_config={
            "Current Stock": st.column_config.NumberColumn("Current Stock", format="%d units"),
            "Daily Velocity": st.column_config.NumberColumn("Velocity", format="%d units/day"),
            "Days Remaining": st.column_config.NumberColumn("Days remaining", format="%.1f days"),
            "Lead Time": st.column_config.NumberColumn("Lead time", format="%d days"),
            "Reorder Point": st.column_config.NumberColumn("Reorder ROP", format="%d units"),
            "Typical Supplier": st.column_config.TextColumn("Vendor Partner")
        }
    )

    st.markdown("---")

    # 2. Detailed Single SKU Simulation
    st.subheader("🔬 Single Product Demand Simulator")
    selected_prod = st.selectbox("Select SKU to Simulate and Plot", global_df["Product"].unique())

    # Get Selected specs
    prod_spec = inventory[inventory["Product"] == selected_prod].iloc[0]
    curr_stock = prod_spec["Current Stock"]
    min_stock = prod_spec["Minimum Stock"]
    unit_cost = prod_spec["Cost"]
    category = prod_spec["Category"]

    supplier_delay = 4
    typical_supplier = "Unknown Partner"
    prod_orders = orders[orders["Product"] == selected_prod]
    if not prod_orders.empty:
        typical_supplier = prod_orders["Supplier"].value_counts().idxmax()
        if not suppliers.empty:
            sup_info = suppliers[suppliers["Supplier"] == typical_supplier]
            if not sup_info.empty:
                supplier_delay = int(sup_info.iloc[0]["Average Delay"])

    # 3. Compile Historical Demand Data
    hist_orders = orders[(orders["Product"] == selected_prod) & (orders["Status"] != "Cancelled")].copy()
    hist_orders["ds"] = pd.to_datetime(hist_orders["Delivery Date"])
    daily_hist = hist_orders.groupby("ds")["Quantity"].sum().reset_index().rename(columns={"Quantity": "y"})
    
    if not daily_hist.empty:
        daily_hist = daily_hist.set_index("ds").resample("D").asfreq().fillna(0).reset_index()

    # 4. Generate 30-Day Demand Forecast (runs from cache if filters/data unchanged)
    days_to_predict = 30
    forecast, model_name = fit_forecast(daily_hist, days_to_predict)
    forecast["ds"] = pd.to_datetime(forecast["ds"])

    # 5. Simulate 30-Day Stock Depletion Trend
    inbound_orders = orders[
        (orders["Product"] == selected_prod) & 
        (orders["Status"].isin(["Pending", "Shipped", "Processing"]))
    ].copy()
    inbound_orders["ds"] = pd.to_datetime(inbound_orders["Delivery Date"])

    sim_dates = [datetime.now().date() + timedelta(days=i) for i in range(days_to_predict + 1)]
    sim_stock = []
    inbound_triggers = {}

    current_sim_stock = curr_stock
    sim_stock.append(current_sim_stock)

    for i in range(1, days_to_predict + 1):
        target_date = sim_dates[i]
        
        yhat_row = forecast[forecast["ds"].dt.date == target_date]
        daily_demand = yhat_row["yhat"].values[0] if not yhat_row.empty else prod_spec["Daily Sales"]
        
        current_sim_stock = max(0, current_sim_stock - daily_demand)
        
        matching_inbound = inbound_orders[inbound_orders["ds"].dt.date == target_date]
        if not matching_inbound.empty:
            total_arrival = matching_inbound["Quantity"].sum()
            current_sim_stock += total_arrival
            inbound_triggers[target_date] = total_arrival
            
        sim_stock.append(current_sim_stock)

    # 6. Risk Threshold Calculations
    safety_days = None
    stockout_days = None
    
    for i, stock in enumerate(sim_stock):
        if safety_days is None and stock <= min_stock:
            safety_days = i
        if stockout_days is None and stock <= 0:
            stockout_days = i
            break

    reorder_days = None
    if stockout_days is not None:
        reorder_days = max(0, stockout_days - supplier_delay)
    elif safety_days is not None:
        reorder_days = max(0, safety_days - supplier_delay)

    # Metric Row
    col_sim1, col_sim2, col_sim3, col_sim4 = st.columns(4)
    
    risk_label = "🚨 Stockout Imminent" if stockout_days is not None and stockout_days <= 7 else "✅ Safe"
    if stockout_days is not None:
        col_sim1.metric("Stock-out Risk", risk_label, f"Day {stockout_days} runout", delta_color="inverse")
    else:
        col_sim1.metric("Stock-out Risk", risk_label, "No stockout projected", delta_color="normal")
        
    if reorder_days is not None:
        col_sim2.metric("Days to Reorder Target", f"{reorder_days} Days", f"Lead Time: {supplier_delay}d", delta_color="inverse")
    else:
        col_sim2.metric("Days to Reorder Target", "N/A", "Stock levels stable")
        
    if safety_days is not None:
        col_sim3.metric("Days to Safety Min", f"{safety_days} Days", f"Min stock: {min_stock} units", delta_color="inverse")
    else:
        col_sim3.metric("Days to Safety Min", "Safe", "Stays above minimum safety limit")

    col_sim4.metric("Engine Selected", model_name.split()[0], model_name)

    st.markdown("---")

    # 7. Render Plots
    left_plot, right_plot = st.columns(2)

    with left_plot:
        st.write("#### 📈 Historical vs Projected Demand")
        fig_demand = go.Figure()
        
        if not daily_hist.empty:
            fig_demand.add_trace(go.Scatter(
                x=daily_hist["ds"],
                y=daily_hist["y"],
                mode="markers",
                name="Historical Order Qty",
                marker=dict(color=THEME_COLORS["secondary"], size=6)
            ))
            
        fig_demand.add_trace(go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat"],
            mode="lines",
            name="Forecasted Demand",
            line=dict(color=THEME_COLORS["primary"], width=3)
        ))
        
        fig_demand.update_layout(xaxis_title="Date", yaxis_title="Quantity Shipped (Units)", height=350)
        fig_demand = apply_plot_theme(fig_demand)
        st.plotly_chart(fig_demand, use_container_width=True)

    with right_plot:
        st.write("#### 📉 Projected Stock Depletion Curve")
        fig_inv = go.Figure()
        
        sim_datetimes = [datetime.now() + timedelta(days=i) for i in range(days_to_predict + 1)]
        
        fig_inv.add_trace(go.Scatter(
            x=sim_datetimes,
            y=sim_stock,
            mode="lines+markers",
            name="Projected Stock Level",
            line=dict(color=THEME_COLORS["primary"], width=3)
        ))
        
        fig_inv.add_trace(go.Scatter(
            x=sim_datetimes,
            y=[min_stock] * len(sim_datetimes),
            mode="lines",
            name="Safety Stock (Min Required)",
            line=dict(color=THEME_COLORS["accent"], dash="dash")
        ))
        
        for target_date, qty in inbound_triggers.items():
            arrival_dt = datetime.combine(target_date, datetime.min.time())
            idx = (target_date - datetime.now().date()).days
            y_val = sim_stock[idx] if idx < len(sim_stock) else curr_stock
            
            fig_inv.add_annotation(
                x=arrival_dt,
                y=y_val,
                text=f"+{qty} units",
                showarrow=True,
                arrowhead=1,
                arrowcolor="white",
                ax=-20,
                ay=-30,
                font=dict(color="white")
            )
            
        fig_inv.update_layout(xaxis_title="Simulation Date", yaxis_title="Stock in Warehouse (Units)", height=350)
        fig_inv = apply_plot_theme(fig_inv)
        st.plotly_chart(fig_inv, use_container_width=True)

    st.markdown("---")

    # 8. Weekly Forecast table
    st.subheader("📅 Weekly Demand Aggregations")
    weekly_forecast = forecast.copy()
    weekly_forecast["Week"] = weekly_forecast["ds"].dt.isocalendar().week
    weekly_forecast["Week_Label"] = "Week " + (weekly_forecast["ds"].dt.isocalendar().week - weekly_forecast["ds"].dt.isocalendar().week.min() + 1).astype(str)
    
    weekly_summary = weekly_forecast.groupby("Week_Label")[["yhat"]].agg(["sum", "mean"]).reset_index()
    weekly_summary.columns = ["Forecast Week", "Estimated Total Demand (Units)", "Est. Daily Demand (Units/Day)"]
    weekly_summary["Estimated Total Demand (Units)"] = weekly_summary["Estimated Total Demand (Units)"].round(1)
    weekly_summary["Est. Daily Demand (Units/Day)"] = weekly_summary["Est. Daily Demand (Units/Day)"].round(2)
    
    st.table(weekly_summary)

    # 9. Plain English summary writeout
    st.subheader("📝 Executive Summary & Risks Analysis")
    
    mean_demand = forecast["yhat"].mean()
    est_monthly = forecast["yhat"].sum()
    
    narrative_list = [
        f"For SKU **{selected_prod}** (Category: *{category}*), the predictive model **({model_name})** projects a future baseline demand averaging **{mean_demand:.2f} units per day**, translating to a total monthly consumption of **{est_monthly:.1f} units**.",
        f"The current stock level is **{curr_stock} units**. The minimum target safety buffer is set at **{min_stock} units**."
    ]

    if curr_stock <= min_stock:
        narrative_list.append(f"❌ **Alert:** Current stock is already breaching the safety threshold limit of **{min_stock} units**.")
    elif safety_days is not None:
        safety_date = (datetime.now() + timedelta(days=safety_days)).strftime("%B %d, %Y")
        narrative_list.append(f"⚠️ **Warning:** Projected stock will deplete below the safety limit of **{min_stock} units** on **Day {safety_days} ({safety_date})**.")
    else:
        narrative_list.append("✅ **Stability:** Projected inventory levels will remain securely above the minimum safety limit throughout the 30-day timeline.")

    if stockout_days is not None:
        stockout_date = (datetime.now() + timedelta(days=stockout_days)).strftime("%B %d, %Y")
        narrative_list.append(f"🚨 **Critical Risk:** Full stock exhaustion (0 stock) is projected on **Day {stockout_days} ({stockout_date})**.")
        if reorder_days is not None and reorder_days > 0:
            reorder_date = (datetime.now() + timedelta(days=reorder_days)).strftime("%B %d, %Y")
            narrative_list.append(f"⏰ **Action Required:** To prevent a stockout, order replacement stock by **Day {reorder_days} ({reorder_date})**, factoring in **{typical_supplier}**'s average lead time delay of **{supplier_delay} days**.")
        else:
            narrative_list.append(f"⏰ **Immediate Action Required:** Order replenishment stock immediately. Lead time ({supplier_delay} days) exceeds projected runout.")
    else:
        narrative_list.append("✅ **Zero Stockout Risk:** Projected inbound shipments and current stock levels are sufficient to cover daily sales demand for the next month.")

    if not inbound_orders.empty:
        total_inbound = inbound_orders["Quantity"].sum()
        narrative_list.append(f"📦 **Inbound Logistics:** There are {len(inbound_orders)} active inbound orders totaling **{total_inbound} units** scheduled to arrive, which are mapped in the simulation curve.")

    if stockout_days is not None:
        procurement_cost = (min_stock * 2) * unit_cost
        narrative_list.append(f"💡 **Procurement Advice:** We suggest creating a purchase requisition for **{min_stock * 2} units** from typical supplier **{typical_supplier}**. Est. requisition budget: {format_currency(procurement_cost)}.")

    st.write("\n\n".join(narrative_list))
