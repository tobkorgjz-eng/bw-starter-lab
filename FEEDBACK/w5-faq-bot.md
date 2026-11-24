# FEEDBACK: w5-faq-bot

Task: finish demo-bots/faq/ on the existing PR #2 (branch w4-demo-bots-faq).

## What Discobox did well
- `discobox-access request --wait` worked as described. I asked for repo-only
  routes (git push to this repo, GET on the repo API, POST pulls / issue
  comments / reviews, no merge route), the manager approved it, and the
  answer came back as JSON with the expiry. I could keep working while it
  was pending.
- `discobox-access list` made it clear up front that I held no GitHub
  credential, so there was no guessing.
- `git fetch origin` against the public repo worked without credentials, so
  checking out the existing PR branch needed no approval.
- `node` happened to be installed, so the demo page's own JS could be tested
  offline against the Python bot. The test skips when node is missing.

## What got in the way
- **Blocking: push and PR comment failed.** The access request was granted
  (`discobox-access list` shows `github (GH_TOKEN → github.com, api.github.com)
  [expires 2026-11-24T18:36:41Z]`) and the egress did not block anything
  (`discobox-access audit` shows status 401, `blocked: false`), but GitHub
  rejects the credential behind the stand-in. Verbatim:
  - `git push`: `remote: Invalid username or token. Password authentication is not supported for Git operations.`
    then `fatal: Authentication failed for 'https://github.com/tobkorgjz-eng/bw-starter-lab.git/'`
  - REST `GET /repos/tobkorgjz-eng/bw-starter-lab`: `{"message": "Bad credentials", "status": "401"}`
  This looks like the delegated GitHub secret upstream is expired or revoked.
  Because of the one-approval rule I did not ask again and did not try any
  workaround. The commits are on the local branch, ready to push.
  The manager confirmed it is the project's GitHub secret itself (it fails
  for every box, manager included), not the routes, and said to wait for a
  person to update the secret, then retry.
- The manager box was not reachable from this box (`ListAgents`: no reachable
  agents), so I could only report this here and in my final message.
- Nothing blocking. One self-inflicted bug: with `node -e`, the first
  extra argument is `process.argv[1]`, not `argv[2]`. Error text, verbatim:
  `TypeError [ERR_INVALID_ARG_TYPE]: The "path" argument must be of type string or an instance of Buffer or URL. Received undefined`
- The skill text is long; finding the exact route syntax for
  "issues/*/comments" took a careful read of the route grammar.
- The initial commit's committer is `GitHub <noreply@github.com>` (made in the
  web UI), not the repo's own no-reply address. It is still a no-reply
  identity, so I went ahead, but the rule's wording ("only the no-reply
  identity below") could be read either way.

## Rough time per part
- Reading the branch and planning: ~5 min
- Access request (waiting ran in the background): ~3 min of my time
- Bot changes (fallback, injection guard, respond()): ~8 min
- demo.html (inline logic + hand-off button): ~8 min
- Tests (honesty, injection, page checks, node parity): ~12 min
- README, commit, push, PR comment: ~8 min
