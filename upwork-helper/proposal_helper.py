#!/usr/bin/env python3
"""Draft a freelance proposal from a job post (.txt) using a local template.

Offline only: no API, no network, never sends anything. It prints a draft
(or writes it to a file) for a human to review and edit.
"""
import argparse
import re
import string
import sys
from pathlib import Path

DEFAULT_TEMPLATE = """Hi $client,

I read your post "$title" and it looks like a good match for my experience.

What I understood you need:
$summary

Skills I would bring: $matched_skills

My plan:
1. Confirm scope and success criteria with you.
2. Deliver a first working version early for feedback.
3. Polish, document and hand over.

$budget_line

Best regards,
$freelancer
"""

# Skills the (made-up) freelancer offers, used for the fit checklist.
DEFAULT_SKILLS = ["python", "automation", "scraping", "api", "data cleaning",
                  "excel", "csv", "testing", "documentation", "bots"]

RED_FLAGS = ["unpaid test", "free sample", "pay after", "outside upwork",
             "off platform", "telegram", "whatsapp", "urgent asap"]


def parse_job_post(text):
    """Parse 'Key: value' header lines plus a free-text description."""
    fields = {}
    body = []
    in_body = False
    for line in text.splitlines():
        m = re.match(r"^\s*([A-Za-z ]+):\s*(.*)$", line)
        if not in_body and m and m.group(1).strip().lower() != "description":
            fields[m.group(1).strip().lower()] = m.group(2).strip()
        elif not in_body and m and m.group(1).strip().lower() == "description":
            in_body = True
            if m.group(2).strip():
                body.append(m.group(2).strip())
        elif in_body or line.strip():
            in_body = True
            body.append(line.rstrip())
    skills = [s.strip().lower() for s in fields.get("skills", "").split(",") if s.strip()]
    return {
        "title": fields.get("title", "Untitled job"),
        "client": fields.get("client", "there"),
        "budget": fields.get("budget", ""),
        "skills": skills,
        "description": "\n".join(body).strip(),
    }


def fit_checklist(job, my_skills=None):
    """Return a list of (check, passed, note) tuples and a 0-100 score."""
    my_skills = [s.lower() for s in (my_skills or DEFAULT_SKILLS)]
    text = (job["description"] + " " + " ".join(job["skills"])).lower()
    matched = [s for s in my_skills if s in text]
    missing = [s for s in job["skills"] if s not in my_skills]
    flags = [f for f in RED_FLAGS if f in text]
    checks = [
        ("Skills overlap", len(matched) >= 2,
         ", ".join(matched) if matched else "no overlap"),
        ("No unknown required skills", not missing,
         ", ".join(missing) if missing else "all known"),
        ("Budget stated", bool(job["budget"]), job["budget"] or "not stated"),
        ("Clear description (40+ words)", len(job["description"].split()) >= 40,
         f"{len(job['description'].split())} words"),
        ("No red flags", not flags, ", ".join(flags) if flags else "none found"),
    ]
    score = round(100 * sum(1 for _, ok, _ in checks if ok) / len(checks))
    return checks, score, matched


def summarize(description, max_sentences=2):
    sentences = re.split(r"(?<=[.!?])\s+", description.replace("\n", " ").strip())
    picked = [s for s in sentences if s][:max_sentences]
    return "\n".join(f"- {s}" for s in picked) or "- (no description given)"


def draft_proposal(job, template=DEFAULT_TEMPLATE, freelancer="Sam Example",
                   my_skills=None):
    checks, score, matched = fit_checklist(job, my_skills)
    budget_line = (f"I can work within the stated budget ({job['budget']})."
                   if job["budget"] else "Happy to discuss a fair budget for the scope.")
    body = string.Template(template).safe_substitute(
        client=job["client"], title=job["title"], summary=summarize(job["description"]),
        matched_skills=", ".join(matched) if matched else "(fill in)",
        budget_line=budget_line, freelancer=freelancer)
    lines = [f"FIT CHECKLIST (score {score}/100)"]
    lines += [f"  [{'x' if ok else ' '}] {name}: {note}" for name, ok, note in checks]
    lines += ["", "DRAFT PROPOSAL (review before using - nothing is sent)", "-" * 40, body]
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="Draft a proposal from a job post .txt (offline).")
    p.add_argument("job_file", help="path to a job post .txt")
    p.add_argument("--template", help="optional template .txt using $placeholders")
    p.add_argument("--name", default="Sam Example", help="your display name")
    p.add_argument("--out", help="write draft to this file instead of stdout")
    args = p.parse_args(argv)
    job = parse_job_post(Path(args.job_file).read_text(encoding="utf-8"))
    template = (Path(args.template).read_text(encoding="utf-8")
                if args.template else DEFAULT_TEMPLATE)
    result = draft_proposal(job, template, args.name)
    if args.out:
        Path(args.out).write_text(result, encoding="utf-8")
    else:
        sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
