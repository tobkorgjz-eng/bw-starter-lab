# upwork-proposal skill

A Claude skill for Blade Works: score an Upwork job post 1-5 for fit, list the
reasons, and draft a short proposal. Offline, Python 3 standard library only,
and it never sends anything. See `SKILL.md` for the rules and steps.

    python3 skills/upwork-proposal/proposal.py skills/upwork-proposal/samples/job_clinic_assistant.txt

Sample results: clinic assistant 5/5, inventory report 3/5, crypto bot 1/5.
All businesses and people in `samples/` are made up.

Builds on `upwork-helper/` (the job-post parser is adapted from
`proposal_helper.py`); `upwork-helper/` stays as it was.

Tests (from the repo root):

    python3 -m unittest discover -s skills/upwork-proposal -t skills/upwork-proposal
