import json
from pathlib import Path

from backend.models import Transaction

RULES_PATH = Path(__file__).parent / "rules.json"


def _load_rules() -> dict:
    if RULES_PATH.exists():
        return json.loads(RULES_PATH.read_text())
    return {"vendor_rules": {}, "categories": []}


def _save_rules(rules: dict) -> None:
    RULES_PATH.write_text(json.dumps(rules, indent=2) + "\n")


def categorize(transactions: list[Transaction]) -> None:
    """Apply category rules to transactions. Modifies in place."""
    rules = _load_rules()
    vendor_rules = rules.get("vendor_rules", {})

    for txn in transactions:
        if txn.vendor_name == "Payment":
            txn.category = "Payment"
        elif txn.vendor_name == "Interest Charge":
            txn.category = "Interest"
        elif txn.vendor_name in vendor_rules:
            txn.category = vendor_rules[txn.vendor_name]
        else:
            txn.category = "Uncategorized"


def set_vendor_category(vendor_name: str, category: str) -> None:
    """Save a vendor -> category mapping to the rules file."""
    rules = _load_rules()
    rules["vendor_rules"][vendor_name] = category
    _save_rules(rules)


def get_categories() -> list[str]:
    """Return the list of available categories."""
    rules = _load_rules()
    return rules.get("categories", [])


def get_uncategorized(transactions: list[Transaction]) -> list[str]:
    """Return vendor names that don't have a category rule."""
    rules = _load_rules()
    vendor_rules = rules.get("vendor_rules", {})
    seen = set()
    uncategorized = []
    for txn in transactions:
        if (
            txn.vendor_name not in vendor_rules
            and txn.vendor_name not in ("Payment", "Interest Charge")
            and txn.vendor_name not in seen
        ):
            seen.add(txn.vendor_name)
            uncategorized.append(txn.vendor_name)
    return uncategorized
