import unittest
from datetime import date, datetime

from booking import BookingBot, BookingError, Salon

TODAY = date(2030, 1, 14)      # a Monday
DAY = "2030-01-15"             # Tuesday
SUNDAY = "2030-01-20"


def at(hh, mm=0, day=date(2030, 1, 15)):
    return datetime(day.year, day.month, day.day, hh, mm)


class SalonTests(unittest.TestCase):
    def setUp(self):
        self.salon = Salon(today=TODAY)

    def test_free_slots_full_day(self):
        slots = self.salon.free_slots(date(2030, 1, 15), "haircut")
        self.assertEqual(slots[0], at(9))
        self.assertEqual(slots[-1], at(16, 30))
        self.assertEqual(len(slots), 31)

    def test_closed_on_sunday_and_past(self):
        self.assertEqual(self.salon.free_slots(date(2030, 1, 20), "haircut"), [])
        self.assertEqual(self.salon.free_slots(date(2030, 1, 1), "haircut"), [])

    def test_unknown_service(self):
        with self.assertRaises(BookingError):
            self.salon.free_slots(date(2030, 1, 15), "perm-xyz")

    def test_book_removes_overlapping_slots(self):
        b = self.salon.book("Test Customer", "color", at(10))
        self.assertEqual(b.code, "MC001")
        self.assertEqual(b.end, at(11, 30))
        slots = self.salon.free_slots(date(2030, 1, 15), "haircut")
        self.assertIn(at(9, 30), slots)
        self.assertNotIn(at(9, 45), slots)
        self.assertNotIn(at(11, 15), slots)
        self.assertIn(at(11, 30), slots)

    def test_double_booking_rejected(self):
        self.salon.book("Customer One", "haircut", at(10))
        with self.assertRaises(BookingError):
            self.salon.book("Customer Two", "haircut", at(10, 15))

    def test_must_fit_before_close_and_need_name(self):
        with self.assertRaises(BookingError):
            self.salon.book("Customer", "color", at(16))
        with self.assertRaises(BookingError):
            self.salon.book("  ", "haircut", at(10))

    def test_cancel_frees_slot(self):
        b = self.salon.book("Customer", "haircut", at(10))
        self.salon.cancel(b.code.lower())
        self.assertIn(at(10), self.salon.free_slots(date(2030, 1, 15), "haircut"))
        with self.assertRaises(BookingError):
            self.salon.cancel(b.code)


class BotTests(unittest.TestCase):
    def setUp(self):
        self.salon = Salon(today=TODAY)
        self.bot = BookingBot(self.salon)

    def test_greet_and_help(self):
        self.assertIn("Maple Comb Studio", self.bot.greet())
        self.assertIn("slots", self.bot.handle("help"))
        self.assertIn("didn't catch", self.bot.handle("dance"))

    def test_slots_command(self):
        reply = self.bot.handle(f"slots haircut {DAY}")
        self.assertIn("09:00", reply)
        self.assertIn("No free", self.bot.handle(f"slots haircut {SUNDAY}"))
        self.assertIn("Sorry", self.bot.handle("slots haircut someday"))

    def test_book_asks_before_confirming(self):
        reply = self.bot.handle(f"book haircut {DAY} 10:00 Test Customer")
        self.assertIn("Shall I book it?", reply)
        self.assertEqual(self.salon.bookings, {})  # nothing booked yet
        self.assertIn("yes or no", self.bot.handle("maybe"))
        self.assertEqual(self.salon.bookings, {})
        reply = self.bot.handle("yes")
        self.assertIn("Booked", reply)
        self.assertIn("MC001", reply)
        self.assertEqual(len(self.salon.bookings), 1)

    def test_book_declined(self):
        self.bot.handle(f"book haircut {DAY} 10:00 Test Customer")
        self.assertIn("nothing was changed", self.bot.handle("no"))
        self.assertEqual(self.salon.bookings, {})
        self.assertIsNone(self.bot.pending)

    def test_book_unavailable_does_not_ask(self):
        self.salon.book("Someone", "haircut", at(10))
        reply = self.bot.handle(f"book haircut {DAY} 10:00 Test Customer")
        self.assertIn("not available", reply)
        self.assertIsNone(self.bot.pending)

    def test_cancel_asks_before_confirming(self):
        self.salon.book("Test Customer", "haircut", at(10))
        reply = self.bot.handle("cancel mc001")
        self.assertIn("cancel", reply)
        self.assertIn("(yes/no)", reply)
        self.assertEqual(len(self.salon.bookings), 1)
        self.assertIn("Cancelled", self.bot.handle("y"))
        self.assertEqual(self.salon.bookings, {})

    def test_cancel_unknown_code(self):
        self.assertIn("No booking", self.bot.handle("cancel MC999"))
        self.assertIsNone(self.bot.pending)

    def test_slot_taken_between_ask_and_yes(self):
        self.bot.handle(f"book haircut {DAY} 10:00 Test Customer")
        self.salon.book("Faster Customer", "haircut", at(10))
        self.assertIn("not available", self.bot.handle("yes"))
        self.assertIsNone(self.bot.pending)


if __name__ == "__main__":
    unittest.main()
