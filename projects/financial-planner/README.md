# Financial Planner

Drop monthly bank statement PDFs into `data/statements/`, hit Scan, and get categorized spending insights.

- **Status:** Active (Phase 1 complete)
- **Type:** Personal expense tracking only
- **Stack:** Python (FastAPI + pdfplumber) backend, vanilla HTML/JS + Chart.js dashboard

## Quick Start

1. **Install dependencies:**
   ```bash
   cd projects/financial-planner
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python backend/app.py
   ```

3. **Open in browser:**
   Navigate to `http://localhost:8000`

## Usage

1. Drop PDF statements into `data/statements/`
2. Click **Scan** on the dashboard
3. Review and re-categorize any uncategorized transactions
4. Category overrides persist and apply to future statements

## What's Built (Phase 1)

✅ BMO credit card PDF parser (text extraction + vendor normalization)  
✅ Rules-based categorization engine with persistent overrides  
✅ Dark terminal-aesthetic dashboard with monthly summaries and donut chart  
✅ Sortable transaction table with inline category editing  
✅ Category filtering in transaction view  
✅ 9 transaction categories (Groceries, Dining & Drinking, Subscriptions, Shopping, Transportation, Entertainment, Housing, Events, Other)

## Supported Accounts

- **BMO CashBack World Elite Mastercard** (PDF) ✅
- CIBC Credit Card (PDF) — Phase 2
- CIBC Debit Account (PDF) — Phase 2

## Configuration

Vendor-to-category mappings are saved in `backend/rules.json` and persist across sessions.
