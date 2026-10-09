# src/utils.py
"""Input validation and formatting helpers.

All prompt_* functions:
- Return None if the user cancels (types 'esc'/'cancel'/'exit'/'q')
- Accept a `default` value; pressing Enter returns the default (if provided)
"""

import re
from datetime import datetime, timedelta


CANCEL_WORDS = {"esc", "cancel", "exit", "q"}


def _is_cancel(value: str) -> bool:
    return value.strip().lower() in CANCEL_WORDS


def _label_with_default(label: str, default) -> str:
    """Append '[current]' to the label when a default exists."""
    if default is None:
        return label
    return f"{label} [{default}]"


# ---------- Date ----------

def prompt_date(label: str = "Date (YYYY-M-D, or 'today'/'tomorrow')", default=None):
    """Date input. Accepts single digits. Returns ISO YYYY-MM-DD or None."""
    while True:
        raw = input(f"{_label_with_default(label, default)}: ").strip()

        if _is_cancel(raw):
            return None

        # Blank keeps default (only during update)
        if raw == "" and default is not None:
            return default

        lowered = raw.lower()
        if lowered == "today":
            return datetime.now().strftime("%Y-%m-%d")
        if lowered == "tomorrow":
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        # Allow 1 or 2 digits for month and day: YYYY-M-D or YYYY-MM-DD
        match = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", raw)
        if not match:
            print("  [!] Use YYYY-M-D or YYYY-MM-DD (e.g. 2026-1-5 or 2026-01-05).")
            continue

        year, month, day = match.groups()
        try:
            dt = datetime(int(year), int(month), int(day))
            return dt.strftime("%Y-%m-%d")  # normalize to 2-digit
        except ValueError:
            print("  [!] That's not a real date (check month/day range).")


# ---------- Time (12-hour input, 24-hour storage) ----------

def _prompt_meridiem() -> str:
    """Ask for AM/PM. Returns 'AM' or 'PM'."""
    while True:
        raw = input("  AM or PM? ").strip().upper()
        if _is_cancel(raw):
            return None
        if raw in ("AM", "A"):
            return "AM"
        if raw in ("PM", "P"):
            return "PM"
        print("  [!] Enter 'AM' or 'PM'.")


def prompt_time(label: str = "Time (H:MM or HH:MM, 12-hour)", default=None):
    """12-hour input with AM/PM. Returns 24-hour 'HH:MM' or None."""
    while True:
        # If we have a default, show it converted to 12-hour for display
        display_default = None
        if default is not None:
            try:
                dt = datetime.strptime(default, "%H:%M")
                display_default = dt.strftime("%I:%M %p").lstrip("0")
            except ValueError:
                display_default = default

        raw = input(f"{_label_with_default(label, display_default)}: ").strip()

        if _is_cancel(raw):
            return None

        # Blank keeps default
        if raw == "" and default is not None:
            return default

        # Accept H:MM or HH:MM (single or double digit hour)
        match = re.fullmatch(r"(\d{1,2}):(\d{2})", raw)
        if not match:
            print("  [!] Use H:MM or HH:MM (e.g. 6:30 or 06:30).")
            continue

        hour, minute = int(match.group(1)), int(match.group(2))

        if not (1 <= hour <= 12):
            print("  [!] Hour must be between 1 and 12.")
            continue
        if not (0 <= minute <= 59):
            print("  [!] Minute must be between 00 and 59.")
            continue

        meridiem = _prompt_meridiem()
        if meridiem is None:
            return None

        # Convert to 24-hour
        if meridiem == "AM":
            hour24 = 0 if hour == 12 else hour
        else:  # PM
            hour24 = 12 if hour == 12 else hour + 12

        return f"{hour24:02d}:{minute:02d}"


# ---------- Integer ----------

def prompt_int(label: str, min_val: int = 1, max_val: int = 100, default=None):
    """Integer within range. Returns None on cancel."""
    while True:
        raw = input(
            f"{_label_with_default(label + f' ({min_val}-{max_val})', default)}: "
        ).strip()

        if _is_cancel(raw):
            return None
        if raw == "" and default is not None:
            return default

        try:
            num = int(raw)
            if min_val <= num <= max_val:
                return num
            print(f"  [!] Must be between {min_val} and {max_val}.")
        except ValueError:
            print("  [!] That's not a valid number.")


# ---------- Phone ----------

def prompt_phone(label: str = "Contact number", default=None):
    """PH-style phone. Returns normalized digits or None."""
    hint = f"{label} (09XXXXXXXXX or +639XXXXXXXXX)"
    while True:
        raw = input(f"{_label_with_default(hint, default)}: ").strip()

        if _is_cancel(raw):
            return None
        if raw == "" and default is not None:
            return default

        cleaned = raw.replace(" ", "").replace("-", "")
        if re.fullmatch(r"09\d{9}", cleaned) or re.fullmatch(r"\+639\d{9}", cleaned):
            return cleaned

        print("  [!] Use 09XXXXXXXXX or +639XXXXXXXXX (11-13 digits).")


# ---------- Name ----------

def prompt_name(label: str = "Name", default=None):
    """Non-empty name. Returns None on cancel."""
    while True:
        raw = input(f"{_label_with_default(label, default)}: ").strip()

        if _is_cancel(raw):
            return None
        if raw == "" and default is not None:
            return default
        if raw:
            return raw
        print("  [!] Name cannot be empty.")


# ---------- Search ----------

def prompt_search_query() -> str:
    """Search query. Returns None on cancel."""
    raw = input("Search query (or 'esc' to stop searching): ").strip()
    if _is_cancel(raw):
        return None
    return raw or None


# ---------- Display ----------

def format_row(res) -> str:
    return (
        f"{res.res_id:<6} {res.name:<20} {res.contact:<15} "
        f"{res.date:<12} {res.time:<6} {res.pax:>4}  {res.status}"
    )


def print_header() -> None:
    print(
        f"{'ID':<6} {'NAME':<20} {'CONTACT':<15} "
        f"{'DATE':<12} {'TIME':<6} {'PAX':>4}  STATUS"
    )
    print("-" * 80)