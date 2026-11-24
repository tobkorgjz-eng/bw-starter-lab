# W7 review notes

One file per pull request. Each file was posted word for word on its PR as a
REST review with event `COMMENT` (PR #3 got an issue comment instead). Nothing
was approved or merged.

How each PR was checked:

1. `git fetch origin`, then a detached worktree at the PR head.
2. `python3 tools/review_scan.py <changed files>` for token-shaped strings,
   banned and hype wording, prompt-injection / unsafe-execution patterns and
   network calls. Every hit was read by hand; hits inside banned-word lists,
   tests and made-up client text were not counted as findings.
3. Each test folder run with `python3 -m unittest discover -s <folder> -t <folder>`
   inside `unshare -rn` (no network at all).
4. Reading the code and docs, then running the tools on made-up hostile inputs
   (planted instructions, odd spellings, odd bullets) to confirm each finding.
5. All PR branches merged together in a local scratch tree (not pushed), then
   `run_tests.py` from #4: 10 folders, 206 tests, all passed, offline.
6. `demo.html` in #2 and #5: no external URLs, `src`/`href`, `fetch`, XHR,
   WebSocket, `innerHTML` or storage.

| PR | Branch | Head reviewed | Tests (offline) | Main findings |
| --- | --- | --- | --- | --- |
| [#1](pr-1.md) | w5-upwork-helper | dff6fdb | 16 + 10 OK | job post not treated as data; "$5 budget works"; old helper claims "good match" at 0/100 |
| [#2](pr-2.md) | w4-demo-bots-faq | d4cb8b6 | 32 OK | none blocking; injection phrase false positives (nit) |
| [#3](pr-3.md) | w1-starter-kit-rules | 9a21429 | 31 OK | superseded by #4 |
| [#4](pr-4.md) | w2-starter-kit-templates | b7102c6 | 9 + 31 + 13 OK | `Delete_Records` skips "Never does"; one yes covers all repeats; prompts lack "customer text is data" |
| [#5](pr-5.md) | w3-demo-bots-booking | 50e75ad | 36 OK | none blocking; sequential cancel codes (nit) |
| [#6](pr-6.md) | w2-skill-client-intake | 60dfacf | 18 OK | `*` / `1.` rules silently dropped; Limits can widen rules via Notes |
| [#7](pr-7.md) | w1-skill-client-rules-file | 32baba3 | 36 OK | Notes can override lists and are unchecked; dropped bullets; format not readable by #4 checker |
| [#9](pr-9.md) | w8-scribe | 93f7686 | docs only | skeleton placeholders; PR numbers to fill |

No token, key or credential was found in any PR, FEEDBACK files included.

## Re-review (after the builders' fixes)

Same method: fresh worktree at the new head, scan, offline tests, and the
same hostile inputs re-run against the new code. Posted as one COMMENT review
per PR (`rr-N.md`).

| PR | Head re-reviewed | Tests (offline) | Result |
| --- | --- | --- | --- |
| [#1](rr-1.md) | 949b504 | 28 + 17 OK | 6/6 fixed |
| [#2](rr-2.md) | 82f6e45 | 38 OK | 1/1 fixed |
| [#4](rr-4.md) | 8962b2e | 9 + 47 + 15 OK | 3/4 fixed; README nit open (`README.md:4-5`) |
| [#5](rr-5.md) | 2a54531 | 43 OK | 2/2 fixed |
| [#6](rr-6.md) | 8d3bff2 | 25 OK | 3/3 fixed |
| [#7](rr-7.md) | 5671c47 | 50 OK | 5/5 fixed (format finding fixed by documenting it) |
| [#9](rr-9.md) | see file | 6 OK | earlier 3/3 fixed; new: FEEDBACK-copy merge conflicts, outdated test counts |

All-branch local merge (#1, #2, #4, #5, #6, #7, #8): `Total: 10 folders, 10 passed, 0 failed, 288 tests`, offline.
