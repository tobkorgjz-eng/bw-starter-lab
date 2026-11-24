# Booking helper (demo bot)

A small booking helper for **Maple Comb Studio**, a made-up hair salon.
Python 3 standard library only, all data in memory, no network calls.

- `booking.py` - `Salon` (free slots, book, cancel) and `BookingBot`, a text
  front end that always asks "yes/no" before a booking or cancellation is final.
- `test_booking.py` - unittest tests.
- `index.html` - static, self-contained browser demo of the same flow
  (no external resources, no network calls). Open it directly in a browser.

## Commands

```
services
slots <service> <date>                    e.g. slots haircut tomorrow
book <service> <date> <HH:MM> <name>      then answer yes / no
cancel <code>                             then answer yes / no
```

Open Mon-Sat 09:00-17:00, one chair, 15-minute start steps.

## Run

```
cd demo-bots/booking
python3 booking.py          # interactive chat
python3 -m unittest -v      # tests
```
