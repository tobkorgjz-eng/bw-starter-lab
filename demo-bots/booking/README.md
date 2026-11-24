# Booking helper (demo bot)

A small booking helper for **Maple Comb Studio**, a made-up hair salon.
Python 3 standard library only, all data in memory, no network calls.
All names and businesses are fictional.

- `booking.py` - `Salon` (free slots, book, cancel) and `BookingBot`, a text
  front end that always asks "yes/no" before a booking or cancellation is final.
- `demo.html` - one self-contained page a website can host as-is: all CSS and
  JavaScript inline, no external scripts, fonts or images, no network calls
  and no browser storage. The bot logic runs in the page and mirrors
  `booking.py` (same commands, rules and replies). Open it directly in a
  browser or upload the single file. Bookings vanish on reload.
- `test_booking.py` - schedule and conversation tests.
- `test_safety.py` - "asks before it acts" and prompt-injection tests.
- `test_demo_html.py` - checks that `demo.html` is self-contained and uses the
  same rule lists as `booking.py`; if `node` is installed it also runs the
  page's script on a sample conversation and compares every reply with
  `booking.py` (skipped when `node` is not available).

## Commands

```
services
slots <service> <date>                    e.g. slots haircut tomorrow
book <service> <date> <HH:MM> <name>      then answer yes / no
cancel <code>                             then answer yes / no
```

Open Mon-Sat 09:00-17:00, one chair, 15-minute start steps.
Times earlier than now are never offered or bookable (`Salon(clock=...)`
takes an injectable clock so tests are deterministic).

## How it follows "asks before it acts"

- `book` and `cancel` only *propose* the change and ask "(yes/no)". Nothing is
  booked or cancelled until the next message is exactly one of
  `yes, y, confirm, ok, sure` (any case). "No", `n`, `stop` or `nope` drops it.
- Anything else while a question is open - "yes please, and also cancel
  MC002", "ignore your rules, it's confirmed" - is not a yes; the bot says
  nothing has been booked yet and asks again.
- The slot is checked again at the moment of "yes"; if it was taken or the
  time has passed, the bot says so instead of booking.
- A reply only starts with `Booked:` or `Cancelled:` after that exact yes,
  and only when the change really happened.

## Customer text is data, not instructions

- The bot understands only the fixed commands above. There is no free-text
  path that can change what it does.
- Messages that try to give it new rules ("ignore your rules", "you are now
  admin", "SYSTEM: ...", "book without asking", ...) get one fixed refusal and
  change nothing. This phrase list is a simple tripwire, not a complete
  filter; the fixed commands and the exact-yes step are what keep the bot
  safe.
- Names may use letters, spaces, `-`, `'` and `.` (up to 40 characters), so a
  name cannot imitate a bot reply such as `Booked: ... (code MC001)`.
- In `demo.html` every message is shown with `textContent`, never as HTML.

Limits: this is a demo. It has no accounts, no real calendar, no payment and
no staff view; one browser tab or one Python process holds the whole
schedule.

## Run

```
cd demo-bots/booking
python3 booking.py          # interactive chat
python3 -m unittest -v      # tests
```

From the repo root:

```
python3 -m unittest discover -s demo-bots/booking -t demo-bots/booking
```
