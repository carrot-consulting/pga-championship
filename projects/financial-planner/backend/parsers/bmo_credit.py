import re
from datetime import date
from pathlib import Path

import pdfplumber

from backend.models import Statement, Transaction

ACCOUNT_NAME = "BMO CashBack World Elite MC"

MONTH_ABBREV = {
    "Jan.": 1, "Feb.": 2, "Mar.": 3, "Apr.": 4,
    "May": 5, "Jun.": 6, "Jul.": 7, "Aug.": 8,
    "Sep.": 9, "Oct.": 10, "Nov.": 11, "Dec.": 12,
}

# Pre-compiled regexes for vendor normalization
_RE_PHONE = re.compile(r"\d{3}-\d{3}-\d{4}")
_RE_CITY_PROV = re.compile(r"\s+[A-Z][A-Za-z]+(?:\s+[A-Z][a-z]+)?\s+[A-Z]{2}\s*$")
_RE_PROV = re.compile(r"\s+[A-Z]{2}\s*$")
_RE_GOOGLE = re.compile(r"^GOOGLE \*(.+)")
_RE_JUNK_SUFFIX = re.compile(r"\s+[a-z]{2,4}$")
_RE_STORE_NUM = re.compile(r"\s+[W#]\d+")
_RE_CITIES = re.compile(r"\s+(?:Montreal|Toronto|Vancouver|Ottawa|Halifax|Calgary|Edmonton|Winnipeg|Quebec)\s*$", re.IGNORECASE)
_RE_TRUNCATED = re.compile(r"\s+[A-Z]{2,4}$")
_RE_TRAILING_DASH = re.compile(r"\s*[-\u2013]\s*$")
_RE_PRIME_MEMBER = re.compile(r"\s+Prime Member$")
_RE_WHITESPACE = re.compile(r"\s+")


def _parse_date(date_str: str, year: int) -> date:
    """Parse 'Mar. 1' style dates into date objects."""
    parts = date_str.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Cannot parse date: {date_str}")
    month_str, day_str = parts
    month = MONTH_ABBREV[month_str]
    return date(year, month, int(day_str))


def _parse_amount(amount_str: str) -> tuple[float, bool]:
    """Parse amount string, return (amount, is_credit)."""
    cleaned = amount_str.strip().replace(",", "")
    is_credit = cleaned.endswith("CR")
    if is_credit:
        cleaned = cleaned.replace("CR", "").strip()
    return float(cleaned), is_credit


def _normalize_vendor(description: str) -> str:
    """Strip noise from transaction descriptions to get clean vendor name."""
    name = description.strip()

    # Remove "PAYMENT RECEIVED" patterns early
    if "PAYMENT RECEIVED" in name:
        return "Payment"

    # Remove "INTEREST" patterns early
    if name.startswith("INTEREST"):
        return "Interest Charge"

    name = _RE_PHONE.sub("", name)
    name = _RE_CITY_PROV.sub("", name)
    name = _RE_PROV.sub("", name)

    m = _RE_GOOGLE.match(name)
    if m:
        service = m.group(1).strip().replace("_", " ")
        service = _RE_JUNK_SUFFIX.sub("", service)
        if service.startswith("Google "):
            return service
        return f"Google {service}"

    name = name.replace("_", " ")
    name = _RE_STORE_NUM.sub("", name)
    name = _RE_CITIES.sub("", name)
    name = _RE_TRUNCATED.sub("", name)
    name = _RE_TRAILING_DASH.sub("", name)
    name = _RE_PRIME_MEMBER.sub("", name)
    name = _RE_WHITESPACE.sub(" ", name).strip()

    if name.isupper():
        name = name.title()

    return name


def _parse_full_date(raw: str) -> date:
    """Parse 'Mar. 24, 2026' style dates."""
    parts = raw.replace(",", "").split()
    return date(int(parts[2]), MONTH_ABBREV[parts[0]], int(parts[1]))


