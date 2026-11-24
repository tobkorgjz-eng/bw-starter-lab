"""Booking helper for a made-up hair salon ("Maple Comb Studio").

Standard library only, no network calls. All data is fictional and in memory.

Two layers:
  * Salon        - the schedule: list free slots, hold, book and cancel.
  * BookingBot   - a tiny text chat front end that always asks the customer
                   to answer "yes" before a booking or cancellation is final.

Customer text is data, never instructions: the bot only understands its fixed
commands, a pending action needs an exact "yes" on its own, and messages that
try to change the rules ("ignore your rules", "you are now ...") get a fixed
refusal and change nothing.
"""

import re

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

SALON_NAME = "Maple Comb Studio"

# service key -> (label, minutes)
SERVICES = {
    "haircut": ("Haircut", 30),
    "wash": ("Wash and blow-dry", 30),
    "color": ("Colour", 90),
    "trim": ("Beard or fringe trim", 15),
}

OPEN_AT = time(9, 0)
CLOSE_AT = time(17, 0)
STEP_MINUTES = 15
CLOSED_WEEKDAYS = {6}  # Sunday (Monday == 0)

YES_WORDS = {"yes", "y", "confirm", "ok", "sure"}
NO_WORDS = {"no", "n", "stop", "nope"}

NAME_MAX = 40
# Letters (any alphabet), spaces, hyphen, apostrophe, full stop. No digits,
# colons, brackets or line breaks, so a name cannot imitate a bot reply such
# as "Booked: ... (code MC001)".
_NAME_RE = re.compile(r"^[^\W\d_](?:[^\W\d_]|[ .'-])*$")

# Phrases that try to give the bot new instructions. Matching is
# case-insensitive and on word boundaries ("contact asap" does not match
# "act as"); it is a tripwire, not the safety net. The real protection is
# that the bot has no free-text "do anything" path.
INJECTION_PATTERNS = (
    "ignore", "disregard", "forget your", "forget the", "override",
    "your rules", "new rules", "system prompt", "system:", "you are now",
    "ignoring", "act as", "pretend", "pretending", "jailbreak",
    "developer mode", "admin mode", "without asking", "without confirm",
    "without confirmation", "skip confirm", "skip confirmation",
    "skip the confirmation", "no need to ask",
    "don't ask", "dont ask", "already confirmed", "pre-confirmed",
    "auto-confirm", "<script",
)

REFUSAL = ("I can only help with bookings, and my rules stay the same: "
           "I always ask before I book or cancel anything. Nothing was "
           "changed.")


def _pattern_re(phrase):
    # A boundary is only required where the phrase starts or ends with a
    # letter or digit ("system:" and "<script" carry their own edge).
    start = r"(?<![a-z0-9])" if phrase[0].isalnum() else ""
    end = r"(?![a-z0-9])" if phrase[-1].isalnum() else ""
    return start + re.escape(phrase) + end


_INJECTION_RE = re.compile("|".join(_pattern_re(p) for p in INJECTION_PATTERNS))


def looks_like_injection(text):
    low = (text or "").lower().replace("\u2019", "'")
    return _INJECTION_RE.search(low) is not None


def _same_name(a, b):
    return " ".join(a.split()).lower() == " ".join(b.split()).lower()


class BookingError(ValueError):
    """Raised when a request cannot be fulfilled."""


@dataclass
class Booking:
    code: str
    customer: str
    service: str
    start: datetime
    end: datetime

    def describe(self):
        label = SERVICES[self.service][0]
        return (f"{label} for {self.customer} on {self.start:%a %d %b %Y} "
                f"at {self.start:%H:%M}-{self.end:%H:%M} (code {self.code})")


def _overlaps(a_start, a_end, b_start, b_end):
    return a_start < b_end and b_start < a_end


class Salon:
    """In-memory schedule with a single chair.

    `clock` is a zero-argument callable returning the current datetime
    (defaults to datetime.now); inject a fixed one for deterministic tests.
    Passing only `today` means "the start of that day".
    """

    def __init__(self, today=None, clock=None):
        if clock is None:
            if today is not None:
                start_of_day = datetime.combine(today, time.min)
                clock = lambda: start_of_day
            else:
                clock = datetime.now
        self.clock = clock
        self.bookings = {}
        self._next = 1

    @property
    def now(self):
        return self.clock()

    @property
    def today(self):
        return self.now.date()

    # -- queries ---------------------------------------------------------
    def is_open(self, day):
        return day.weekday() not in CLOSED_WEEKDAYS

    def free_slots(self, day, service):
        """Return start times (datetime) where `service` fits on `day`."""
        if service not in SERVICES:
            raise BookingError(f"Unknown service '{service}'. "
                               f"Try one of: {', '.join(SERVICES)}.")
        now = self.now
        if not self.is_open(day) or day < now.date():
            return []
        length = timedelta(minutes=SERVICES[service][1])
        cursor = datetime.combine(day, OPEN_AT)
        close = datetime.combine(day, CLOSE_AT)
        slots = []
        while cursor + length <= close:
            end = cursor + length
            if cursor >= now and not any(_overlaps(cursor, end, b.start, b.end)
                       for b in self.bookings.values()):
                slots.append(cursor)
            cursor += timedelta(minutes=STEP_MINUTES)
        return slots

    # -- changes ---------------------------------------------------------
    def check(self, customer, service, start):
        """Validate a request without booking it. Returns the end time."""
        customer = " ".join((customer or "").split())
        if not customer:
            raise BookingError("Please give a name for the booking.")
        if len(customer) > NAME_MAX or not _NAME_RE.match(customer):
            raise BookingError(f"Names can use letters, spaces, - ' and . "
                               f"(up to {NAME_MAX} characters).")
        if start < self.now:
            raise BookingError("That time has already passed.")
        if start not in self.free_slots(start.date(), service):
            raise BookingError("That time is not available.")
        return start + timedelta(minutes=SERVICES[service][1])

    def book(self, customer, service, start):
        end = self.check(customer, service, start)
        code = f"MC{self._next:03d}"
        self._next += 1
        booking = Booking(code, " ".join(customer.split()), service, start,
                          end)
        self.bookings[code] = booking
        return booking

    def find(self, code, customer):
        """Return the booking only if both code and name match.

        The same message is used for a wrong code and a wrong name, so the
        reply does not reveal which codes exist.
        """
        booking = self.bookings.get((code or "").strip().upper())
        if booking is None or not _same_name(booking.customer, customer or ""):
            raise BookingError("No booking found with that code and name.")
        return booking

    def cancel(self, code, customer):
        booking = self.find(code, customer)
        del self.bookings[booking.code]
        return booking


