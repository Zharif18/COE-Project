import streamlit as st
from dotenv import load_dotenv
from utils.loader import load_csv, clear_data_cache
from utils.helpers import load_css

# Load environment variables
load_dotenv()

# ---------------------------------------
# PAGE CONFIG
# ---------------------------------------
st.set_page_config(
    page_title="SupplySense AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------
# LOAD STYLING & DATA
# ---------------------------------------
load_css("assets/style.css")

inventory = load_csv("inventory.csv")
suppliers = load_csv("suppliers.csv")
orders = load_csv("orders.csv")
shipments = load_csv("shipments.csv")

# ---------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------
st.sidebar.title("🚀 SupplySense AI")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Inventory",
        "Suppliers",
        "Orders",
        "Shipments",
        "Forecast",
        "AI Assistant",
        "Reports"
    ]
)

# Cache management widget
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reload Raw Datasets"):
    clear_data_cache()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(
    """
    📦 Supply Chain Agent
    
    Version 1.0
    
    Powered by Gemini AI
    """
)

# ---------------------------------------
# ROUTING CONTROLLER
# ---------------------------------------
if page == "Dashboard":
    from pages.dashboard import render_dashboard
    render_dashboard(inventory, suppliers, orders, shipments)

elif page == "Inventory":
    from pages.inventory import render_inventory
    render_inventory(inventory)

elif page == "Suppliers":
    from pages.suppliers import render_suppliers
    render_suppliers(suppliers)

elif page == "Orders":
    from pages.orders import render_orders
    render_orders(orders)

elif page == "Shipments":
    from pages.shipments import render_shipments
    render_shipments(shipments)

elif page == "Forecast":
    from pages.forecast import render_forecast
    render_forecast(inventory, orders, suppliers)

elif page == "AI Assistant":
    from pages.ai_assistant import render_ai_assistant
    render_ai_assistant(inventory, suppliers, orders, shipments)

elif page == "Reports":
    from pages.reports import render_reports
    render_reports(inventory, suppliers, orders, shipments)