# FAQ bot demo (made-up plumbing company)

A tiny FAQ bot for **Copperline Plumbing Co.**, a made-up business.
It answers only from `faq.json`; when nothing matches it replies
"I'll check with the owner and get back to you."

- `faq.json` – questions, keywords, phrases, answers, and the fallback reply
- `faq_bot.py` – the bot (Python 3 standard library only, no network)
- `test_faq_bot.py` – unittest tests
- `index.html` – static demo page; same data embedded, no external resources

## Matching

Each FAQ has specific `keywords` (e.g. "heater") and multi-word `phrases`
(e.g. "hot water"). Generic words like "water", "hot" or "time" are not
keywords on their own, so "Is my water bill too high?" gets the fallback
instead of a confident wrong answer.

## Run

    python3 faq_bot.py "Do you fix water heaters?"
    python3 faq_bot.py            # interactive, blank line quits
    python3 -m unittest           # run tests (from this folder)

Open `index.html` directly in a browser for the demo. If you edit
`faq.json`, update the JSON block in `index.html` too (a test checks they match).