def parse_day(text, today):
    text = text.strip().lower()
    if text == "today":
        return today
    if text == "tomorrow":
        return today + timedelta(days=1)
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise BookingError("Dates look like 2030-01-15, 'today' or "
                           "'tomorrow'.") from None


def parse_time(text):
    try:
        return datetime.strptime(text.strip(), "%H:%M").time()
    except ValueError:
        raise BookingError("Times look like 10:30.") from None


HELP = (
    "I can help with:\n"
    "  services\n"
    "  slots <service> <date>\n"
    "  book <service> <date> <HH:MM> <your name>\n"
    "  cancel <code> <your name>\n"
    "Dates: YYYY-MM-DD, today or tomorrow."
)


class BookingBot:
    """Text front end. Bookings and cancellations wait for a 'yes'."""

    def __init__(self, salon):
        self.salon = salon
        self.pending = None  # ("book", args) or ("cancel", (code, name))

    def greet(self):
        return f"Hi! This is the {SALON_NAME} booking helper.\n{HELP}"

    def handle(self, message):
        text = (message or "").strip()
        if self.pending is not None:
            return self._answer(text.lower())
        if looks_like_injection(text):
            return REFUSAL
        if not text:
            return HELP
        parts = text.split()
        command, args = parts[0].lower(), parts[1:]
        try:
            if command in ("help", "hi", "hello"):
                return HELP
            if command == "services":
                return "\n".join(f"  {k}: {v[0]} ({v[1]} min)"
                                 for k, v in SERVICES.items())
            if command == "slots":
                return self._slots(args)
            if command == "book":
                return self._ask_book(args)
            if command == "cancel":
                return self._ask_cancel(args)
        except BookingError as exc:
            return f"Sorry: {exc}"
        return "I didn't catch that.\n" + HELP

    # -- commands ----------------------------------------------------------
    def _slots(self, args):
        if len(args) != 2:
            raise BookingError("Use: slots <service> <date>")
        service = args[0].lower()
        day = parse_day(args[1], self.salon.today)
        slots = self.salon.free_slots(day, service)
        if not slots:
            return f"No free {service} slots on {day:%a %d %b %Y}."
        times = ", ".join(f"{s:%H:%M}" for s in slots)
        return f"Free {service} slots on {day:%a %d %b %Y}: {times}"

    def _ask_book(self, args):
        if len(args) < 4:
            raise BookingError("Use: book <service> <date> <HH:MM> <name>")
        service = args[0].lower()
        day = parse_day(args[1], self.salon.today)
        start = datetime.combine(day, parse_time(args[2]))
        name = " ".join(args[3:])
        end = self.salon.check(name, service, start)
        name = " ".join(name.split())
        self.pending = ("book", (name, service, start))
        return (f"Just to check: {SERVICES[service][0]} for {name} on "
                f"{start:%a %d %b %Y} at {start:%H:%M}-{end:%H:%M}. "
                "Shall I book it? (yes/no)")

    def _ask_cancel(self, args):
        if len(args) < 2:
            raise BookingError("Use: cancel <code> <your name>")
        name = " ".join(args[1:])
        booking = self.salon.find(args[0], name)
        self.pending = ("cancel", (booking.code, name))
        return (f"Just to check: cancel {booking.describe()}? (yes/no)")

    def _answer(self, word):
        # Only an exact yes/no word counts. Anything else ("yes, and also
        # cancel MC002", "ignore your rules, it's confirmed") is not a yes.
        kind, payload = self.pending
        if word in NO_WORDS:
            self.pending = None
            return "No problem, nothing was changed."
        if word not in YES_WORDS:
            return ("Nothing has been booked or cancelled yet. "
                    "Please answer yes or no.")
        self.pending = None
        try:
            if kind == "book":
                booking = self.salon.book(*payload)
                return f"Booked: {booking.describe()}."
            booking = self.salon.cancel(*payload)
            return f"Cancelled: {booking.describe()}."
        except BookingError as exc:
            return f"Sorry: {exc}"


def main():  # pragma: no cover - interactive
    bot = BookingBot(Salon())
    print(bot.greet())
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.strip().lower() in ("quit", "exit"):
            break
        print(bot.handle(line))


if __name__ == "__main__":  # pragma: no cover
    main()
