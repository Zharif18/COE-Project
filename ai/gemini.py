import os
import streamlit as st
import google.generativeai as genai
import pandas as pd
from typing import Optional
from dotenv import load_dotenv
from ai.prompts import SYSTEM_PROMPT, serialize_csv_context

# Load environment variables from .env file
load_dotenv()

def get_api_key() -> Optional[str]:
    """Retrieves the Gemini API key from session state, secrets, or environment variables."""
    # 1. Check Streamlit Session State (entered dynamically in UI)
    if "gemini_api_key" in st.session_state and st.session_state["gemini_api_key"]:
        return st.session_state["gemini_api_key"]
        
    # 2. Check Streamlit Secrets
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
        
    # 3. Check System Environment variables (including those loaded from .env)
    return os.getenv("GEMINI_API_KEY")

def has_api_key() -> bool:
    """Returns True if a Gemini API key is configured."""
    key = get_api_key()
    return key is not None and len(key.strip()) > 0

def query_gemini_api(prompt: str, context: str, api_key: str) -> str:
    """
    Invokes the Google Gemini API with system prompts.
    Handles rate-limiting, authentication failures, and connection drops gracefully.
    """
    try:
        # Configure client safely
        genai.configure(api_key=api_key)
        
        # Use the standard gemini-2.5-flash model
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        full_prompt = f"{SYSTEM_PROMPT}\n\n### Data Context\n{context}\n\n### User Question\n{prompt}"
        response = model.generate_content(full_prompt)
        
        if response and response.text:
            return response.text
        return "⚠️ Gemini API returned an empty response. Please try again."
        
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "API key not valid" in error_msg:
            return "❌ **Authentication Failure:** The provided Gemini API Key is invalid. Please verify your credentials."
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            return "❌ **Rate Limit Exceeded:** You have exceeded your Gemini free quota. Please wait a minute or upgrade your key."
        return f"⚠️ **Gemini API Error:** {error_msg}. (Temporarily switching to Local Heuristics Advisor)"

def local_heuristic_fallback(
    prompt: str, 
    inventory: pd.DataFrame, 
    suppliers: pd.DataFrame, 
    orders: pd.DataFrame, 
    shipments: pd.DataFrame
) -> str:
    """
    Analyzes user queries locally using pandas filters when no Gemini API Key is available
    or if API connection fails.
    """
    query = prompt.lower()
    
    # 1. Low stock / restocking questions
    if any(k in query for k in ["low stock", "out of stock", "stockout", "restock", "reorder"]):
        if inventory.empty:
            return "Unable to parse inventory: data file is empty."
        low_stock = inventory[inventory["Current Stock"] <= inventory["Minimum Stock"]]
        if not low_stock.empty:
            items = []
            for _, r in low_stock.iterrows():
                runout = r["Current Stock"] / r["Daily Sales"] if r["Daily Sales"] > 0 else float('inf')
                items.append(f"*   🚨 **{r['Product']}** (Stock: {r['Current Stock']} / Min: {r['Minimum Stock']}) | Warehouse: {r['Warehouse']} | Runout: {runout:.1f} days")
            return "### 📦 Critical Restocking Alerts (Calculated Offline)\n" + "\n".join(items) + "\n\n**Action Recommendation:** Place orders with high-performing suppliers immediately."
        else:
            return "### ✅ Stock Levels Healthy\nAll products are currently stocked above minimum threshold limits."

    # 2. Supplier questions
    elif any(k in query for k in ["supplier", "reliable", "defect", "lead time"]):
        if suppliers.empty:
            return "Unable to parse suppliers: data file is empty."
        best_supplier = suppliers.sort_values(by=["Rating", "Average Delay"], ascending=[False, True]).iloc[0]
        worst_supplier = suppliers.sort_values(by=["Rating", "Defect Rate"], ascending=[True, False]).iloc[0]
        return f"""### 🏭 Supplier Reliability Metrics (Calculated Offline)
*   **🏆 Most Reliable Partner:** **{best_supplier['Supplier']}** (Rating: {best_supplier['Rating']} ★ | Avg Delay: {best_supplier['Average Delay']} days | Location: {best_supplier['Location']})
*   **⚠️ Risk Warning:** **{worst_supplier['Supplier']}** has the lowest rating of **{worst_supplier['Rating']} ★** with a defect rate of **{worst_supplier['Defect Rate']}%**.
*   **Operational Delay average:** {suppliers['Average Delay'].mean():.1f} days.
"""

    # 3. Shipment delay questions
    elif any(k in query for k in ["shipment", "transit", "delay", "route"]):
        if shipments.empty:
            return "Unable to parse shipments: data file is empty."
        delayed = shipments[shipments["Status"] == "Delayed"]
        if not delayed.empty:
            items = []
            for _, r in delayed.iterrows():
                items.append(f"*   🚚 **Shipment {r['Shipment ID']}** (Route: {r['Route']}) | Distance: {r['Distance']} km | Delay: {r['Delay']} days")
            return "### 🚨 Active Logistics Delays (Calculated Offline)\n" + "\n".join(items)
        else:
            return "### ✅ Logistics Running Smoothly\nAll active shipments are currently 'In Transit' or 'Delivered' on schedule."

    # 4. Weekly reports/summaries questions
    elif any(k in query for k in ["report", "weekly", "health", "summarize", "trends", "risk"]):
        total_value = 0.0
        low_stock_count = 0
        if not inventory.empty:
            total_value = (inventory["Current Stock"] * inventory["Cost"]).sum()
            low_stock_count = len(inventory[inventory["Current Stock"] <= inventory["Minimum Stock"]])
        
        delayed_ships = 0
        if not shipments.empty:
            delayed_ships = len(shipments[shipments["Status"] == "Delayed"])

        avg_defect = 0.0
        if not suppliers.empty:
            avg_defect = suppliers["Defect Rate"].mean()

        return f"""### 📊 Operational Health Snapshot (Calculated Offline)
*   **Inventory Capitalization:** ₹{total_value:,.2f}
*   **Low Stock Alerts:** {low_stock_count} SKUs requiring replenishment.
*   **Logistics Disruptions:** {delayed_ships} delayed shipments currently flagged.
*   **Supplier Defect Average:** {avg_defect:.2f}% defects.

**⚡ Recommended Strategy:** Review low stock parts immediately, and prioritize shipments transit route optimizations in delayed corridors.
"""

    # Default Context Dump
    context_str = serialize_csv_context(inventory, suppliers, orders, shipments)
    return f"""### 🤖 Supply Chain Advisor (Offline Heuristics Mode)
*Gemini API is offline or key is missing. Here is a local analysis of your datasets:*

{context_str}
"""

def get_ai_response(
    prompt: str,
    inventory: pd.DataFrame,
    suppliers: pd.DataFrame,
    orders: pd.DataFrame,
    shipments: pd.DataFrame
) -> str:
    """
    Routing helper to get response. Queries Gemini API if key is valid,
    falls back to local calculations on error or key absence.
    """
    context = serialize_csv_context(inventory, suppliers, orders, shipments)
    api_key = get_api_key()
    
    if api_key:
        response = query_gemini_api(prompt, context, api_key)
        # If API returns error message, try parsing locally as a secondary safety net
        if response.startswith("⚠️ **Gemini API Error:**") or response.startswith("❌"):
            local_result = local_heuristic_fallback(prompt, inventory, suppliers, orders, shipments)
            return f"{response}\n\n---\n\n{local_result}"
        return response
    else:
        return local_heuristic_fallback(prompt, inventory, suppliers, orders, shipments)
