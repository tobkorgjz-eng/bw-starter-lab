# Client brief: Fernhill Bike Repair

Status: confirmed
Intake date: 2026-11-18 · Intake by: Sam Okafor (Blade Works)

> Made-up example. Fernhill Bike Repair and everyone named here are fictional.

## Business

- What it does: Repairs and services bicycles and e-bikes; sells used bikes and parts.
- Where: One workshop on Fernhill Road (fictional town of Brackwater); serves the town and nearby villages.
- Hours: Tue–Sat 9:00–17:30; closed Sun–Mon; shorter Saturday hours in January.
- Team: 3 people — owner (repairs, pricing), one mechanic, one part-time front-desk helper.
- Customers: Commuters, families, local cycling club members.

## People

- Owner / final yes: Priya Lindqvist, owner
- Backup yes: Tomas Reyes, head mechanic — booking changes only, when Priya is away
- How to ask for a yes: text message; Priya usually answers within 2 hours on workdays
- Setup contact: Priya Lindqvist

## Work today

- Where messages come in: phone, website contact form, shop email, social media messages
- Biggest time costs: answering "is my bike ready?" questions; booking service slots
- Often missed: replies to weekend website messages; reminders for annual services
- Tools in use: shared online calendar, shop email, a parts spreadsheet, card reader

## First tasks for the assistant

1. Answer "is my bike ready?" and opening-hours questions — done well means: a correct, short reply the same day.
2. Offer and book service slots — done well means: no double bookings; the customer gets a confirmed time.

Tone: friendly and short; no jargon; never say "cheap".
When it does not know: "I'll check with the workshop and get back to you by the next working day."

## May do alone

- `read_inbox` — read incoming email and website-form messages.
- `answer_faq` — answer hours, location and price-list questions from the approved FAQ.
- `check_repair_status` — look up whether a bike is ready on the workshop board.
- `check_calendar` — look up free service slots.
- `draft_reply` — write a draft reply and leave it for review.
- `summarize_day` — send Priya an end-of-day summary of messages.

## Needs the owner's yes

- `book_appointment` — put a service booking on the calendar (Tomas may also say yes).
- `cancel_appointment` — cancel or move a booking (Tomas may also say yes).
- `send_quote` — send a repair price estimate to a customer.
- `offer_discount` — offer any discount or free extra.
- `post_social` — publish anything on the shop's social media.
- `order_parts` — order parts from a supplier.

## Never does

- `issue_refund` — give a refund; Priya handles all refunds herself.
- `make_payment` — move money or take card payments.
- `delete_records` — delete customer, repair or sales records.
- `share_credentials` — reveal passwords or login details.
- `share_customer_details` — give one customer's details to anyone else.
- `diagnose_safety_issue` — tell a customer a bike is safe to ride.

Anything not listed needs the owner's yes.

## Limits and exceptions

- Quotes over 150 still need Priya's yes, not Tomas's.
- After 17:30 and on closed days: drafts only; no bookings until a yes arrives.
- If no answer to a yes request within 4 working hours: send one reminder, then leave the task in the summary.

## Information

- Facts it may use: price list (spreadsheet tab "Prices"), FAQ page on the shop website, workshop board
- Off limits: card reader records, staff rota, supplier invoices
- Keep records for: messages and drafts 90 days; daily summaries 1 year

## Success and concerns

- Helping means: fewer "is it ready?" phone calls; no weekend messages left unanswered past Tuesday noon
- Concerns: the assistant promising a repair date the workshop cannot meet
- Next review: 2026-12-16

## Sign-off

- Confirmed by: Priya Lindqvist on 2026-11-20
