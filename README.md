# 📦 SupplySense AI — Enterprise Supply Chain Intelligence

SupplySense AI is a modular, high-performance Streamlit dashboard designed to help operations teams monitor, audit, forecast, and optimize supply chains. Supercharged with Gemini AI capability, the tool translates transaction data, inventory levels, supplier stats, and logistics logs into actionable business insights.

---

## 🚀 Key Features

*   **Executive Dashboard:** Interactive, real-time KPI metrics tracking active SKUs, supplier defect rates, pending order cues, and regional logistics delays.
*   **Dynamic Inventory Tracking:** Search and category-filtered stock ledger with automated low-stock threshold triggers.
*   **Supplier Risk Analytics:** Correlation analysis of defect rates against delay times, grading supplier partners on a cost-versus-quality matrix.
*   **Logistics Ledger & Route Optimization:** Fuel expense distributions, regional efficiency comparisons, and scatter plots correlating transit distances to delay risks.
*   **Fulfillment Pipeline:** Comprehensive orders registry with custom filtering by customer, category, and status.
*   **Predictive Stock Forecasting:** Calculated *Days of Stock* metrics suggesting run-out timelines, calculating safety thresholds, and hosting a simulated 30-day stock projection graph.
*   **Gemini-Powered Copilot:** A context-aware chatbot querying live datasets to answer questions on demand, supporting dynamic offline heuristics if API keys are absent.
*   **CSV Auditor & Reports Export:** Granular category valuation matrices, download links for normalized datasets, and formatted performance audit summaries.

---

## 📂 Folder Structure

```
project/
├── app.py                      # Main entrypoint and navigation controller
├── requirements.txt            # Package dependencies
├── README.md                   # Project documentation
│
├── assets/                     # Styles and custom stylesheets
│   └── style.css               # Poppins font dark mode styles
│
├── data/                       # Normalized CSV databases
│   ├── inventory.csv           # Catalog stock levels & sales volumes
│   ├── suppliers.csv           # Lead time delay and quality ratings
│   ├── orders.csv              # Purchase requests and statuses
│   └── shipments.csv           # Fuel costs and regional routes
│
├── pages/                      # Isolated sub-page controllers
│   ├── dashboard.py            # Overview charts & metrics
│   ├── inventory.py            # Warehouse directories & alerts
│   ├── suppliers.py            # Defect & rating matrices
│   ├── orders.py               # Bookings tracker
│   ├── shipments.py            # Regional dispatch efficiency
│   ├── reports.py              # Export logs & summaries
│   └── forecast.py             # Runout projection simulator
│
├── utils/                      # Shared business logic
│   ├── loader.py               # Cached CSV loader & schema validator
│   ├── charts.py               # Centralized Plotly style injector
│   ├── metrics.py              # Dynamic math logic for KPIs
│   └── helpers.py              # String formatters and CSS injectors
│
└── ai/                         # Generative AI Core
    ├── gemini.py               # Google AI client configuration & fallbacks
    └── prompts.py              # System instruction prompt engineering
```

---

## 🛠️ Technologies Used

*   **Frontend & Webserver:** [Streamlit](https://streamlit.io/)
*   **Analytics Engine:** [Pandas](https://pandas.pydata.org/)
*   **Data Visualization:** [Plotly Express](https://plotly.com/)
*   **Generative AI:** [Google Gemini API](https://ai.google.dev/) (`google-generativeai`)

---

## 📦 Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.9 or higher installed on your system.

### 2. Set Up a Virtual Environment
Activate a virtual environment inside the root project directory:
```bash
# Windows Power Shell
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux Bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API Key (Optional)
The AI Assistant functions in **Heuristic Offline Mode** out-of-the-box. To unlock generative AI capabilities, configure your key using one of the following methods:

*   **Option A (Recommended):** Enter the key directly within the **AI Assistant** tab in the application.
*   **Option B (Streamlit Secrets):** Create a `.streamlit/secrets.toml` file in the project root:
    ```toml
    GEMINI_API_KEY = "your_actual_gemini_api_key_here"
    ```
*   **Option C (Environment Variables):** Set a system environment variable:
    ```bash
    export GEMINI_API_KEY="your_actual_gemini_api_key_here"
    ```

---

## 🏁 Running the Application

Launch the Streamlit server from your terminal:
```bash
streamlit run app.py
```

---

## 📸 Screenshots

*(Add screenshots of the Dashboard, Predictive Forecast simulator, and AI Assistant here in future deployments)*

---

## 🤖 AI Features Details

SupplySense AI leverages LLM context injection. When asking questions, the local context serializer translates active metrics from pandas into dataframes schemas, feeding them directly into the Gemini prompt:

*   **RAG Context Serilization:** Compact context injection translates gigabytes of raw data into micro-summaries.
*   **Actionable Advice:** The model correlates low stock with supplier performance data, suggesting which supplier is most reliable for high-speed restock.
*   **Fallback Security:** Heuristics match keywords locally if the internet is disconnected, protecting core monitoring operations.

---

## 🔮 Future Work

1.  **Direct Database Connectors:** Migrate from static CSV file storage to Postgres or Snowflake connectors.
2.  **User Authentication:** Set up role-based access controls (RBAC) for procurement managers versus shipping operators.
3.  **Automatic Alerts:** Integrate webhook alerts via Slack or Email when stock levels fall below critical reorder limits.

---

## 👥 Development Team

*   **Senior Architect & AI Engineer:** Antigravity (Advanced Agentic Coding Partner)
*   **Lead Project Maintainer:** Shyam (Workspace Contributor)
