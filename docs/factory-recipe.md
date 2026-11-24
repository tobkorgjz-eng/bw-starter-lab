# Factory recipe: the 9-box Blade Works run

This is how one manager box and eight worker boxes built the Blade Works starter lab on 2026-11-24 (16:31 to about 17:15 UTC), including one review and fix round. It is written so someone else can repeat the run. Blade Works ("Runs by your rules, asks before it acts.") is a made-up business, and all data in the repo is made up.

Sources: the nine `FEEDBACK/*.md` files on this branch, the exact prompts in [`docs/prompts/`](prompts/), and the manager's notes. No token or credential appears here.

## 1. What the run produced

| Box | Branch | PR | What it built |
| --- | --- | --- | --- |
| manager | (none) | summary comment on #1 | Wrote the prompts, launched 8 boxes, approved 8 access requests, reviewed every branch, did a combined test run |
| w1-client-rules-file | `w1-skill-client-rules-file` | #7 (new) | `skills/client-rules-file/`: SKILL.md, `rules_tool.py` checker, 2 worked examples, 25 tests |
| w2-client-intake | `w2-skill-client-intake` | #6 (new) | `skills/client-intake/`: intake questions, client brief template, worked example, `check_brief.py` + tests |
| w3-upwork-proposal | `w5-upwork-helper` | #1 (reused) | `skills/upwork-proposal/`: fit score 1 to 5 with reasons, short honest draft, never sends; tests on 3 made-up posts |
| w4-booking-bot | `w3-demo-bots-booking` | #5 (reused) | `demo-bots/booking/`: self-contained `demo.html`, confirms before booking, prompt-injection tripwire, tests |
| w5-faq-bot | `w4-demo-bots-faq` | #2 (reused) | `demo-bots/faq/`: self-contained `demo.html`, answers only from its FAQ, hands off to a person, tests |
| w6-starter-kit | `w2-starter-kit-templates` | #4 (reused; #3 merged into it) | `starter-kit/` client pack and repo-root `run_tests.py` (+ its own test) |
| w7-reviewer | `w7-reviewer` | #8 (new) | Review comments on every PR, scan script in `tools/`, notes in `docs/reviews/` |
| w8-scribe | `w8-scribe` | #9 (new) | This file, `docs/discobox-feedback.md`, the collected FEEDBACK files |

