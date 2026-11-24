# FEEDBACK - w3-upwork-proposal

Task: build `skills/upwork-proposal/` on top of PR #1 (branch `w5-upwork-helper`).

## What Discobox did well
- `discobox-access request --json ... wait` was simple: one JSON request with
  five narrow routes (this repo only: git push/fetch, GET repo, POST pulls,
  PATCH pulls/1, POST issues/1/comments). The manager approved it in under a minute.
- `discobox-access audit` made the auth problem easy to pin down. It showed an
  off-route call (`GET /user`) as `BLOCKED` with the reason, and on-route calls
  as a plain upstream 401. So the egress was letting the requests through and
  GitHub was rejecting the credential.
- Public `git fetch` and unauthenticated REST GETs worked without any credential.

## What got in the way
- After the grant, `GH_TOKEN` was not in the tool shell until
  `eval "$(discobox-access env)"` (expected, the skill documents it).
- With the variable set, GitHub rejected the credential on every allowed route,
  both for `git push` and for REST. Tried Bearer and `token` schemes, and retried
  after a short wait. Exact errors:
  - git push: `remote: Invalid username or token. Password authentication is not supported for Git operations.`
    then `fatal: Authentication failed for 'https://github.com/tobkorgjz-eng/bw-starter-lab.git/'`
  - REST GET pulls/1: `HTTP/2 401` with `"message": "Bad credentials"`
  - audit line: `401  GET https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls/1` (not blocked)
- Cause, confirmed by the manager: the project's GitHub secret itself is
  invalid. It fails the same way for every box, the manager included, so the
  routes and the approval are fine. Per the manager I did not send a second
  access request. I committed locally and waited for a person to update the
  secret.
- A person updated the secret about 18 minutes later (first 200 at 16:56Z).
  After `eval "$(discobox-access env)"`, the push, PATCH pulls/1 and the PR
  comment all worked on the first try with the same approval.
- Waiting cost no tokens: a background loop re-ran `discobox-access env` and
  one allowed GET every 60 s, and stopped on the first 200.
- ListAgents showed no reachable manager session, so I could not message the
  manager from the box.

## Design notes
- Client text that contains "proof" or a hype word (for example the sample
  title "Best expert needed ... proof of concept") is not quoted in the draft.
  An early version rewrote such text and produced broken sentences, so I
  dropped rewriting.
- An early synonym mapped "bot" to "chatbot", so a crypto *trading* bot counted
  as a skill match. That was a dishonest claim, so I removed the synonym and
  added a test for it.
- The hype check covers the draft. The score reasons may quote a client's red
  flag (for example "guarantees profit"). "proof" is not allowed anywhere in
  the output.
- SKILL.md and `proposal.py` contain the word "proof" only where they state
  and enforce the rule against it.

## Rough time (minutes)
- Repo check, identity, branch checkout, reading upwork-helper: 3
- Access request and approval wait: 2
- Skill code, samples, SKILL.md, README: 12
- Tests and the fixes they led to: 6
- Debugging the GitHub 401: 6
- FEEDBACK and preparing the PR update: 4
