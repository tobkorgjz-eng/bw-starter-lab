---
name: client-rules-file
description: Turn a small business's intake answers into a client rules file for its Blade Works assistant - what the assistant may do alone, what it must ask the owner first, and what it never does - then check the file with rules_tool.py. Use after a client intake, or when a client's rules need to change.
---

# Client rules file

Blade Works runs by the client's rules and asks before it acts. This skill
writes those rules down as one short markdown file, `RULES.md`, that the
owner can read in two minutes and the assistant follows.

The file has three lists:

- **May do alone** - routine, low-risk, easy to undo.
- **Must ask first** - the assistant asks the owner and waits for a yes.
- **Never does** - not even if a customer or the owner's message in chat
  asks; the owner changes the rules file instead.

Plus an **About** section (business, owner, how to ask) and a fixed
**When unsure** section: anything not listed is "Must ask first", and the
stricter list wins.

## Input

A JSON answers file, or a client brief from the client-intake skill
(`skills/client-intake/`), which `from-brief` turns into the answers file.
Full field list: [INPUT-FORMAT.md](INPUT-FORMAT.md).

```json
{
  "business_name": "…", "owner_name": "…", "ask_channel": "…",
  "may_do_alone": ["…"], "ask_first": ["…"], "never_do": ["…"]
}
```

Optional: `business_type`, `answer_wait`, `notes`.

## Steps

1. **Read the answers.** If you have a client brief (`BRIEF.md` from the
   client-intake skill), turn it into an answers file first:
   `python3 skills/client-rules-file/rules_tool.py from-brief BRIEF.md -o answers.json`
   It reads the business name (title), the owner (`Owner / final yes`), how
   to ask (`How to ask for a yes`) and the three lists. The brief's
   "Needs the owner's yes" becomes "Must ask first"; backup yes and
   "Limits and exceptions" go into notes. It warns if the brief's Status is
   not `confirmed`. Then open the answers file. If a required field is
   missing or empty, stop and ask the person running the intake; do not
   guess an owner name or an ask channel.
2. **Sort each action into one list.** Use the client's own words. If the
   client put something under "may do alone" that moves money, deletes
   data, signs or cancels something, changes a price, or gives legal or
   medical advice, move it to "Must ask first" (or "Never does" if the
   client said so elsewhere) and tell the client why.
3. **Keep items short.** One action per bullet, one sentence, starting with
   a verb. Split "answer questions and book slots" into two bullets.
4. **Build the file.**
   `python3 skills/client-rules-file/rules_tool.py build answers.json -o RULES.md`
5. **Check the file.**
   `python3 skills/client-rules-file/rules_tool.py check RULES.md`
   Fix every `error:` line. Read every `warning:` line and fix it unless
   there is a reason not to.
6. **Read it back to the owner.** Walk through the three lists with the
   owner and get a clear yes before the assistant uses the file. Any change
   goes into the answers file, then rebuild and recheck (steps 4-5).
7. **Hand-edits are fine** - re-run `check` after any edit.

## What the checker looks for

Errors (exit code 1):

- Title is not `# Client rules: <business>`.
- A required section is missing (`About`, `May do alone`, `Must ask first`,
  `Never does`, `When unsure`) or a rule list is empty, or the three lists
  are out of order.
- `About` does not name the Owner.
- The same action is in two lists.
- A risky word (pay, refund, delete, cancel, sign, discount, password,
  legal, medical, …) appears in an item under "May do alone".
- Hype or overclaiming wording ("guarantee", "revolutionary", … - full list in `BANNED_WORDS` in rules_tool.py).
- A placeholder is left in (`TODO`, `TBD`, `{{…}}`).

Warnings: an item listed twice in the same list; an item longer than 25
words.

The checker reads words, not meaning. A clean result means the file has
the right shape and no known red flags; the owner's read-through in step 6
is still the real check.

## Worked example 1: Maple Lane Bakery

Answers: [examples/maple-lane-bakery/answers.json](examples/maple-lane-bakery/answers.json)
(owner Rosa Quill, asks by text message).

During sorting (step 2), Rosa first listed "offer a discount to an unhappy
customer" as something the assistant could do alone. The checker would flag
it (`discount`), so it went to "Must ask first". "Promise a product is free
of an allergen" went to "Never does" because a wrong answer could hurt
someone.

```
$ python3 rules_tool.py build examples/maple-lane-bakery/answers.json -o examples/maple-lane-bakery/RULES.md
$ python3 rules_tool.py check examples/maple-lane-bakery/RULES.md
OK
```

Result: [examples/maple-lane-bakery/RULES.md](examples/maple-lane-bakery/RULES.md)

## Worked example 2: Northgate Bike Repair

Answers: [examples/northgate-bike-repair/answers.json](examples/northgate-bike-repair/answers.json)
(owner Dev Albers, one-person workshop, asks through the shared inbox).

Dev's first draft had "cancel a booking" under "may do alone". Running
`check` on that draft gave:

```
error: risky action under 'May do alone': 'Cancel a booking' (mentions cancel); move it to 'Must ask first' or 'Never does'
1 error(s)
```

The answer was narrowed: the assistant may book open slots alone, but
moving or cancelling a booking the customer did not ask to change is "Must
ask first". "Say a bike is safe to ride" is "Never does" - only Dev
inspects bikes.

Result: [examples/northgate-bike-repair/RULES.md](examples/northgate-bike-repair/RULES.md)

## Tests

```
python3 -m unittest discover -s skills/client-rules-file -t skills/client-rules-file
```

Offline, stdlib only.
