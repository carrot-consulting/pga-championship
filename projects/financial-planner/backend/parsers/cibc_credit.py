import csv
import re
from datetime import date
from pathlib import Path

from backend.models import Statement, Transaction

ACCOUNT_NAME = "CIBC Credit Card"

# Pre-compiled regexes for vendor normalization
_RE_FX_SUFFIX = re.compile(r"\s+[\d,]*\.?\d+\s+[A-Z]{3}\s+@\s+[\d.]+.*$")   # "235.00 USD @ 1.43" or ".99 EUR @ 1.65"
_RE_PHONE_SUFFIX = re.compile(r"\s+\d{3}[-\s]\d{3}[-\s]\d{4}.*$")            # "866-216-1072, ON" → strip all
_RE_ASTERISK_CODE = re.compile(r"\*[A-Z0-9-]{5,}")                            # "*GS4L521S3" order codes
_RE_CITY_PROV = re.compile(r"\s+[A-Za-z][A-Za-z'-]+,\s+[A-Z]{2}\s*$")        # " MONTREAL, QC" (1-word city)
_RE_PROVINCE_ONLY = re.compile(r",\s*[A-Z]{2}\s*$")                           # leftover ", ON"
_RE_ALPHANUM_CODE = re.compile(r"\s+[A-Z][A-Z0-9]*[0-9][A-Z0-9]*\b")         # mixed letter+digit codes: "DG1K4Z0SD"
_RE_SQ_PREFIX = re.compile(r"^SQ \*", re.I)                                   # Square vendor prefix
_RE_STORE_NUM = re.compile(r"\s+[#\*]?\d{3,}\b")                              # "#8739", "00823"
_RE_WHITESPACE = re.compile(r"\s+")


def _normalize_vendor(description: str) -> str:
    name = description.strip()

    # Payment marker
    if "PAYMENT" in name.upper() and "THANK" in name.upper():
        return "Payment"

    # FX rate suffix: "235.00 USD @ 1.430592"
    name = _RE_FX_SUFFIX.sub("", name)

    # Phone number suffix: "866-216-1072, ON" → strip from phone onwards
    name = _RE_PHONE_SUFFIX.sub("", name)

    # Asterisk order codes: "Amazon.ca*GS4L521S3", "CA*BC9098TG1"
    name = _RE_ASTERISK_CODE.sub("", name)

    # City + Province: " MONTREAL, QC"
    name = _RE_CITY_PROV.sub("", name)

    # Leftover province-only: ", ON"
    name = _RE_PROVINCE_ONLY.sub("", name)

    # Square vendor prefix: "SQ *IGLOOFEST" → "Igloofest"
    name = _RE_SQ_PREFIX.sub("", name)

    # Alphanumeric booking codes (contain both letters AND digits): "DG1K4Z0SD", "Ryanair 000000S21Kfd0"
    name = _RE_ALPHANUM_CODE.sub("", name)

    # Store/branch numbers: "#8739", "400"
    name = _RE_STORE_NUM.sub("", name)

    # Strip trailing punctuation
    name = name.strip(" ,*-/")

    name = _RE_WHITESPACE.sub(" ", name).strip()

    if name.isupper():
        name = name.title()

    return name or "Unknown"


def parse(csv_path: str | Path) -> Statement:
    """Parse a CIBC credit card CSV export into a Statement object.

    CSV format (no header, 5 columns):
        date (YYYY-MM-DD), description, debit_amount, credit_amount, account_number
    """
    csv_path = Path(csv_path)
    transactions: list[Transaction] = []

    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 4:
                continue

            date_str = row[0].strip()
            raw_desc = row[1].strip()
            debit_str = row[2].strip()
            credit_str = row[3].strip()

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
