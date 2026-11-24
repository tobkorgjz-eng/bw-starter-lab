#!/usr/bin/env python3
"""Score an Upwork job post 1-5 for fit and draft a short proposal.

Blade Works - "Runs by your rules, asks before it acts."

Offline only: standard library, no network, no Upwork API. It never sends
anything. It prints a fit score, the reasons, and a draft for a person to
read, edit and send themselves.

The job-post parser is adapted from upwork-helper/proposal_helper.py.
"""
import argparse
import re
import sys
from pathlib import Path

EXPERIENCE_LINE = "2 years building AI assistant teams"

# What Blade Works actually offers. Only these may be claimed in a draft.
OUR_SKILLS = [
    "ai assistant", "chatbot", "faq", "booking", "automation", "python",
    "customer support", "email", "approval steps", "documentation", "testing",
    "csv", "excel",
]
# Words in a post that mean the same as one of our skills.
SYNONYMS = {
    "assistant": "ai assistant", "chat bot": "chatbot",
    "appointments": "booking", "scheduling": "booking", "faqs": "faq",
    "emails": "email", "automate": "automation", "automatically": "automation",
}

RED_FLAGS = [
    "unpaid test", "free sample", "pay after", "outside upwork", "off platform",
    "telegram", "whatsapp", "urgent asap", "guarantees profit",
]

# Never in a draft. "proof" is matched as a substring, so "proofread" counts.
BANNED_SUBSTRINGS = ["proof"]
HYPE_WORDS = [
    "best", "expert", "guarantee", "guaranteed", "guarantees", "world-class",
    "revolutionary", "cutting-edge", "game-changer", "game-changing", "10x",
    "rockstar", "ninja", "unmatched", "unbeatable", "amazing", "incredible",
    "perfect", "top-notch", "seamless", "effortless", "100%", "passionate",
    "skyrocket", "leading", "ultimate",
]

MAX_DRAFT_WORDS = 170


def has_word(phrase, text):
    """True if phrase appears in text as whole word(s): 'api' is not in 'rapid'."""
    return re.search(r"(?<![\w-])" + re.escape(phrase) + r"(?![\w-])", text) is not None


def parse_job_post(text):
    """Parse 'Key: value' header lines, then free text after 'Description:'."""
    fields, body, in_body = {}, [], False
    for line in text.splitlines():
        m = re.match(r"^\s*([A-Za-z ]+):\s*(.*)$", line)
        key = m.group(1).strip().lower() if m else None
        if not in_body and m and key != "description":
            fields[key] = m.group(2).strip()
        elif not in_body and key == "description":
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


def find_banned(text):
    """Return every banned or hype word found in text (case-insensitive)."""
    low = text.lower()
    found = [b for b in BANNED_SUBSTRINGS if b in low]
    found += [h for h in HYPE_WORDS if has_word(h, low)]
    return found


def quote(text, fallback):
    """Return client text unchanged if it is free of banned words, else fallback.

    We never rewrite a client's words (that could change their meaning);
    we just stop quoting them.
    """
    text = text.replace("(made-up)", "").strip()
    return text if text and not find_banned(text) else fallback


def score_fit(job):
    """Return (score 1-5, list of reasons, matched skills, missing skills)."""
    text = (job["title"] + " " + job["description"] + " " + " ".join(job["skills"])).lower()
    matched = [s for s in OUR_SKILLS if has_word(s, text)]
    for word, skill in SYNONYMS.items():
        if skill not in matched and has_word(word, text):
            matched.append(skill)
    covered = set(OUR_SKILLS) | set(SYNONYMS)
    missing = [s for s in job["skills"] if s not in covered]
    flags = [f for f in RED_FLAGS if f in text]
    words = len(job["description"].split())

    score, reasons = 1, []
    if matched:
        score += 1
        reasons.append(f"+1 skills we offer appear in the post: {', '.join(matched)}")
    else:
        reasons.append("+0 none of our skills appear in the post")
    if len(matched) >= 3:
        score += 1
        reasons.append(f"+1 strong overlap ({len(matched)} matching skills)")
    if job["budget"]:
        score += 1
        reasons.append(f"+1 budget stated: {job['budget']}")
    else:
        reasons.append("+0 no budget stated")
    if words >= 40:
        score += 1
        reasons.append(f"+1 clear description ({words} words)")
    else:
        reasons.append(f"+0 short description ({words} words), scope unclear")
    if len(missing) >= 2:
        score -= 1
        reasons.append(f"-1 required skills we do not offer: {', '.join(missing)}")
    elif missing:
        reasons.append(f"-0 one skill we do not offer: {missing[0]} (say so honestly)")
    if flags:
        score -= 2
        reasons.append(f"-2 red flags: {', '.join(flags)}")
    score = max(1, min(5, score))
    return score, reasons, matched, missing


def draft_proposal(job, freelancer="The Blade Works team"):
    """Return a short draft proposal. Raises ValueError if a banned word slips in."""
    score, _, matched, missing = score_fit(job)
    client = quote(job["client"], "there")
    title = quote(job["title"], "")
    lines = [f"Hi {client},", ""]
    lines.append(f'Thanks for posting "{title}".' if title else "Thanks for your post.")
    lines.append("")
    lines.append(f"Blade Works has {EXPERIENCE_LINE}. Our assistants run by "
                 f"your rules and ask a person before they act.")
    if matched:
        lines.append(f"Relevant to your post: {', '.join(matched[:5])}.")
    if missing:
        lines.append(f"To be clear, we have not worked with {', '.join(missing)}.")
    lines += ["", "How we would start:",
              "1. A short call to agree on scope and what done looks like.",
              "2. A first working version for you to try and comment on.",
              "3. Changes, short documentation and handover."]
    lines.append("")
    budget = quote(job["budget"], "")
    lines.append(f"Your budget ({budget}) works for a first scoped version."
                 if budget else "Happy to suggest a budget once the scope is clear.")
    lines += ["", "Kind regards,", freelancer]
    draft = "\n".join(lines)
    bad = find_banned(draft)
    if bad:
        raise ValueError(f"draft contains banned words: {bad}")
    if score <= 2:
        draft = "NOTE: fit score is low - consider not applying.\n\n" + draft
    return draft


def report(job, freelancer="The Blade Works team"):
    score, reasons, _, _ = score_fit(job)
    out = [f"FIT SCORE: {score}/5", "Reasons:"]
    out += [f"  {r}" for r in reasons]
    out += ["", "DRAFT PROPOSAL - not sent. Read, edit and send it yourself.",
            "-" * 40, draft_proposal(job, freelancer), ""]
    return "\n".join(out)


def main(argv=None):
    p = argparse.ArgumentParser(description="Score a job post 1-5 and draft a proposal (offline, never sends).")
    p.add_argument("job_file", help="path to a job post .txt")
    p.add_argument("--name", default="The Blade Works team", help="sign-off name")
    p.add_argument("--out", help="write the result to this file instead of stdout")
    args = p.parse_args(argv)
    job = parse_job_post(Path(args.job_file).read_text(encoding="utf-8"))
    result = report(job, args.name)
    if args.out:
        Path(args.out).write_text(result, encoding="utf-8")
    else:
        sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
