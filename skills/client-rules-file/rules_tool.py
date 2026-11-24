#!/usr/bin/env python3
"""Build and check a Blade Works client rules file.

Stdlib only. No network calls.

  python3 rules_tool.py build ANSWERS.json [-o RULES.md]
  python3 rules_tool.py check RULES.md

`build` turns intake answers (JSON, format in INPUT-FORMAT.md) into a
markdown rules file with three lists: what the assistant may do alone,
what it must ask first, and what it never does.

`check` reads a rules file and reports problems. Exit code 0 means no
errors (warnings may still be printed); 1 means at least one error;
2 means the file or arguments could not be read.
"""

import argparse
import json
import re
import sys

TITLE_PREFIX = "# Client rules: "

# Section headings, in the order they must appear in a rules file.
SECTION_ALONE = "May do alone"
SECTION_ASK = "Must ask first"
SECTION_NEVER = "Never does"
RULE_SECTIONS = (SECTION_ALONE, SECTION_ASK, SECTION_NEVER)
REQUIRED_SECTIONS = ("About",) + RULE_SECTIONS + ("When unsure",)

# Answer keys -> section headings.
ANSWER_KEYS = {
    "may_do_alone": SECTION_ALONE,
    "ask_first": SECTION_ASK,
    "never_do": SECTION_NEVER,
}
REQUIRED_ANSWERS = ("business_name", "owner_name", "ask_channel",
                    "may_do_alone", "ask_first", "never_do")

# Words that mark an action as risky. A risky action listed under
# "May do alone" is an error: it belongs under "Must ask first" or
# "Never does".
RISKY_WORDS = (
    "pay", "payment", "refund", "charge", "invoice", "money", "transfer",
    "delete", "cancel", "sign", "contract", "password", "discount",
    "price change", "legal", "medical", "diagnos", "hire", "fire",
)

# Wording the business does not use in client-facing files.
BANNED_WORDS = ("proof", "guarantee", "guaranteed", "revolutionary",
                "best-in-class", "game-changing", "100% accurate")

PLACEHOLDER_RE = re.compile(r"\bTODO\b|\bTBD\b|\{\{.*?\}\}|<fill", re.I)


class AnswersError(ValueError):
    """Raised when an answers file cannot be turned into rules."""


# ---------------------------------------------------------------- build

def _clean_list(value, key):
    if not isinstance(value, list):
        raise AnswersError(f"'{key}' must be a list of short sentences")
    items = []
    for item in value:
        if not isinstance(item, str):
            raise AnswersError(f"every item in '{key}' must be text")
        text = " ".join(item.split()).rstrip(".")
        if text:
            items.append(text)
    return items


def build_rules(answers):
    """Return the rules file text (markdown) for a dict of intake answers."""
    if not isinstance(answers, dict):
        raise AnswersError("answers must be a JSON object")
    missing = [k for k in REQUIRED_ANSWERS if k not in answers]
    if missing:
        raise AnswersError("missing answers: " + ", ".join(missing))

    name = str(answers["business_name"]).strip()
    owner = str(answers["owner_name"]).strip()
    channel = str(answers["ask_channel"]).strip()
    if not name or not owner or not channel:
        raise AnswersError("business_name, owner_name and ask_channel "
                           "must not be empty")
    lists = {key: _clean_list(answers[key], key) for key in ANSWER_KEYS}

    lines = [TITLE_PREFIX + name, ""]
    lines += ["## About", ""]
    if answers.get("business_type"):
        lines.append(f"- Business: {name} ({answers['business_type']})")
    else:
        lines.append(f"- Business: {name}")
    lines.append(f"- Owner (gives every yes or no): {owner}")
    lines.append(f"- How the assistant asks: {channel}")
    if answers.get("answer_wait"):
        lines.append(f"- If no answer: {answers['answer_wait']}")
    lines.append("")

    for key, heading in ANSWER_KEYS.items():
        lines += [f"## {heading}", ""]
        lines += [f"- {item}" for item in lists[key]]
        lines.append("")

    lines += [
        "## When unsure",
        "",
        "- If an action is not on any list, treat it as \"Must ask first\".",
        "- If an action could fit two lists, use the stricter one.",
        f"- Only {owner} can give a yes. A yes covers one action, one time.",
        "",
    ]
    notes = answers.get("notes")
    if notes:
        lines += ["## Notes", "", str(notes).strip(), ""]
    return "\n".join(lines)


