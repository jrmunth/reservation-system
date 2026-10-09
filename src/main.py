# src/main.py
"""Entry point for the CLI reservation system."""

import sys
import csv
import re
from datetime import datetime
from pathlib import Path

from reservation import Reservation
from storage import load_reservations, save_reservations
from utils import (
    prompt_name,
    prompt_date,
    prompt_time,
    prompt_int,
    prompt_phone,
    prompt_search_query,
    format_row,
    print_header,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = PROJECT_ROOT / "exports"


# ---------- ID generation ----------

def next_id(reservations) -> str:
    if not reservations:
        return "R001"
    numeric = [int(r.res_id[1:]) for r in reservations if r.res_id.startswith("R")]
    return f"R{max(numeric) + 1:03d}"


# ---------- Create ----------

def create_reservation(reservations) -> None:
    print("\n--- New Reservation ---")
    print("(type 'esc' at any prompt to cancel)\n")

    name = prompt_name("Name")
    if name is None:
        print("  [i] Cancelled.")
        return

    contact = prompt_phone()
    if contact is None:
        print("  [i] Cancelled.")
        return

    while True:
        date = prompt_date()
        if date is None:
            print("  [i] Cancelled.")
            return

        same_day = [r for r in reservations
                    if r.date == date and r.status == "confirmed"]
        if same_day:
            print(f"  [i] {len(same_day)} existing reservation(s) on {date}:")
            for r in same_day:
                print(f"      {r.res_id} at {r.time} — {r.name}")

        while True:
            time = prompt_time()
            if time is None:
                print("  [i] Cancelled.")
                return

            conflict = next(
                (r for r in reservations
                 if r.date == date and r.time == time and r.status == "confirmed"),
                None,
            )
            if conflict:
                print(f"  [!] {date} {time} is already booked by "
                      f"{conflict.name} ({conflict.res_id}).")
                print("      Enter a different time, or type 'esc' to cancel.")
                continue
            break
        break

    pax = prompt_int("Number of guests", 1, 50)
    if pax is None:
        print("  [i] Cancelled.")
        return

    res = Reservation(next_id(reservations), name, contact, date, time, pax)
    reservations.append(res)
    save_reservations(reservations)

    # Pretty echo of the stored time as 12-hour
    pretty_time = datetime.strptime(time, "%H:%M").strftime("%I:%M %p").lstrip("0")
    print(f"\n  [✓] Reservation {res.res_id} created for {name} "
          f"on {date} at {pretty_time} (pax {pax}).")


# ---------- View ----------

def view_all(reservations) -> None:
    print("\n--- All Reservations ---")
    if not reservations:
        print("  (no reservations yet)")
        return
    print_header()
    for r in reservations:
        print(format_row(r))


# ---------- Search (loops until esc) ----------

def search_reservations(reservations) -> None:
    print("\n--- Search ---")
    print("  Search by: reservation ID, name, contact, date, or time.")
    print("  Partial matches OK. Type 'esc' to stop searching.\n")

    while True:
        query = prompt_search_query()
        if query is None:
            print("  [i] Search ended.")
            return

        q = query.lower()
        matches = [
            r for r in reservations
            if q in r.res_id.lower()
            or q in r.name.lower()
            or q in r.contact.lower()
            or q in r.date.lower()
            or q in r.time.lower()
        ]

        if not matches:
            print(f"  (no matches for '{query}')\n")
            continue

        print(f"\n  {len(matches)} match(es):")
        print_header()
        for r in matches:
            print(format_row(r))
        print()  # blank line before next query


# ---------- Update (uses prompt_* helpers, no raw input) ----------

def find_by_id(reservations, res_id):
    return next((r for r in reservations if r.res_id == res_id), None)


def update_reservation(reservations) -> None:
    print("\n--- Update Reservation ---")
    res_id = prompt_name("Reservation ID (e.g. R001)")
    if res_id is None:
        print("  [i] Cancelled.")
        return

    res = find_by_id(reservations, res_id.upper())
    if not res:
        print(f"  [!] No reservation found with ID {res_id}.")
        return

    print(f"  Current: {format_row(res)}")
    print("  Press Enter to keep current value. Type 'esc' to cancel.\n")

    # Each prompt takes the current value as default and returns it on blank
    new_name = prompt_name("Name", default=res.name)
    if new_name is None:
        print("  [i] Cancelled — no changes saved.")
        return

    new_contact = prompt_phone(default=res.contact)
    if new_contact is None:
        print("  [i] Cancelled — no changes saved.")
        return

    # For date, prompt_date accepts a default; also rechecks conflicts
    while True:
        new_date = prompt_date(default=res.date)
        if new_date is None:
            print("  [i] Cancelled — no changes saved.")
            return

        # Check conflict on the new date (excluding this reservation)
        same_day = [
            r for r in reservations
            if r.date == new_date and r.status == "confirmed" and r is not res
        ]
        if same_day:
            print(f"  [i] Existing reservations on {new_date}:")
            for r in same_day:
                print(f"      {r.res_id} at {r.time} — {r.name}")

        new_time = prompt_time(default=res.time)
        if new_time is None:
            print("  [i] Cancelled — no changes saved.")
            return

        conflict = next(
            (r for r in reservations
             if r.date == new_date and r.time == new_time
             and r.status == "confirmed" and r is not res),
            None,
        )
        if conflict:
            print(f"  [!] {new_date} {new_time} is already booked by "
                  f"{conflict.name} ({conflict.res_id}).")
            print("      Try a different date/time, or 'esc' to cancel.")
            continue
        break

    new_pax = prompt_int("Number of guests", 1, 50, default=res.pax)
    if new_pax is None:
        print("  [i] Cancelled — no changes saved.")
        return

    # All prompts succeeded — commit
    res.name = new_name
    res.contact = new_contact
    res.date = new_date
    res.time = new_time
    res.pax = new_pax
    save_reservations(reservations)
    print(f"  [✓] Reservation {res.res_id} updated.")


# ---------- Cancel ----------

def cancel_reservation(reservations) -> None:
    print("\n--- Cancel Reservation ---")
    res_id = prompt_name("Reservation ID to cancel")
    if res_id is None:
        print("  [i] Cancelled.")
        return

    res = find_by_id(reservations, res_id.upper())
    if not res:
        print(f"  [!] No reservation found with ID {res_id}.")
        return

    if res.status == "cancelled":
        print(f"  [i] {res.res_id} is already cancelled.")
        return

    confirm = input(f"  Cancel {res.name}'s reservation? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Cancelled — no changes made.")
        return

    res.status = "cancelled"
    save_reservations(reservations)
    print(f"  [✓] Reservation {res.res_id} marked as cancelled.")


# ---------- Export ----------

def export_to_csv(reservations) -> None:
    if not reservations:
        print("  [!] Nothing to export.")
        return

    EXPORT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = EXPORT_DIR / f"reservations_{timestamp}.csv"

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Contact", "Date", "Time", "Pax", "Status"])
        for r in reservations:
            writer.writerow([r.res_id, r.name, r.contact, r.date, r.time, r.pax, r.status])

    print(f"  [✓] Exported to {out_path}")


# ---------- Menu ----------

MENU = """
===== RESERVATION SYSTEM =====
  1. Create Reservation
  2. View All Reservations
  3. Search Reservation
  4. Update Reservation
  5. Cancel Reservation
  6. Export to CSV
  0. Exit

  (type 'esc' at any input prompt to cancel)
"""

ACTIONS = {
    "1": create_reservation,
    "2": view_all,
    "3": search_reservations,
    "4": update_reservation,
    "5": cancel_reservation,
    "6": export_to_csv,
}


def main() -> None:
    reservations = load_reservations()
    print(f"Loaded {len(reservations)} reservation(s).")

    while True:
        print(MENU)
        choice = input("Choose an option (number): ").strip()

        if choice == "0":
            print("Goodbye!")
            sys.exit(0)

        action = ACTIONS.get(choice)
        if not action:
            print("  [!] Invalid option. Try again.")
            continue

        try:
            action(reservations)
        except KeyboardInterrupt:
            print("\n  [!] Interrupted — returning to menu.")


if __name__ == "__main__":
    main()