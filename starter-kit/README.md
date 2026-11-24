# Starter Kit

Everything needed to set up a new client assistant for Blade Works:
**runs by your rules, asks before it acts.** All examples use made-up
businesses (the main one is "Maple Lane Bakery").

## What is in the pack

| Path | What it is |
| --- | --- |
| `rules/RULES.md` | House rules: what the assistant may do alone, what needs the owner's yes, what it never does |
| `rules/check_rules.py` | Checks a bot's planned actions against `RULES.md` (ALLOW / ASK / BLOCK) |
| `templates/prompts/` | Prompt templates: receptionist, scheduler, follow-up writer |
| `templates/new-client-layout/` | Empty folder layout to copy for each new client |
| `templates/onboarding-checklist.md` | Step-by-step setup checklist |
| `templates/CLIENT-README.md` | Plain-English guide to hand to the client |

## Setting up a new client

1. Copy `templates/new-client-layout/` to a folder named after the client,
   for example `maple-lane-bakery/`.
2. Copy `rules/RULES.md` into the client's `rules/` folder and edit the three
   lists with the owner. Anything not listed counts as "ask first".
3. Copy the prompt templates the client needs into their `prompts/` folder
   and replace every `{{PLACEHOLDER}}`.
4. Check a sample plan against the client's rules:

   ```sh
   python3 starter-kit/rules/check_rules.py starter-kit/rules/example_plan.json
   ```

   The owner's yes is given separately (`--approvals FILE` or
   `--approve ACTION`). The assistant cannot approve its own actions.
5. Work through `templates/onboarding-checklist.md`, then fill in and send
   `templates/CLIENT-README.md` to the client.

## Folder layout for one client

```
<client-name>/
  config/     business details: hours, services, contacts (no secrets)
  rules/      the client's own RULES.md
  prompts/    filled-in prompt templates
  knowledge/  FAQs and reference notes the assistant may use
  logs/       conversation logs kept for review
  notes/      onboarding notes and test results
```

## Tests

Python 3 standard library only, no network calls. From the repo root:

```sh
python3 run_tests.py                                                  # every test in the repo
python3 -m unittest discover -s starter-kit/rules -t starter-kit/rules
python3 -m unittest discover -s starter-kit/templates -t starter-kit/templates
```

The tests check the rules checker's behaviour and that the templates,
checklist and layout are complete and well-formed. They do not test how a
live assistant behaves; that is what the onboarding test conversations are for.
