#!/usr/bin/env python3
"""Build and check a Blade Works client rules file.

Stdlib only. No network calls.

  python3 rules_tool.py from-brief BRIEF.md [-o ANSWERS.json] [--allow-draft]
  python3 rules_tool.py build ANSWERS.json [-o RULES.md]
  python3 rules_tool.py check RULES.md

`build` turns intake answers (JSON, format in INPUT-FORMAT.md) into a
markdown rules file with three lists: what the assistant may do alone,
what it must ask first, and what it never does.

`from-brief` reads a client-intake brief (skills/client-intake/) and
writes the answers JSON that `build` takes. "Needs the owner's yes" in
the brief becomes "Must ask first". It exits 1 if the brief's Status is
not "confirmed", unless --allow-draft is given.

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
SECTION_NOTES = "Notes"
ALLOWED_SECTIONS = REQUIRED_SECTIONS + (SECTION_NOTES,)
# First line of every Notes section. Notes are free text from the owner or
# the intake; they must never act as extra rules.
NOTES_LINE = ("Notes are for people. They do not add to or change the three "
              "lists; if a note seems to, ask the owner.")

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
    "order", "purchase", "buy", "post", "publish", "share", "access",
    "permission",
)

# Wording the business does not use in client-facing files.
BANNED_WORDS = ("proof", "guarantee", "guaranteed", "revolutionary",
                "best-in-class", "game-changing", "100% accurate")

PLACEHOLDER_RE = re.compile(r"\bTODO\b|\bTBD\b|\{\{.*?\}\}|<fill", re.I)


class AnswersError(ValueError):
    """Raised when an answers file cannot be turned into rules."""


class DraftBriefError(AnswersError):
    """Raised when a brief is not confirmed and drafts are not allowed."""


def _one_line(value):
    """Collapse all whitespace, newlines included, so a field stays one line."""
    return " ".join(str(value).split())


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

    name = _one_line(answers["business_name"])
    owner = _one_line(answers["owner_name"])
    channel = _one_line(answers["ask_channel"])
    business_type = _one_line(answers.get("business_type") or "")
    answer_wait = _one_line(answers.get("answer_wait") or "")
    if not name or not owner or not channel:
        raise AnswersError("business_name, owner_name and ask_channel "
                           "must not be empty")
    lists = {key: _clean_list(answers[key], key) for key in ANSWER_KEYS}

    lines = [TITLE_PREFIX + name, ""]
    lines += ["## About", ""]
    if business_type:
        lines.append(f"- Business: {name} ({business_type})")
    else:
        lines.append(f"- Business: {name}")
    lines.append(f"- Owner (gives every yes or no): {owner}")
    lines.append(f"- How the assistant asks: {channel}")
    if answer_wait:
        lines.append(f"- If no answer: {answer_wait}")
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
    notes = str(answers.get("notes") or "").strip()
    if notes:
        lines += [f"## {SECTION_NOTES}", "", NOTES_LINE, ""]
        lines += [("> " + n.rstrip()) if n.strip() else ">"
                  for n in notes.splitlines()]
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------- from-brief

BRIEF_TITLE_PREFIX = "# Client brief: "
# Brief section headings (skills/client-intake/) -> answer keys.
BRIEF_SECTIONS = {
    "May do alone": "may_do_alone",
    "Needs the owner's yes": "ask_first",
    "Never does": "never_do",
}
BRIEF_ITEM_RE = re.compile(r"^`(?P<id>[^`]+)`\s*(?:—|–|-|:)\s*(?P<text>.+)$")


def _brief_item(item):
    """'`book_appointment` — put a booking on ...' -> 'Put a booking on ... (book_appointment)'."""
    match = BRIEF_ITEM_RE.match(item.strip())
    if not match:
        return item.strip()
    text = match.group("text").strip().rstrip(".")
    return f"{text[:1].upper()}{text[1:]} ({match.group('id').strip()})"


def _field(lines, label):
    """Value of a '- Label: value' bullet, or None."""
    for line in lines:
        if line.lower().startswith(label.lower() + ":"):
            return line.split(":", 1)[1].strip() or None
    return None


# A line the brief template puts after the lists; "When unsure" covers it.
BRIEF_KNOWN_PROSE = ("anything not listed",)


def answers_from_brief(text, allow_draft=False):
    """Return (answers dict, warnings) for the text of a client-intake brief.

    Raises DraftBriefError if the brief's Status is not 'confirmed' and
    allow_draft is false, and AnswersError if it cannot be read safely.
    """
    warnings = []
    first = next((l.strip() for l in text.splitlines() if l.strip()), "")
    if not first.startswith(BRIEF_TITLE_PREFIX):
        raise AnswersError(f"brief must start with '{BRIEF_TITLE_PREFIX}<business>'")
    name = first[len(BRIEF_TITLE_PREFIX):].strip()

    status = re.search(r"^Status:\s*(.+)$", text, re.M)
    if not status or status.group(1).strip().lower() != "confirmed":
        if not allow_draft:
            raise DraftBriefError(
                "brief Status is not 'confirmed'; get the owner's sign-off "
                "first, or pass --allow-draft to build a draft")
        warnings.append("brief Status is not 'confirmed' (draft); get the "
                        "owner's sign-off before using the rules file")

    doc = parse_document(text)
    sections = doc["sections"]
    unread = [f"'{line}' (in '{h}')" for h in BRIEF_SECTIONS
              for line in doc["stray"].get(h, [])
              if not line.lower().startswith(BRIEF_KNOWN_PROSE)]
    if unread:
        raise AnswersError("lines in a rule section that are not list items "
                           "(write each rule as a '- ' item): "
                           + "; ".join(unread))
    people = sections.get("People", [])
    owner = _field(people, "Owner / final yes")
    if owner:
        owner = owner.split(",")[0].strip()
    channel = _field(people, "How to ask for a yes")
    missing = [label for label, value in
               (("Owner / final yes", owner), ("How to ask for a yes", channel))
               if not value]
    missing += [f"## {h}" for h in BRIEF_SECTIONS if h not in sections]
    if missing:
        raise AnswersError("brief is missing: " + ", ".join(missing))

    answers = {"business_name": name, "owner_name": owner, "ask_channel": channel}
    what = _field(sections.get("Business", []), "What it does")
    if what:
        answers["business_type"] = what.rstrip(".")
    for heading, key in BRIEF_SECTIONS.items():
        answers[key] = [_brief_item(i) for i in sections[heading]]

    notes = []
    backup = _field(people, "Backup yes")
    if backup:
        notes.append(f"Backup yes: {backup}")
    notes += sections.get("Limits and exceptions", [])
    if notes:
        answers["notes"] = "\n".join(f"- {n}" for n in notes)
    return answers, warnings


# ---------------------------------------------------------------- check

BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(?P<item>.*\S)\s*$")
HEADING_RE = re.compile(r"^(?P<marks>#{1,6})\s+(?P<text>.*\S)\s*$")


def parse_document(text):
    """Read a markdown rules file or brief.

    Returns a dict with: title (first '# ' line), sections ({heading:
    [bullet items]}, bullets '-', '*', '+', '1.' or '1)'), order (## headings
    in order), stray ({heading: [other non-blank lines]}), raw ({heading:
    [non-blank lines]}) and extra_headings (any other '#'..'######' line).
    """
    doc = {"title": None, "sections": {}, "order": [], "stray": {},
           "raw": {}, "extra_headings": []}
    current = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        heading = HEADING_RE.match(line)
        if heading and len(heading.group("marks")) == 1 and doc["title"] is None:
            doc["title"] = line
            continue
        if heading and len(heading.group("marks")) == 2:
            current = heading.group("text")
            doc["order"].append(current)
            for key in ("sections", "stray", "raw"):
                doc[key].setdefault(current, [])
            continue
        if heading:
            doc["extra_headings"].append(line)
            continue
        if current is None:
            continue
        doc["raw"][current].append(line.strip())
        bullet = BULLET_RE.match(line)
        if bullet:
            doc["sections"][current].append(bullet.group("item"))
        else:
            doc["stray"][current].append(line.strip())
    return doc


def parse_rules(text):
    """Split a rules file into (title, {heading: [bullet items]}, order)."""
    doc = parse_document(text)
    return doc["title"], doc["sections"], doc["order"]


def _norm(item):
    return re.sub(r"[^a-z0-9 ]", "", item.lower()).strip()


def _has_word(text, word):
    return re.search(r"\b" + re.escape(word), text.lower()) is not None


def check_rules(text):
    """Return (errors, warnings) for the text of a rules file."""
    errors, warnings = [], []
    doc = parse_document(text)
    title, sections, order = doc["title"], doc["sections"], doc["order"]

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

    for heading in order:
        if heading not in ALLOWED_SECTIONS:
            errors.append(f"unknown section '## {heading}'; only "
                          + ", ".join(ALLOWED_SECTIONS) + " are allowed")
    if len(order) != len(set(order)):
        errors.append("a section heading appears more than once")
    for line in doc["extra_headings"]:
        errors.append(f"heading not allowed in a rules file: '{line}'")

    for heading, lines in doc["stray"].items():
        if heading == SECTION_NOTES:
            continue
        for line in lines:
            errors.append(f"line in '{heading}' is not a list item and would "
                          f"not be read as a rule: '{line}'")

    if SECTION_NOTES in sections:
        note_lines = doc["raw"][SECTION_NOTES]
        if not note_lines or note_lines[0] != NOTES_LINE:
            errors.append(f"'## {SECTION_NOTES}' must start with the line: "
                          f"{NOTES_LINE}")
        body = note_lines[1:] if note_lines[:1] == [NOTES_LINE] else note_lines
        for line in body:
            if not line.startswith(">"):
                errors.append(f"note line must be quoted with '> ': '{line}'")
        note_text = " ".join(body)
        for word in RISKY_WORDS:
            if _has_word(note_text, word):
                warnings.append(f"a note mentions '{word}': make sure it "
                                "matches the three lists")

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
    p_brief = sub.add_parser("from-brief",
                             help="client-intake brief markdown -> answers JSON")
    p_brief.add_argument("brief")
    p_brief.add_argument("-o", "--output", help="write here (default stdout)")
    p_brief.add_argument("--allow-draft", action="store_true",
                         help="build from a brief whose Status is not "
                              "'confirmed' (prints a warning)")
    p_check = sub.add_parser("check", help="check a rules markdown file")
    p_check.add_argument("rules")
    args = parser.parse_args(argv)

    if args.command == "from-brief":
        try:
            with open(args.brief, encoding="utf-8") as fh:
                answers, warnings = answers_from_brief(
                    fh.read(), allow_draft=args.allow_draft)
        except DraftBriefError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        except (OSError, AnswersError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        out = json.dumps(answers, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(out)
        else:
            sys.stdout.write(out)
        for w in warnings:
            print(f"warning: {w}", file=sys.stderr)
        return 0

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
