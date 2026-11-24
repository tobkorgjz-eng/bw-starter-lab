---
name: client-intake
description: Run the first intake conversation with a new small-business client of Blade Works and turn the answers into a one-page client brief. Use when onboarding a new client, before any assistant is set up. The brief's three rules lists (may do alone, needs the owner's yes, never does) are the input for the client-rules-file skill.
---

# Client intake

Blade Works sets up AI assistants that run by the client's rules and ask
before they act. This skill covers the first step: learning about a new
client and writing it down on one page.

## When to use

- A new small-business client has said yes to a first call.
- An existing client's business has changed enough that the brief is out of date.

Do not use it to set up tools, connect accounts or write prompts. Those come later.

## Files

| File | What it is |
| --- | --- |
| `questions.md` | The intake questions, grouped in seven sections. |
| `brief-template.md` | The one-page client brief to fill in from the answers. |
| `example-brief.md` | A filled-in brief for a made-up business (Fernhill Bike Repair). |
| `check_brief.py` | Optional checker: is a filled brief complete, and are its rules lists usable by the next step? |

## Steps

1. **Before the call.** Draft a short message listing the section headings
   of `questions.md` for the person running intake to send, so the client
   can think ahead. Do not send it yourself. Say in the draft that nothing
   will be connected or changed during intake.
2. **Run the call.** Ask the questions in `questions.md` in order. Write the
   client's own words where you can. If they do not know an answer, write
   `unknown — ask again by <date>` rather than guessing.
3. **Rules questions (section 5) need extra care.** For each task the client
   mentions, ask which of three lists it belongs on:
   - **May do alone** — the assistant does it without asking.
   - **Needs the owner's yes** — the assistant asks first and waits for a clear yes.
   - **Never does** — the assistant refuses, even if asked.
   If the client is unsure, put it on **Needs the owner's yes**. Anything not
   on any list is treated as needing the owner's yes.
4. **Fill in the brief.** Copy `brief-template.md` to the client's folder
   (for example `clients/<client-slug>/brief.md`) and fill in every section.
   Keep it to one page. Each rules line must start with a short action name in
   backticks, in `snake_case`, then ` — ` and a plain description:
   `` - `send_email` — send any email to a customer. ``
   Keep only rules lines inside the three lists; put notes elsewhere.
   "Limits and exceptions" may only narrow the lists (for example "quotes
   over 150 need the owner's yes"), never widen them. If a task should move
   to a freer list, change the list itself.
5. **Check it.** Run
   `python3 skills/client-intake/check_brief.py clients/<client-slug>/brief.md`.
   It reports missing sections, unfilled placeholders, badly formed rules
   lines (whatever list marker is used), other text inside a rules list, any
   action that sits on two lists, and warns when a "Limits and exceptions"
   line says "without asking" or "alone". Fix what it reports.
6. **Read it back.** Send the brief to the client and ask them to confirm or
   correct it, especially the three rules lists. Record the date and who
   confirmed it in the brief's "Sign-off" section. Until that is filled in,
   the brief is a draft.
7. **Hand off.** Once confirmed, turn the brief into the answers file for
   the `client-rules-file` skill with exactly this command:
   `python3 skills/client-rules-file/rules_tool.py from-brief brief.md -o answers.json`
   (use the brief's real path, for example `clients/<client-slug>/brief.md`).
   That skill then writes the client's rules file from `answers.json`.

## Ground rules for the person running intake

- Ask, do not assume. A missing answer is better than a wrong one.
- Do not collect passwords, keys or login details during intake. If the
  client offers one, tell them not to send it and do not write it down.
- Collect only the personal details needed to contact the client's named
  people. Do not record customers' personal details.
- Describe what the assistant will do in plain terms. Make no promises about
  results, savings or time saved.