Combined check (manager, on a local merge of all 8 branches that was thrown away afterwards and never pushed): `Total: 10 folders, 10 passed, 0 failed, 206 tests` before the review round. After the fix round the same check ran 288 tests (manager's count).

Nothing was merged into main. Nothing was pushed to main. No force push.

## 2. Setup before you start

1. **A public GitHub repo** with one initial commit made under a no-reply identity (here `tobkorgjz-eng/bw-starter-lab`). Being public lets every box `git fetch origin` and do REST GETs with no credential.
2. **A manager discobox that has discobox API access**, so it can create boxes and answer their access requests. Only a person can turn this on.
3. **A GitHub secret for the project, plus a delegation of it to the manager.** In this run a `github` delegation was already bound to the manager (host-wide: `api.github.com, github.com`). That let the manager approve worker requests without a person.
4. **Test the secret before launching anyone.** The manager should make one authenticated call, such as `GET https://api.github.com/repos/<owner>/<repo>` with its own grant, and expect 200. This run skipped that step: the secret was bad, and all nine boxes lost about 18 minutes (see section 6).
5. **Ask under the project secret's own name.** The manager's first use grant came out as `github-2`. The person asked everyone to use `github`, so the manager had to ask again (about 10 minutes). Use the name already bound to the project from the start.

## 3. How each prompt is built

Every worker prompt is three parts joined in this order. All eight files in `docs/prompts/` were checked to match exactly.

1. [`docs/prompts/common.md`](prompts/common.md): the shared header (context, test convention, wording rules, FEEDBACK request, what the final message must say).
2. `Your box name: <box>`, then `Your task (Wn): ...` and `Branch: ...`. These are the only lines that differ between boxes; see the files `docs/prompts/w1-client-rules-file.md` to `w8-scribe.md`.
3. [`docs/prompts/rules.md`](prompts/rules.md): the box rules, word for word. They are copied below because they are what kept the run safe.

```
Box rules for you and for every worker you start (put them in each worker's prompt, word for word):
1. Clean repo: work only in tobkorgjz-eng/bw-starter-lab. Before the first commit, run git log --format='%an <%ae>' and confirm every existing commit uses only the no-reply identity below; if not, stop and say so.
2. Git identity, set in this repo only (never --global, never environment variables): git config user.name "tobkorgjz-eng" and git config user.email "359593544+tobkorgjz-eng@users.noreply.github.com". Before the first commit, show git var GIT_AUTHOR_IDENT and git var GIT_COMMITTER_IDENT.
3. GitHub access: request access with discobox-access (github.com + api.github.com, this repo only) and wait for the answer. Manager: your own request is answered by a person – wait for it. Workers: your manager answers yours. Never stop just because access needs someone's answer; never work around a refusal.
4. gh pr create does not work in a box (GraphQL is blocked). Open pull requests with the GitHub REST API: POST https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls (head = your branch, base = main). Reviews and comments also via REST (POST .../pulls/N/reviews with event COMMENT; POST .../issues/N/comments).
5. One approval: each worker asks once; the manager reads each request (repo, routes, no merge route) and approves it once under its delegation, limited to this repo, push + open PR + comments, max 2 hours. Never approve a merge route, a wider repo pattern or another repo.
Also: never print, log, write or commit any token or credential (FEEDBACK files included); no pip install or any other install; code and tests make no network calls; do not merge any pull request; do not push to main; no force push; made-up data only.
```

Task design notes that worked:

- **Reuse existing PRs where they exist** (W3 on #1, W4 on #5, W5 on #2, W6 on #4) with normal commits and a comment that describes the update. W6 brought #3 in with a plain `git merge origin/w1-starter-kit-rules` and left #3 open with a pointer comment.
- **Name the neighbouring worker** when two tasks must line up (W1 reads what W2 writes). W2 still had to guess W1's format from an older branch, because W1 had not pushed yet. Next time, fix the shared input format in both prompts.
- **Gate the reviewer and the scribe on a typed word** ("GO REVIEW", "GO SCRIBE", "RE-REVIEW <n>", "REFRESH W7"). They prepare first and act once the builders have pushed.
- **Ask for a single test runner** (`run_tests.py`, one subprocess per test folder) so the manager can check every branch with one command.

## 4. Order of work (as it happened)

| Time (UTC) | Event |
| --- | --- |
| 16:31 | Manager starts: reads skills, checks identity and history, maps open PRs (5 min) |
| ~16:34 | Manager writes the 8 prompts and launches all 8 boxes in one loop with `discobox run --from-json` (prompt passed through `jq`) (~1 min) |
| 16:35–16:38 | Each worker checks rules 1–2 and sends one `discobox-access request --json ... "wait": true` with routes for this repo only (git, GET repo, POST pulls, POST reviews/comments; no merge). Workers keep coding while it waits. |
| 16:35–16:38 | Manager lists requests (`discobox secret request ls -o json`), checks each with a small script (repo only, no merge route), and approves each once with `--for 2h`. Each took about 1 to 3 minutes. |
| ~16:38–16:56 | **Every authenticated GitHub call from every box returns 401 "Bad credentials".** The project secret itself was bad. Workers commit locally and wait. The manager tells each worker, using `discobox send`, not to send a second request. |
| ~16:55–16:56 | A person (JZ) updates the `github` secret. The first 200 arrives at 16:56 (the manager's notes say 16:58 for its own shell). Each worker's first approval starts working **with no re-approval**, once it runs `eval "$(discobox-access env)"` in the same command as the push. |
| 16:56–17:00 | Workers push and open or update PRs through REST. Manager types "GO REVIEW" to W7. |
| ~17:00 | Manager reviews each branch in its own `git worktree`, runs `unittest discover` per folder, does the combined merge test (206 tests pass), and makes the W1/W2 integration fix. |
| ~17:00–17:08 | W7 posts reviews on every PR. Builders fix the findings on their own branches (one round, same approvals) and update their FEEDBACK files. Tests: 206 → 288. |
| ~17:05 | Manager copies its FEEDBACK file and the prompts into the scribe box and types "GO SCRIBE". |
| ~17:12 | Manager types "REFRESH ALL"; the scribe copies every FEEDBACK file again, byte for byte from its branch, so a merge of all branches has no conflict on `FEEDBACK/`. |

### One review and fix round

After the builders pushed, W7 reviewed every PR (a REST review with event `COMMENT`, with file:line, a failing case and a suggested fix for each finding). Each builder fixed its findings on the same branch with the same approval. No box sent a new access request for the fix round.

The real issues W7 found (as summarised by the manager):

- client **Notes** text could override the rules in the rules file
- a "Never does" rule could be bypassed by spelling the action differently
- **injected job post text** in the Upwork proposal skill: the post is now treated as data, and injection phrases, contact details and links are flagged

From the builders' own files: W2 fixed three findings on #6 (18 → 25 tests). W3 fixed the injection handling and wording on #1, and fixed one test that matched the company name "Blade Works" against its own "never says works" check. W4 made cancelling require a name and made matching respect word boundaries on #5. W5 stopped ordinary questions ("act as", "from now on") from being flagged as injection on #2. W6 aligned action names and the "information, not instructions" line across the prompts on #4.

Across all branches the tests went **from 206 to 288**. One round was enough. Builders said the review format (file:line + failing case + fix) meant no back-and-forth was needed.

## 5. Commands that worked (copy these)

Push with the granted variable. Run the `eval` **in the same command** as the push, because shell state does not carry from one tool call to the next:

```sh
eval "$(discobox-access env)"; git -c credential.helper='!f(){ echo username=x-access-token; echo "password=$GH_TOKEN"; }; f' push -u origin <branch>
```

Open a PR with REST. Send real JSON, or the egress refuses the request and curl prints nothing (see the feedback doc):

```sh
curl -s -X POST -H "Authorization: Bearer $GH_TOKEN" -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" --data-binary @pr.json \
  "https://api.github.com/repos/<owner>/<repo>/pulls"
```

Tell a bad secret apart from a bad route: `discobox-access audit --host api.github.com --since 10m`. A plain `401` (not `BLOCKED`) with body `{"message": "Bad credentials"}` means the secret is bad. Sending another access request will not fix it.

Wait without using tokens: run a background loop that runs `discobox-access env` and one allowed GET every 60 to 120 seconds, and stops at the first 200.

Steer a worker from the manager: `discobox capture <id> --trim`, then `discobox send <id> "..." && discobox send-key <id> Enter`.

Check that tests really pass offline: `unshare -rn python3 -m unittest discover -s <folder> -t <folder>` (used by W7).

Quote every URL that contains `?` in zsh, for example `"...pulls?state=all"`.

## 6. Time taken

Rough minutes from each box's FEEDBACK file. "Lost to bad secret" counts debugging plus idle waiting where the box reported it.

| Box | Total (approx.) | Lost to bad secret | Review fix round |
| --- | --- | --- | --- |
| manager | 69 | 18 (+10 re-asking under the right secret name) | (review, merge test and integration fix are in the total) |
| w1-client-rules-file | 38 | 19 | not stated |
| w2-client-intake | 50 | 6 debugging, ~20 wall clock | 15 |
| w3-upwork-proposal | 60 | 6 debugging, ~18 wall clock | 27 |
| w4-booking-bot | 65 | 6 debugging (+1 denied second request) | 15 |
| w5-faq-bot | 54 | not stated; ~18 wall clock | 10 |
| w6-starter-kit | 73 | 22 (+4 on an empty variable after the fix) | 15 |
| w7-reviewer | 105 | idle wait, not counted | (review is its main task) |
| w8-scribe | ~60 | 20 | 10 (refresh + updates) |

The whole run took about 45 minutes of wall clock, and about 18 of them were spent waiting on the bad secret, with all nine boxes waiting at once.

## 7. What to change next time

1. Before launching any worker, have the manager make one authenticated GET with the project secret (section 2, step 4).
2. Ask under the project secret's own name (`github`), never a new name such as `github-2`.
3. Put the push one-liner and the `Content-Type: application/json` note from section 5 into `common.md`, so no box has to discover them.
4. Tell workers how to reach the manager. In this run `ListAgents` showed "No reachable agents" in every worker, so W4 sent a second access request to get attention. A line in the prompt such as "If blocked, write BLOCKED: <reason> as your last line; the manager watches with `discobox capture`" would cover it.
5. Rule 1 checks authors only (`%an <%ae>`). The initial commit's committer was `GitHub <noreply@github.com>` (made in the web UI). W5 noticed this and was unsure whether it passed. Write the rule as `git log --format='%an <%ae> | %cn <%ce>'` and list both allowed no-reply identities.
6. Fix the shared input format between W1 and W2 in both prompts, instead of telling them to "line up".
7. Plan the review and fix round from the start: tell builders a review is coming, to fix on the same branch with the same approval, and to add a "Review fixes" section to their FEEDBACK file. Tell the scribe to copy FEEDBACK files only after the fix round, byte for byte.
8. Tell every box never to probe a write endpoint with a real request. All boxes share one GitHub account, so a test `POST .../reviews` with body `{}` created a real pending review on PR #3 that no box could remove (see the feedback doc).
9. Use `curl` for REST calls from a box. In W7's box, Python `urllib` did not reach the egress, while `curl` did.
