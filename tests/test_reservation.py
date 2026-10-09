# tests/test_reservation.py
"""Basic tests for the Reservation model."""

import sys
import unittest
from pathlib import Path

# Allow importing from src/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from reservation import Reservation


class TestReservation(unittest.TestCase):

    def test_to_dict_round_trip(self):
        r = Reservation("R001", "Juan", "09171234567",
                        "2026-10-15", "18:30", 4)
        restored = Reservation.from_dict(r.to_dict())
        self.assertEqual(r.res_id, restored.res_id)
        self.assertEqual(r.name, restored.name)
        self.assertEqual(r.pax, restored.pax)
        self.assertEqual(r.status, "confirmed")

    def test_default_status(self):
        r = Reservation("R002", "Maria", "09189876543",
                        "2026-10-16", "12:00", 2)
        self.assertEqual(r.status, "confirmed")

    def test_from_dict_missing_status_defaults(self):
        data = {
            "res_id": "R003", "name": "Pedro", "contact": "09001112222",
            "date": "2026-10-17", "time": "09:00", "pax": 3,
        }
        r = Reservation.from_dict(data)
        self.assertEqual(r.status, "confirmed")


if __name__ == "__main__":
    unittest.main()