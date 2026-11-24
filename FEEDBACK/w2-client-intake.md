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

## Blocker: push and PR could not be done

The access request (sreq_k6nt1afpayygah0k) was granted (github, GH_TOKEN, github.com + api.github.com, expires 2026-11-24T18:35:19Z), but GitHub rejected the credential on every try. The egress let each request through (audit shows `"blocked":false`), so the routes were fine; the credential behind the grant was not accepted by GitHub.

Exact text from `git push -u origin w2-skill-client-intake`, first without a helper:
`fatal: could not read Username for 'https://github.com': No such device or address`
then with a credential helper that reads GH_TOKEN from the environment:
`remote: Invalid username or token. Password authentication is not supported for Git operations.`
`fatal: Authentication failed for 'https://github.com/tobkorgjz-eng/bw-starter-lab.git/'`

Exact text from `GET https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab` with `Authorization: Bearer $GH_TOKEN`, six tries over about 2 minutes:
`{"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}`

- Time lost on this: ~6 min.
- What would help: Git not having to be told how to use GH_TOKEN (a credential helper set up in the box by default), and a clearer sign of whether the secret bound to a grant is a valid GitHub token before the grant is marked done.

Manager's diagnosis: the 401 "Bad credentials" comes from the project's GitHub secret itself (it fails the same way for every box, the manager included), not from this box's routes. No second access request was sent; the box waited for a person to update the secret.
- Resolved: after the secret was updated, the token was accepted at 16:56 UTC (about 20 minutes after the first 401); the branch was pushed and the PR opened with the same single approval.

## Review fixes (W7 review on PR #6)

- Fixed three findings: rules lines with any list marker, limits that only narrow the lists, and a drafted (not sent) topics message. Tests went from 18 to 25.
- What went well: the review gave file:line, a way to reproduce, and the fix it wanted, so no back-and-forth was needed. The existing approval covered reading the review and posting the comment.
- Time: reading the review ~3 min, code and tests ~8 min, cross-check with #7's `from-brief` ~2 min, comment ~2 min.