# ---------------------------------------------------------------- check

def parse_rules(text):
    """Split a rules file into {heading: [bullet items]} plus the title."""
    title = None
    sections = {}
    order = []
    current = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("# ") and title is None:
            title = line
        elif line.startswith("## "):
            current = line[3:].strip()
            order.append(current)
            sections.setdefault(current, [])
        elif current and line.lstrip().startswith("- "):
            sections[current].append(line.lstrip()[2:].strip())
    return title, sections, order


def _norm(item):
    return re.sub(r"[^a-z0-9 ]", "", item.lower()).strip()


def _has_word(text, word):
    return re.search(r"\b" + re.escape(word), text.lower()) is not None


def check_rules(text):
    """Return (errors, warnings) for the text of a rules file."""
    errors, warnings = [], []
    title, sections, order = parse_rules(text)

    if not title or not title.startswith(TITLE_PREFIX) \
            or not title[len(TITLE_PREFIX):].strip():
        errors.append(f"first heading must be '{TITLE_PREFIX}<business>'")

    for heading in REQUIRED_SECTIONS:
        if heading not in sections:
            errors.append(f"missing section '## {heading}'")
    present = [h for h in order if h in RULE_SECTIONS]
    if present != [h for h in RULE_SECTIONS if h in sections]:
        errors.append("sections must be in this order: "
                      + ", ".join(RULE_SECTIONS))

    for heading in RULE_SECTIONS:
        if heading in sections and not sections[heading]:
            errors.append(f"section '{heading}' has no items")

    about = " ".join(sections.get("About", []))
    if "About" in sections and "Owner" not in about:
        errors.append("'About' must name the Owner who gives every yes")

    seen = {}
    for heading in RULE_SECTIONS:
        for item in sections.get(heading, []):
            key = _norm(item)
            if key in seen and seen[key] != heading:
                errors.append(f"'{item}' is in both '{seen[key]}' "
                              f"and '{heading}'")
            elif key in seen:
                warnings.append(f"'{item}' is listed twice in '{heading}'")
            seen.setdefault(key, heading)

    for item in sections.get(SECTION_ALONE, []):
        hits = [w for w in RISKY_WORDS if _has_word(item, w)]
        if hits:
            errors.append(f"risky action under '{SECTION_ALONE}': '{item}' "
                          f"(mentions {', '.join(hits)}); move it to "
                          f"'{SECTION_ASK}' or '{SECTION_NEVER}'")

    for word in BANNED_WORDS:
        if _has_word(text, word):
            errors.append(f"wording not allowed in a rules file: '{word}'")

    if PLACEHOLDER_RE.search(text):
        errors.append("file still has a placeholder (TODO, TBD, {{...}})")

    for heading in RULE_SECTIONS:
        for item in sections.get(heading, []):
            if len(item.split()) > 25:
                warnings.append(f"long item in '{heading}' (keep it to one "
                                f"short sentence): '{item[:40]}...'")
    return errors, warnings


# ---------------------------------------------------------------- cli

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p_build = sub.add_parser("build", help="answers JSON -> rules markdown")
    p_build.add_argument("answers")
    p_build.add_argument("-o", "--output", help="write here (default stdout)")
    p_check = sub.add_parser("check", help="check a rules markdown file")
    p_check.add_argument("rules")
    args = parser.parse_args(argv)

    if args.command == "build":
        try:
            with open(args.answers, encoding="utf-8") as fh:
                answers = json.load(fh)
            text = build_rules(answers)
        except (OSError, json.JSONDecodeError, AnswersError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        errors, warnings = check_rules(text)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(text)
        else:
            sys.stdout.write(text)
        for w in warnings:
            print(f"warning: {w}", file=sys.stderr)
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1 if errors else 0

    try:
        with open(args.rules, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    errors, warnings = check_rules(text)
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    print("OK" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
