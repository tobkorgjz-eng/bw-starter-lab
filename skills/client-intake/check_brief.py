#!/usr/bin/env python3
"""Check a filled client brief before it is handed to the client-rules-file step.

Usage: python3 check_brief.py BRIEF.md [--json]

Reports missing sections, unfilled <placeholders>, badly formed rules lines
(any list marker: -, *, + or 1.), other text inside a rules list, empty rules
lists, actions listed on more than one rules list, and warns when a "Limits
and exceptions" line looks like it widens a list ("without asking", "alone").
Exit status: 0 no problems, 1 problems found, 2 usage or file error.
Stdlib only; reads one local file; makes no network calls.
"""
import json
import re
import sys

REQUIRED_SECTIONS = [
    "Business",
    "People",
    "Work today",
    "First tasks for the assistant",
    "May do alone",
    "Needs the owner's yes",
    "Never does",
    "Limits and exceptions",
    "Information",
    "Success and concerns",
    "Sign-off",
]
RULES_SECTIONS = ["May do alone", "Needs the owner's yes", "Never does"]

LIST_MARKER = re.compile(r"^(?:[-*+]|\d+[.)])\s+")
RULE_LINE = re.compile(r"^(?:[-*+]|\d+[.)])\s+`([a-z][a-z0-9_]*)` — \S.*$")
PLACEHOLDER = re.compile(r"<[^<>\n]+>")
# The one non-rule line allowed inside a rules section (from the template).
DEFAULT_LINE = "Anything not listed needs the owner's yes."
WIDENING = re.compile(r"without asking|\balone\b", re.IGNORECASE)


def parse_sections(text):
    """Return {section heading: [lines]} for '## ' headings, in order."""
    sections = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return sections


def parse_rules(sections):
    """Return {rules section: [action names]} from well-formed rule lines."""
    rules = {}
    for name in RULES_SECTIONS:
        actions = []
        for line in sections.get(name, []):
            m = RULE_LINE.match(line.strip())
            if m:
                actions.append(m.group(1))
        rules[name] = actions
    return rules


def check_brief(text):
    """Return a list of problem strings for the brief text (empty if fine)."""
    problems = []
    if not text.lstrip().startswith("# Client brief: "):
        problems.append("first line should be '# Client brief: <business name>'")
    sections = parse_sections(text)
    for name in REQUIRED_SECTIONS:
        if name not in sections:
            problems.append("missing section: " + name)

    for lineno, line in enumerate(text.splitlines(), 1):
        for ph in PLACEHOLDER.findall(line):
            problems.append("line %d: unfilled placeholder %s" % (lineno, ph))

    seen = {}
    for name in RULES_SECTIONS:
        if name not in sections:
            continue
        count = 0
        for line in sections[name]:
            s = line.strip()
            if not s or s == DEFAULT_LINE:
                continue
            if not LIST_MARKER.match(s):
                problems.append(
                    "%s: text that is not a rules line (put notes outside "
                    "the rules lists): %s" % (name, s))
                continue
            m = RULE_LINE.match(s)
            if not m:
                problems.append(
                    "%s: rules line not in the form "
                    "'- `action_name` — description': %s" % (name, s))
                continue
            count += 1
            action = m.group(1)
            if action in seen and seen[action] != name:
                problems.append("action `%s` is on two lists: %s and %s"
                                % (action, seen[action], name))
            elif action in seen:
                problems.append("action `%s` listed twice in %s" % (action, name))
            else:
                seen[action] = name
        if count == 0:
            problems.append("%s: no rules listed" % name)

    for line in sections.get("Limits and exceptions", []):
        s = line.strip()
        if s and WIDENING.search(s):
            problems.append(
                "warning: Limits and exceptions may only narrow the rules "
                "lists, never widen them; move this into the right list: " + s)
    return problems


def main(argv):
    args = [a for a in argv if a != "--json"]
    as_json = len(args) != len(argv)
    if len(args) != 1:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    try:
        with open(args[0], encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print("cannot read %s: %s" % (args[0], e.strerror), file=sys.stderr)
        return 2
    problems = check_brief(text)
    if as_json:
        print(json.dumps({"ok": not problems, "problems": problems,
                          "rules": parse_rules(parse_sections(text))}, indent=2))
    elif problems:
        for p in problems:
            print("PROBLEM: " + p)
    else:
        print("OK: brief is complete and its rules lists are well formed")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
