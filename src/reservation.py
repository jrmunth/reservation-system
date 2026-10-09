# src/reservation.py
"""Data model for a reservation. Pure logic — no I/O, no user input."""


class Reservation:
    """Represents a single reservation entry."""

    def __init__(self, res_id, name, contact, date, time, pax, status="confirmed"):
        self.res_id = res_id
        self.name = name
        self.contact = contact
        self.date = date        # ISO format: YYYY-MM-DD
        self.time = time        # HH:MM (24-hour)
        self.pax = pax          # number of guests
        self.status = status    # "confirmed" | "cancelled"

    def to_dict(self):
        """Convert to a plain dict so it can be JSON-serialized."""
        return {
            "res_id": self.res_id,
            "name": self.name,
            "contact": self.contact,
            "date": self.date,
            "time": self.time,
            "pax": self.pax,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a Reservation from a dict loaded from JSON."""
        return cls(
            res_id=data["res_id"],
            name=data["name"],
            contact=data["contact"],
            date=data["date"],
            time=data["time"],
            pax=data["pax"],
            status=data.get("status", "confirmed"),
        )

    def __repr__(self):
        return (
            f"Reservation({self.res_id!r}, {self.name!r}, "
            f"{self.date!r} {self.time!r}, pax={self.pax}, status={self.status!r})"
        )