import json
import re
from collections import defaultdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.categorizer import categorize, get_categories, set_vendor_category
from backend.models import MonthlySummary, Transaction
from backend.parsers import bmo_credit

app = FastAPI(title="Financial Planner")

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
STATEMENTS_DIR = DATA_DIR / "statements"
PROCESSED_FILE = DATA_DIR / "processed.json"
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"

STATEMENTS_DIR.mkdir(parents=True, exist_ok=True)

PARSERS = {
    "bmo": bmo_credit.parse,
}


def _load_processed() -> set[str]:
    if PROCESSED_FILE.exists():
        return set(json.loads(PROCESSED_FILE.read_text()))
    return set()


def _save_processed(processed: set[str]) -> None:
    PROCESSED_FILE.write_text(json.dumps(sorted(processed), indent=2) + "\n")


def _load_transactions() -> list[Transaction]:
    if TRANSACTIONS_FILE.exists():
        data = json.loads(TRANSACTIONS_FILE.read_text())
        return [Transaction.model_validate(t) for t in data]
    return []


def _save_transactions(transactions: list[Transaction]) -> None:
    data = [t.model_dump(mode="json") for t in transactions]
    TRANSACTIONS_FILE.write_text(json.dumps(data, indent=2) + "\n")


def _detect_parser(filename: str):
    lower = filename.lower()
    for key, parser in PARSERS.items():
        if key in lower:
            return parser
    return None


@app.post("/scan")
def scan_statements():
    """Scan the statements folder for new PDFs and parse them."""
    processed = _load_processed()
    existing_transactions = _load_transactions()
    new_count = 0
    errors = []

    for pdf_file in sorted(STATEMENTS_DIR.glob("*.pdf")):
        if pdf_file.name in processed:
            continue

        parser = _detect_parser(pdf_file.name)
        if not parser:
            errors.append({"file": pdf_file.name, "error": "No parser found for file"})
            continue

        try:
            statement = parser(pdf_file)
            categorize(statement.transactions)
            existing_transactions.extend(statement.transactions)
            processed.add(pdf_file.name)
            new_count += len(statement.transactions)
        except Exception as e:
            errors.append({"file": pdf_file.name, "error": str(e)})

    if new_count > 0:
        _save_transactions(existing_transactions)
        _save_processed(processed)

    return {
        "new_transactions": new_count,
        "total_transactions": len(existing_transactions),
        "errors": errors,
    }


@app.get("/transactions")
def get_transactions(
    month: str | None = None,
    category: str | None = None,
    account: str | None = None,
) -> list[dict]:
    """List transactions with optional filters."""
    if month and not re.match(r'^\d{4}-\d{2}$', month):
        raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")

    transactions = _load_transactions()

    if month:
        transactions = [
            t for t in transactions if t.date.strftime("%Y-%m") == month
        ]
    if category:
        transactions = [t for t in transactions if t.category == category]
    if account:
        transactions = [t for t in transactions if t.account_source == account]

    transactions.sort(key=lambda t: t.date, reverse=True)
    return [t.model_dump(mode="json") for t in transactions]


@app.get("/summary")
def get_summary(month: str | None = None) -> dict:
    if month and not re.match(r'^\d{4}-\d{2}$', month):
        raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")

    transactions = _load_transactions()

    if month:
        transactions = [
            t for t in transactions if t.date.strftime("%Y-%m") == month
        ]

    total_expenses = 0.0
    total_credits = 0.0
    by_category: dict[str, float] = defaultdict(float)

    for t in transactions:
        if t.is_credit:
            total_credits += t.amount
        elif t.category == "Interest":
            by_category["Interest"] += t.amount
            total_expenses += t.amount
        else:
            by_category[t.category] += t.amount
            total_expenses += t.amount

    by_category = {k: round(v, 2) for k, v in by_category.items()}

    return MonthlySummary(
        month=month or "all",
        total_expenses=round(total_expenses, 2),
        total_credits=round(total_credits, 2),
        net=round(total_expenses - total_credits, 2),
        transaction_count=len(transactions),
        by_category=by_category,
    ).model_dump()


class CategorizeRequest(BaseModel):
    vendor_name: str
    category: str


@app.put("/categorize")
def categorize_vendor(req: CategorizeRequest):
    categories = get_categories()
    if req.category not in categories and req.category not in ("Payment", "Interest"):
        raise HTTPException(
            status_code=400,
            detail=f"Unknown category: {req.category}. Valid: {categories}",
        )

    set_vendor_category(req.vendor_name, req.category)

    transactions = _load_transactions()
    categorize(transactions)
    _save_transactions(transactions)

    return {"status": "ok", "vendor": req.vendor_name, "category": req.category}


@app.get("/categories")
def list_categories():
    """Return available categories."""
    return get_categories()


@app.get("/months")
def list_months():
    """Return available months from transaction data."""
    transactions = _load_transactions()
    months = sorted(set(t.date.strftime("%Y-%m") for t in transactions))
    return months


# Serve frontend static files
FRONTEND_DIR = PROJECT_ROOT / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(str(FRONTEND_DIR / "index.html"))
