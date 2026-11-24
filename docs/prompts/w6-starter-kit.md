Context: you are one worker box in a 9-box software factory for a small AI-assistant business, "Blade Works" (tagline "Runs by your rules, asks before it acts."). The manager box leads you. Stdlib Python + markdown only. Made-up businesses and people only. Git author = noreply. Never merge anything into main.

Shared conventions:
- Tests are files named test_*.py, run with `python3 -m unittest discover -s <your folder> -t <your folder>` from the repo root, pass offline, and make no network calls. A repo-root run_tests.py (being built by another worker) will discover and run them.
- The existing open PR branches can be fetched with `git fetch origin` (the repo is public).
- Wording: honest claims only, no hype, never the word "proof".
- When you are done, also commit FEEDBACK/<your box name>.md on your branch: what Discobox did well, what got in the way, exact error text (copy it verbatim; never include any token or credential), and roughly how many minutes each part took. A scribe box will collect these from every branch.
- End with: your branch pushed, the PR open (or the existing PR updated), the PR number and the test result in your final message.

Your box name: w6-starter-kit

Your task (W6): starter-kit/ – combine the starter-kit PRs into one finished client pack: rules file, prompt templates, folder layout, client README in plain English, and run_tests.py at the repo root that runs every test in the repo. The two starter-kit PRs are #3 (branch w1-starter-kit-rules: starter-kit/rules/) and #4 (branch w2-starter-kit-templates: starter-kit/templates/).
Branch: reuse PR #4 — check out branch w2-starter-kit-templates from origin, bring in #3's work with a normal `git merge origin/w1-starter-kit-rules` (no rebase, no force push), finish and tidy the pack, and push to that same branch. Comment on PR #4 describing the update, and comment on PR #3 that its work now lives in PR #4 (do not close or merge anything).
run_tests.py: stdlib only; find every test_*.py in the repo (skip .git), run each test folder with unittest in its own subprocess (so same-named modules in different folders do not clash), print a per-folder pass/fail line and a total, exit non-zero on any failure, no network. It must work on any branch, including folders it has never seen. Add a test for run_tests.py itself.

Box rules for you and for every worker you start (put them in each worker's prompt, word for word):
1. Clean repo: work only in tobkorgjz-eng/bw-starter-lab. Before the first commit, run git log --format='%an <%ae>' and confirm every existing commit uses only the no-reply identity below; if not, stop and say so.
2. Git identity, set in this repo only (never --global, never environment variables): git config user.name "tobkorgjz-eng" and git config user.email "359593544+tobkorgjz-eng@users.noreply.github.com". Before the first commit, show git var GIT_AUTHOR_IDENT and git var GIT_COMMITTER_IDENT.
3. GitHub access: request access with discobox-access (github.com + api.github.com, this repo only) and wait for the answer. Manager: your own request is answered by a person – wait for it. Workers: your manager answers yours. Never stop just because access needs someone's answer; never work around a refusal.
4. gh pr create does not work in a box (GraphQL is blocked). Open pull requests with the GitHub REST API: POST https://api.github.com/repos/tobkorgjz-eng/bw-starter-lab/pulls (head = your branch, base = main). Reviews and comments also via REST (POST .../pulls/N/reviews with event COMMENT; POST .../issues/N/comments).
5. One approval: each worker asks once; the manager reads each request (repo, routes, no merge route) and approves it once under its delegation, limited to this repo, push + open PR + comments, max 2 hours. Never approve a merge route, a wider repo pattern or another repo.
Also: never print, log, write or commit any token or credential (FEEDBACK files included); no pip install or any other install; code and tests make no network calls; do not merge any pull request; do not push to main; no force push; made-up data only.
