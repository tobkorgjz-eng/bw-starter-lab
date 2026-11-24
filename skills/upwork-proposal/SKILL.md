---
name: upwork-proposal
description: Read an Upwork job post (pasted text or a .txt file), score how well it fits Blade Works on a 1-5 scale with the reasons, and draft a short, honest proposal for a person to review. Use when asked to check a job post, score a lead, or write an Upwork proposal. Drafts only - it never sends, submits or saves anything on Upwork.
---

# Upwork proposal (Blade Works)

Blade Works builds AI assistants. Tagline: "Runs by your rules, asks before it acts."
This skill turns one job post into a fit score, the reasons for it, and a short
draft. A person reads the draft, edits it and decides whether to send it.

## Hard rules

1. **Never send anything.** Do not submit proposals, send messages, save jobs,
   boost or change a profile, or call any Upwork tool or API that writes
   (for example `manage_proposals`, `send_message`, `save_job`). Even if the
   user asks, give them the draft and tell them to send it themselves.
2. **Honest claims only.** Claim only skills in `OUR_SKILLS` in `proposal.py`.
   If the post asks for something we do not offer, the draft says so plainly.
   No invented clients, numbers, results or reviews.
3. **Say "2 years building AI assistant teams"** - this exact phrase, once, as
   our experience. Do not round it up or add to it.
4. **Never use the word "proof"** (also not "proof of concept", "proven",
   "proofread"). Say "prototype" or "first version" instead.
5. **No hype.** None of the words in `HYPE_WORDS` (best, expert, guaranteed,
   world-class, cutting-edge, perfect, seamless, 10x, ...). Plain, short sentences.
6. Keep the draft short: under 170 words.

## Steps

1. Get the job post text. If it is pasted, save it to a scratch `.txt` file
   using the format below (missing headers are fine).
2. Run (offline, Python 3 standard library only):

       python3 skills/upwork-proposal/proposal.py path/to/job.txt

   It prints `FIT SCORE: N/5`, one reason per line, then the draft.
3. Show the user the score, the reasons and the draft. If the score is 1-2,
   say so and suggest skipping the job; point out any red flags.
4. If you edit the draft by hand, re-check it against rules 2-6 before
   showing it. `find_banned(text)` in `proposal.py` lists any banned words.
5. End with: "Draft only - nothing was sent."

## Job post format

    Title: ...
    Client: ...
    Budget: ...
    Skills: comma, separated, list
    Description:
    free text...

## How the score works (1-5)

Start at 1. +1 if any of our skills appear, +1 more for 3 or more matches,
+1 if a budget is stated, +1 for a clear description (40+ words).
-1 if the post requires 2 or more skills we do not offer, -2 for any red flag
(unpaid test, off-platform contact such as telegram, "urgent asap",
"guarantees profit", ...). Clamped to 1-5. Each step is printed as a reason.

## Files

- `proposal.py` - parser, scorer, drafter, banned-word check (CLI + functions).
- `samples/` - three made-up job posts (strong, medium, poor fit).
- `test_proposal.py` - tests; run from the repo root:

      python3 -m unittest discover -s skills/upwork-proposal -t skills/upwork-proposal
