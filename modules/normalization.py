
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation


def normalize_amount(value):
    """
    Convert currency amounts into comparable numeric values.

    Examples:
        "₹11,50,000" -> 1150000
        "Rs. 11,50,000" -> 1150000
        "1150000" -> 1150000
        None -> None

    Returns None for missing values.
    Raises ValueError for invalid amounts.
    """

    if value is None:
        return None

    if isinstance(value, bool):
        raise ValueError("Boolean values are not valid amounts.")

    if isinstance(value, (int, float, Decimal)):
        try:
            amount = Decimal(str(value))
        except InvalidOperation:
            raise ValueError(f"Invalid amount: {value}")

    else:
        amount_text = str(value).strip()

        if not amount_text or amount_text.lower() in {
            "none", "null", "nan", "n/a", "na", "-"
        }:
            return None

        # Remove currency symbols.
        amount_text = amount_text.replace("₹", "")

        # Remove currency labels at the beginning.
        amount_text = re.sub(
            r"(?i)^\s*(?:inr|rs\.?|rupees?)\s*",
            "",
            amount_text
        )

        # Remove currency labels at the end.
        amount_text = re.sub(
            r"(?i)\s*(?:inr|rs\.?|rupees?)\s*$",
            "",
            amount_text
        )

        # Remove commas and spaces.
        amount_text = amount_text.replace(",", "")
        amount_text = amount_text.replace(" ", "")

        try:
            amount = Decimal(amount_text)
        except InvalidOperation:
            raise ValueError(f"Invalid amount: {value}")

    if not amount.is_finite():
        raise ValueError(f"Invalid amount: {value}")

    if amount == amount.to_integral_value():
        return int(amount)

    return float(amount)


def normalize_date(value):
    """
    Convert supported date formats into ISO format: YYYY-MM-DD.

    Supported examples:
        2026-01-10
        10/01/2026
        10-01-2026
        10.01.2026
        10 Jan 2026
        10 January 2026

    Numeric Indian-style dates use day/month/year order.
    Missing values return None.
    Invalid dates raise ValueError.
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date().isoformat()

    date_text = str(value).strip()

    if not date_text or date_text.lower() in {
        "none", "null", "nan", "n/a", "na", "-"
    }:
        return None

    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%d %b %Y",
        "%d %B %Y",
        "%Y/%m/%d",
    ]

    for date_format in formats:
        try:
            parsed_date = datetime.strptime(date_text, date_format)
            return parsed_date.date().isoformat()
        except ValueError:
            continue

    raise ValueError(f"Unsupported or invalid date: {value}")


def normalize_project_id(value):
    """
    Standardise project ID casing and surrounding whitespace.

    Does not alter internal characters.
    """

    if value is None:
        return None

    project_id = str(value).strip()

    if not project_id or project_id.lower() in {
        "none", "null", "nan", "n/a", "na", "-"
    }:
        return None

    return project_id.upper()


def normalize_text(value, casefold=False):
    """
    Standardise text by removing leading/trailing whitespace
    and replacing repeated whitespace with a single space.

    Set casefold=True for case-insensitive comparison.
    Similar names are not automatically treated as identical.
    """

    if value is None:
        return None

    text = str(value).strip()

    if not text or text.lower() in {
        "none", "null", "nan", "n/a", "na", "-"
    }:
        return None

    text = re.sub(r"\s+", " ", text)

    if casefold:
        text = text.casefold()

    return text
