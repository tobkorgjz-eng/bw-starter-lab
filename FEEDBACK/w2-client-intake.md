# Feedback: w2-client-intake

Box: w2-client-intake · Branch: w2-skill-client-intake · Task: W2, skills/client-intake/

## What Discobox did well

- `discobox-access list` showed at once that no GitHub credential was held, so there was no guessing.
- The access request with narrow routes (this repo only: git push, GET, POST pulls, POST reviews, POST issue comments; no merge route) was answered within a few minutes, and the grant said its expiry plainly.
- Running the `wait` in the background let me write the skill while the request was pending.
- `git fetch origin` worked without a credential, so I could read W1's RULES.md vocabulary and match it.

## What got in the way

- The output of `discobox-access wait --json` has two JSON objects (a progress line, then the result), so a plain `json.load` on the file failed. Exact error:
  `json.decoder.JSONDecodeError: Extra data: line 2 column 1 (char 404)`
  Reading the last line instead worked. Small, but worth a note in the skill text.
- The "never the word p-r-o-o-f" rule also hits a test that checks for that word; I had to build the string from two parts in the test so the repo itself stays clean.
- W1's client-rules-file skill was not on a branch yet when I started, so I aligned with W1's earlier `starter-kit/rules/RULES.md` format (backticked `snake_case` action names under "May do alone", "Needs the owner's yes", "Never does"). If W1 picks a different format, `check_brief.py` will need a matching change.

## Rough time

- Reading the brief, checking identity, asking for access: ~4 min
- Reading W1's earlier rules format: ~2 min
- SKILL.md, questions, template, worked example: ~10 min
- check_brief.py and tests: ~8 min
- Feedback, commit, push, PR: ~5 min
