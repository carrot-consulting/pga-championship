import csv
import re
from datetime import date
from pathlib import Path

from backend.models import Statement, Transaction

ACCOUNT_NAME = "CIBC Debit"

# Pre-compiled regexes
_RE_TRAILING_REF = re.compile(r"\s+\d{6,}.*$")          # trailing numeric ref + anything after
_RE_FX_SUFFIX = re.compile(r"\s+[\d,]+\.\d{2}\s+[A-Z]{3}\s+@\s+[\d.]+.*$")
_RE_SLASH_SUFFIX = re.compile(r"/[A-Z_]{2,8}$")          # e.g. "/UBE", "/BILL", "/PA"
_RE_STAR_PENDING = re.compile(r"\s*\*?\s*PENDING\s*$", re.I)
_RE_SQ_PREFIX = re.compile(r"^SQ \*", re.I)
_RE_AIRBNB_CODE = re.compile(r"\s+\*\s*[A-Z0-9]{6,}\b")  # "* HM3824"
_RE_STORE_NUM = re.compile(r"\s+#\d+\b")
_RE_WHITESPACE = re.compile(r"\s+")


def _normalize_vendor(description: str) -> str:
    desc = description.strip()

    # --- Classified patterns (return early) ---

    # E-transfer: "Internet Banking E-TRANSFER 011548604222 MEG COONEY"
    m = re.match(r"Internet Banking E-TRANSFER \d+\s+(.+)$", desc, re.I)
    if m:
        name = m.group(1).strip().title()
        return f"E-Transfer: {name}"

    # Internal transfer (no payee)
    if re.match(r"Internet Banking INTERNET TRANSFER \d+\s*$", desc, re.I):
        return "Internal Transfer"

    # International transfer fee
    if re.match(r"Internet Banking INTERNET GLOBAL MONEY TRANSFER", desc, re.I):
        return "International Transfer"

    # ATM withdrawal
    if re.match(r"Automated Banking Machine", desc, re.I):
        return "ATM Withdrawal"

    # Branch fees
    if re.match(r"Branch Transaction OVERDRAFT", desc, re.I):
        return "Overdraft Fee"
    if re.match(r"Branch Transaction SERVICE CHARGE", desc, re.I):
        return "Bank Service Fee"
    if re.match(r"Branch Transaction NETWORK TRANSACTION FEE", desc, re.I):
        return "ATM Fee"
    if re.match(r"Branch Transaction", desc, re.I):
        return "Bank Fee"

    # EFT network fee
    if re.match(r"Electronic Funds Transfer NETWORK TRANSACTION FEE", desc, re.I):
        return "ATM Fee"

    # --- Strip type prefix to isolate vendor name ---
    prefixes = [
        r"Internet Banking INTERNET BILL PAY \d+\s+",
        r"Internet Banking\s+",
        r"Electronic Funds Transfer PREAUTHORIZED DEBIT \d*\s*",
        r"Electronic Funds Transfer DEPOSIT EDI \d+\s+",
        r"Electronic Funds Transfer DEPOSIT\s+",
        r"Electronic Funds Transfer PAY\s+",
        r"Electronic Funds Transfer\s+",
        r"Point of Sale - Interac RETAIL PURCHASE \d+\s+",
        r"Point of Sale - Visa Debit INTL VISA DEB RETAIL PURCHASE\s+",
        r"Point of Sale - Visa Debit VISA DEBIT RETAIL PURCHASE\s+",
        r"Point of Sale - Visa Debit VISA DEBIT PURCHASE REVERSAL\s+",
        r"Point of Sale - Visa Debit CORRECTION\s+",
        r"Point of Sale - Visa Debit\s+",
    ]

    name = desc
    for pat in prefixes:
        m = re.match(pat, name, re.I)
        if m:
            name = name[m.end():].strip()
            break

    # Strip FX rate info: "235.00 CAD @ 1.000000"
    name = _RE_FX_SUFFIX.sub("", name)

    # Strip trailing numeric ref codes
    name = _RE_TRAILING_REF.sub("", name)

    # Square vendor prefix: "SQ *IGLOOFEST" → "Igloofest"
    name = _RE_SQ_PREFIX.sub("", name)

    # Airbnb listing codes: "AIRBNB * HM3824" → "Airbnb"
    name = _RE_AIRBNB_CODE.sub("", name)

    # * PENDING suffix: "UBER * PENDING" → "Uber"
    name = _RE_STAR_PENDING.sub("", name)

    # Trailing /SUFFIX: "UBER CANADA/UBE" → "Uber Canada"
    name = _RE_SLASH_SUFFIX.sub("", name)

    # Store numbers: "PHARMAPRIX #180" → "Pharmaprix"
    name = _RE_STORE_NUM.sub("", name)

    name = _RE_WHITESPACE.sub(" ", name).strip()

    if name.isupper() or name.islower():
        name = name.title()

    return name or "Unknown"


def parse(csv_path: str | Path) -> Statement:
    """Parse a CIBC debit account CSV export into a Statement object.

    CSV format (no header, 4 columns):
        date (YYYY-MM-DD), description, debit_amount, credit_amount
    """
    csv_path = Path(csv_path)
    transactions: list[Transaction] = []

    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue

            date_str = row[0].strip()
            raw_desc = row[1].strip()
            debit_str = row[2].strip()
            credit_str = row[3].strip() if len(row) > 3 else ""

            try:
                txn_date = date.fromisoformat(date_str)
            except ValueError:
                continue

            if debit_str:
                amount = float(debit_str.replace(",", ""))
                is_credit = False
            elif credit_str:
                amount = float(credit_str.replace(",", ""))
                is_credit = True
            else:
                continue

            vendor = _normalize_vendor(raw_desc)

            transactions.append(
                Transaction(
                    date=txn_date,
                    posting_date=txn_date,
                    raw_description=raw_desc,
                    vendor_name=vendor,
                    amount=amount,
                    is_credit=is_credit,
                    account_source=ACCOUNT_NAME,
                )
            )

    if transactions:
        dates = [t.date for t in transactions]
        period_start = min(dates)
        period_end = max(dates)
    else:
        period_start = period_end = date.today()

    return Statement(
        account_name=ACCOUNT_NAME,
        statement_date=period_end,
        period_start=period_start,
        period_end=period_end,
        previous_balance=0.0,
        new_balance=0.0,
        transactions=transactions,
        source_file=csv_path.name,
    )
