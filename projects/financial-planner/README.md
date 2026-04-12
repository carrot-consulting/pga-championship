# Financial Planner

Drop monthly bank statement PDFs into `data/statements/`, hit Scan, and get categorized spending insights.

- **Status:** Active (Phase 1 complete)
- **Type:** Personal
- **Stack:** Python (FastAPI + pdfplumber) backend, vanilla HTML/JS + Chart.js dashboard

## Quick Start

```bash
cd projects/financial-planner
source .venv/bin/activate
uvicorn backend.app:app --port 8099
```

Open `http://localhost:8099` in your browser.

## Usage

1. Drop PDF statements into `data/statements/`
2. Click **Scan** on the dashboard
3. Review and re-categorize any uncategorized vendors
4. Category overrides are saved and applied to future statements

## Supported Accounts

- BMO CashBack World Elite Mastercard (PDF)
- CIBC Credit Card (PDF) - coming soon
- CIBC Debit Account (PDF) - coming soon

## Categories

Groceries, Dining, Subscriptions, Shopping, Transportation, Entertainment, Housing, Other

Custom vendor-to-category mappings are saved in `backend/rules.json`.