def _extract_statement_metadata(text: str) -> dict:
    metadata = {}

    m = re.search(r"Statement date\s+(\w+\.?\s+\d+,\s+\d{4})", text)
    if m:
        metadata["statement_date"] = _parse_full_date(m.group(1))

    m = re.search(
        r"Statement period\s+(\w+\.?\s+\d+,\s+\d{4})\s*[-\u2013]\s*(\w+\.?\s+\d+,\s+\d{4})",
        text,
    )
    if m:
        metadata["period_start"] = _parse_full_date(m.group(1))
        metadata["period_end"] = _parse_full_date(m.group(2))

    m = re.search(r"Previous total balance.*?\$?([\d,]+\.\d{2})", text)
    if m:
        metadata["previous_balance"] = float(m.group(1).replace(",", ""))

    m = re.search(r"Total balance\s+\$?([\d,]+\.\d{2})", text)
    if m:
        metadata["new_balance"] = float(m.group(1).replace(",", ""))

    return metadata


def _extract_transactions_from_text(full_text: str, year: int) -> list[Transaction]:
    """Parse transactions from raw text using regex.

    BMO transaction lines look like:
        Mar. 1 Mar. 2 GOOGLE *Workspace_carr 650-253-0000 ON 12.20
        Mar. 2 Mar. 3 PAYMENT RECEIVED - THANK YOU 300.00 CR
    """
    transactions = []

    # Match: trans_date posting_date description amount [CR]
    # Dates are like "Mar. 1" or "Mar. 22"
    pattern = re.compile(
        r"^(\w+\.?\s+\d{1,2})\s+(\w+\.?\s+\d{1,2})\s+"  # trans date, posting date
        r"(.+?)\s+"  # description (non-greedy)
        r"([\d,]+\.\d{2}(?:\s*CR)?)\s*$",  # amount, optional CR
        re.MULTILINE,
    )

    for m in pattern.finditer(full_text):
        trans_date_str = m.group(1)
        posting_date_str = m.group(2)
        raw_desc = m.group(3).strip()
        amount_str = m.group(4)

        # Skip subtotal/total lines
        if "Subtotal" in raw_desc or "Total for" in raw_desc:
            continue
        # Skip card number header lines
        if "Card number" in raw_desc:
            continue

        try:
            trans_date = _parse_date(trans_date_str, year)
            posting_date = _parse_date(posting_date_str, year)
            amount, is_credit = _parse_amount(amount_str)
        except (ValueError, KeyError):
            continue

        vendor = _normalize_vendor(raw_desc)

        transactions.append(
            Transaction(
                date=trans_date,
                posting_date=posting_date,
                raw_description=raw_desc,
                vendor_name=vendor,
                amount=amount,
                is_credit=is_credit,
                account_source=ACCOUNT_NAME,
            )
        )

    return transactions


def parse(pdf_path: str | Path) -> Statement:
    """Parse a BMO credit card PDF statement into a Statement object."""
    pdf_path = Path(pdf_path)

    with pdfplumber.open(pdf_path) as pdf:
        # Extract metadata from first page
        first_page_text = pdf.pages[0].extract_text() or ""
        metadata = _extract_statement_metadata(first_page_text)
        year = metadata.get("statement_date", date.today()).year

        # Extract transactions from all pages via text parsing
        # (pdfplumber table detection doesn't find the BMO transaction table)
        transactions = []
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            transactions.extend(_extract_transactions_from_text(page_text, year))

    return Statement(
        account_name=ACCOUNT_NAME,
        statement_date=metadata.get("statement_date", date.today()),
        period_start=metadata.get("period_start", date.today()),
        period_end=metadata.get("period_end", date.today()),
        previous_balance=metadata.get("previous_balance", 0.0),
        new_balance=metadata.get("new_balance", 0.0),
        transactions=transactions,
        source_file=pdf_path.name,
    )
