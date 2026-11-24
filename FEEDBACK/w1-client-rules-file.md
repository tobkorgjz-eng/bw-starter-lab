# Feedback: w1-client-rules-file

Box: w1-client-rules-file. Task: W1, `skills/client-rules-file/` (SKILL.md,
rules checker `rules_tool.py`, tests, two worked examples).

## What Discobox did well

- The access request (`discobox-access request --json ... --wait`) was
  answered in about a minute; routes could be scoped to this one repo and
  to the exact REST endpoints (pulls, reviews, issue comments), with no
  merge route.
- `discobox-access list` made it easy to confirm what was granted and when
  it expires.
- `git fetch origin` worked without a credential (public repo), so I could
  look at the other open branches before starting.

## What got in the way

- Push blocked: the granted GitHub credential returns 401 Bad credentials
  (see below). No manager or other session was reachable (ListAgents
  showed none), so this needs a person to check the credential.
- The access request runs as a long wait, so I ran it in
  the background and wrote code meanwhile; that worked but needs the
  worker to remember to check the result before pushing.
- An older branch `origin/w1-starter-kit-rules` (starter-kit/rules/) covers
  a similar idea with a JSON plan + approvals checker. This skill is
  separate (it builds the rules file from intake answers) and does not
  touch that folder; a later pass may want to line the two up.

## Exact error text

The GitHub credential was granted (`discobox-access list` shows
`github (GH_TOKEN → github.com, api.github.com) [expires 2026-11-24T18:35:20Z]`),
but GitHub rejected it. The egress audit shows these as 401 from GitHub,
`blocked: false`, so the routes were fine and the credential behind them
was not accepted.

`git push` with a credential helper reading GH_TOKEN:

    remote: Invalid username or token. Password authentication is not supported for Git operations.
    fatal: Authentication failed for 'https://github.com/tobkorgjz-eng/bw-starter-lab.git/'

`git push` with no helper:

    fatal: could not read Username for 'https://github.com': No such device or address

`GET https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab` with `Authorization: Bearer $GH_TOKEN`:

    {"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest", "status": "401"}

After the person updated the project's GitHub secret, the same
credential worked at 16:56 (about 19 minutes after the first 401) with no
new access request; `eval "$(discobox-access env)"` and a retry of the push
was enough.

Opening the PR with `curl --data @pr.json` (which sends a form content
type) was refused by the egress before it left; the audit said:

    403 BLOCKED  POST https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls
        reason: route: route POST api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls cannot tell what method the body's _method names: it does not parse, or names one twice

curl printed nothing in this case. Adding `-H "Content-Type: application/json"`
(and `--data-binary`) fixed it; the PR opened on the next try.

## Rough time per part

- Repo checks, git identity, access request: ~2 min (approval wait ~1 min)
- rules_tool.py (build + check + CLI): ~5 min
- Two worked examples + SKILL.md + INPUT-FORMAT.md: ~5 min
- Tests (25, offline): ~3 min
- Commit, push, PR via REST, this file: ~4 min
- Waiting for the GitHub secret fix: ~19 min
