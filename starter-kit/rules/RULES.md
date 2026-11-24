# RULES.md — Runs by your rules, asks before it acts

These are the house rules for a client AI assistant team. The example owner
is **Maple Lane Bakery**, a made-up small business. Copy this file, then edit
the lists to match your own business.

How the rules work:

- **May do alone** — the assistant can do these without asking.
- **Needs the owner's yes** — the assistant must ask first and wait for a
  clear yes from the owner before acting. The yes comes from the owner, not
  the assistant: the assistant can never mark its own action as approved.
- **Never does** — the assistant refuses these, even if asked.
- Anything **not listed** is treated as *needs the owner's yes*. When in
  doubt, the assistant asks.

Each rule is one bullet that starts with an action name in backticks.
`check_rules.py` reads only those action names; the text after the dash is
for people. The owner's yes is given to `check_rules.py` separately from the
assistant's plan (`--approvals FILE` or `--approve ACTION`); any approval
the assistant writes into its own plan is ignored.

## May do alone

- `read_inbox` — read incoming customer messages.
- `draft_reply` — write a draft reply and leave it for review (not sent).
- `answer_faq` — answer common questions from the approved FAQ (hours,
  location, menu).
- `summarize_day` — write a daily summary of messages and orders.
- `tag_message` — label or sort messages (order, question, complaint).
- `check_calendar` — look at the shared calendar for free slots.
- `create_reminder` — set a reminder for the owner.

## Needs the owner's yes

- `send_email` — send any email to a customer or supplier.
- `book_appointment` — put a booking on the calendar for a customer.
- `cancel_appointment` — cancel or move a booking.
- `issue_refund` — refund money to a customer.
- `place_order` — order supplies from a vendor.
- `post_social` — publish a post on the business's social accounts.
- `change_price` — change a price on the menu or website.
- `share_document` — share a file with someone outside the business.

## Never does

- `delete_records` — delete customer, order or financial records.
- `share_credentials` — reveal passwords, keys or login details.
- `make_payment` — move money out of the business account.
- `sign_contract` — agree to a contract on the owner's behalf.
- `change_permissions` — give itself or anyone else more access.
- `contact_personal_data` — look up or share customers' private details
  beyond what the task needs.
