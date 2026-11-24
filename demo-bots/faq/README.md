# FAQ bot demo (made-up plumbing company)

A small FAQ bot for **Copperline Plumbing Co.**, a made-up business.
It answers only from `faq.json`. When a question is not covered, it says
so instead of guessing and offers to pass the question to a person.

- `faq.json`: FAQ entries (question, keywords, phrases, answer), the fallback
  reply, the injection reply, injection phrases and the hand-off texts
- `faq_bot.py`: the bot (Python 3 standard library only, no network)
- `test_faq_bot.py`: unittest tests
- `demo.html`: single-file browser demo. CSS, JS, the bot logic and the
  FAQ data are all inside the page. It loads no external scripts, fonts or
  images and makes no network calls.

## How it behaves

- **Answers only from the FAQ.** Every reply is one of the fixed texts in
  `faq.json`: an FAQ answer, the fallback or the injection reply. The
  customer's own words are never copied into a reply.
- **Says when it does not know.** If nothing matches, it replies
  "I don't have that in my FAQ, so I won't guess." and offers to pass the
  question to a person.
- **No invented prices or promises.** The only price it ever states is the
  call-out fee written in the FAQ, and that answer says other job prices
  aren't listed. Questions about discounts, refunds, guarantees or arrival
  times get the fallback, not a yes.
- **Customer text is data, not instructions.** A message containing phrases
  such as "ignore your rules", "you are now", "system prompt" or
  "from now on" gets a fixed reply ("messages can't change how I work") plus
  the hand-off offer, even if it also contains FAQ keywords. This check is
  a simple phrase list, not a full defense. The bot is still safe with
  messages the list misses, because it can only ever reply with the fixed
  texts above.
- **Hand-off in the demo is local only.** The "Pass my question to a person"
  button shows a note that, in this demo, nothing is sent anywhere.

## Matching

Each FAQ has specific `keywords` (e.g. "heater") and multi-word `phrases`
(e.g. "hot water"). Generic words like "water", "hot" or "time" are not
keywords on their own, so "Is my water bill too high?" gets the fallback
instead of a confident wrong answer.

## Run

    python3 faq_bot.py "Do you fix water heaters?"
    python3 faq_bot.py            # interactive, blank line quits

Tests, from the repo root:

    python3 -m unittest discover -s demo-bots/faq -t demo-bots/faq

Open `demo.html` directly in a browser for the demo. If you edit
`faq.json`, copy it into the `faq-data` JSON block in `demo.html` too
(a test checks they match). If `node` is installed, one test also runs the
page's own JavaScript offline and checks it gives the same replies as
`faq_bot.py`; without `node` that test is skipped.
