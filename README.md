# Cargo — GenAI Supply Chain Agent

A Generative AI-powered Supply Chain Agent that predicts demand, monitors inventory, manages supplier risks, and automates procurement decisions to create a smarter, faster, and more efficient supply chain.

This repo currently contains a **single-file front-end demo** (`genai-supply-chain-agent.html`) built to present the product concept and interface direction. It is a progress checkpoint, not the final product — see [Roadmap](#roadmap) for what comes next.

---

## What problem this solves

Businesses lose money in two opposite directions at once: running out of stock (lost sales, unhappy customers) and overstocking (tied-up cash, storage cost, waste). Most teams catch these problems manually, after they've already happened, by digging through spreadsheets and ERP screens.

Cargo is meant to sit on top of that data and do three things continuously: predict demand before it's needed, flag risk before it becomes a stock-out, and let a manager ask a plain-language question instead of building a report.

---

## How the current demo works

Everything lives in one HTML file with inline CSS and JavaScript — no build step, no server, no dependencies to install. Open it in any browser and it runs.

### 1. Dashboard section
- **Demand forecast chart** — rendered with Chart.js, plotting a 14-day predicted stock curve against a reorder threshold line.
- **Supplier reliability list** — a ranked list of suppliers with a reliability score and progress bar.
- **Stock-out risk table** — a list of SKUs with current stock, days-to-stock-out, recommended reorder quantity, and a risk pill (Healthy / Watch / High risk).

All of this data is **hardcoded as JavaScript arrays** near the bottom of the file (`forecast`, `suppliers`, `risk`). There is no real inventory system behind it yet — it exists to show what the interface looks like once real data is flowing in.

### 2. "Ask the Agent" chat widget
A chat-style UI where you can type a question or tap one of three preset buttons. It is **not connected to a real language model** — it's a lookup table (`responses` object in the script) that matches a typed question against three known questions and returns a pre-written answer with a short artificial delay, to simulate what a live response would feel like. Anything outside those three questions returns a generic fallback message.

This is the part most worth narrating in a demo: it shows the *intended interaction model* even though the intelligence behind it isn't wired up yet.

### 3. Capabilities and roadmap sections
Static content explaining the six functions the agent is meant to perform, and a phase-by-phase build plan (see below) so reviewers can see this is an intentional, staged build rather than a one-shot project.

---

## File structure

```
genai-supply-chain-agent.html   → the entire demo (HTML + CSS + JS, single file)
README.md                       → this file
```

As development continues, this will grow into a proper project structure (see Phase 2+ below) with separate frontend, backend, and data layers.

---

## Roadmap

### Phase 1 — Concept & interface (done)
Define the problem, design the dashboard and conversational UI, and mock the data model for forecasts, risk, and suppliers. This is the current demo.

### Phase 2 — Data pipeline (in progress)
Replace the hardcoded arrays with real data. Realistic starting point: ingest a CSV/Excel export from an existing inventory or ERP system (stock levels, sales history, supplier records), parse it on a backend, and serve it to the dashboard via an API instead of inline JS. This is where a database (e.g. PostgreSQL or a simple SQLite file to start) gets introduced.

### Phase 3 — Forecasting model
Build the actual demand prediction logic. Options to evaluate:
- A classical time-series model (e.g. moving average, exponential smoothing, or Prophet) for a fast, explainable baseline.
- An LLM-assisted approach that reasons over sales trends and seasonality in natural language.
Validate accuracy against held-out historical data before trusting its recommendations.

### Phase 4 — LLM agent layer
Replace the chat widget's lookup table with a real language model (e.g. via the Anthropic API) that has **tool access** to the inventory database, supplier records, and the forecasting model from Phase 3. This is what turns "Ask the Agent" from a scripted demo into a genuinely useful assistant that can answer arbitrary questions, not just the three pre-written ones.

### Phase 5 — Automated procurement
Let the agent draft purchase orders at its recommended quantities and route them to a manager for approval, with a full audit trail of what data and reasoning produced each recommendation.

---

## How to extend the current demo right now

A few concrete next steps that don't require the full pipeline:

- **Swap mock data for a CSV**: load a real inventory CSV with PapaParse in the browser as an interim step before a backend exists.
- **Add more scripted Q&A pairs**: expand the `responses` object so the demo handles more sample questions convincingly.
- **Connect the chat to a real model**: the simplest version of Phase 4 is calling the Anthropic API directly from the page with the dashboard data included in the prompt context, before a full tool-calling backend is built.

---

## Notes for presenting tomorrow

- Lead with the chat widget — it's the most tangible expression of "ask it like you'd ask a planner."
- Be upfront that the dashboard numbers are illustrative; the honest framing is "this is the interface and interaction model — Phase 2 connects it to real data."
- The roadmap section on the page itself is built to be shown directly, so you don't need a separate slide for "what's next."
