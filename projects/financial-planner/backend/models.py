from datetime import date
from pydantic import BaseModel


class Transaction(BaseModel):
    date: date
    posting_date: date
    raw_description: str
    vendor_name: str
    amount: float
    is_credit: bool
    category: str = "Uncategorized"
    account_source: str = ""


class Statement(BaseModel):
    account_name: str
    statement_date: date
    period_start: date
    period_end: date
    previous_balance: float
    new_balance: float
    transactions: list[Transaction]
    source_file: str = ""


class MonthlySummary(BaseModel):
    month: str
    total_expenses: float
    total_credits: float
    net: float
    transaction_count: int
    by_category: dict[str, float]
