#!/usr/bin/env python3
"""Check a bot's planned actions against RULES.md.

Usage:
    python3 check_rules.py plan.json [--rules RULES.md]

plan.json is a JSON list. Each item is either an action name string, or an
object like {"action": "send_email", "owner_approved": true}.

Verdicts per action:
    ALLOW    - in "May do alone"
    ALLOW    - in "Needs the owner's yes" and owner_approved is true
    ASK      - in "Needs the owner's yes" (or not listed) without approval
    BLOCK    - in "Never does" (approval does not change this)

Exit code: 0 if every action is ALLOW, 1 if any action is ASK or BLOCK,
2 on bad input. Standard library only, no network.
"""

import argparse
import json
import os
import re
import sys

ALONE = "alone"
NEEDS_YES = "needs_yes"
NEVER = "never"

ALLOW = "ALLOW"
ASK = "ASK"
BLOCK = "BLOCK"

_SECTION_KEYS = (
    ("may do alone", ALONE),
    ("needs the owner", NEEDS_YES),
    ("never does", NEVER),
)
_BULLET = re.compile(r"^\s*[-*]\s+`([A-Za-z0-9_.:-]+)`")

DEFAULT_RULES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RULES.md")


class RulesError(ValueError):
    """RULES.md or the plan is malformed."""


def parse_rules(text):
    """Return {action_name: category} from RULES.md text."""
    rules = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            heading = line[3:].strip().lower()
            current = None
            for key, cat in _SECTION_KEYS:
                if heading.startswith(key):
                    current = cat
            continue
        if line.startswith("# "):
            current = None
            continue
        if current is None:
            continue
        m = _BULLET.match(line)
        if not m:
            continue
        name = m.group(1)
        if name in rules and rules[name] != current:
            raise RulesError(
                "action %r is listed in two sections (%s and %s)"
                % (name, rules[name], current)
            )
        rules[name] = current
    if not rules:
        raise RulesError("no rules found in RULES.md")
    return rules


def load_rules(path=DEFAULT_RULES):
    with open(path, encoding="utf-8") as fh:
        return parse_rules(fh.read())


def normalize_plan(plan):
    """Turn a plan list into [(action, owner_approved)]."""
    if not isinstance(plan, list):
        raise RulesError("plan must be a JSON list")
    out = []
    for i, item in enumerate(plan):
        if isinstance(item, str):
            action, approved = item, False
        elif isinstance(item, dict):
            action = item.get("action")
            approved = item.get("owner_approved", False)
            if not isinstance(approved, bool):
                raise RulesError("item %d: owner_approved must be true or false" % i)
        else:
            raise RulesError("item %d: must be a string or an object" % i)
        if not isinstance(action, str) or not action.strip():
            raise RulesError("item %d: missing action name" % i)
        out.append((action.strip(), approved))
    return out


def check_action(rules, action, owner_approved=False):
    """Return (verdict, reason) for one action."""
    cat = rules.get(action)
    if cat == NEVER:
        return BLOCK, "never allowed"
    if cat == ALONE:
        return ALLOW, "may do alone"
    if cat == NEEDS_YES:
        if owner_approved:
            return ALLOW, "owner said yes"
        return ASK, "needs the owner's yes"
    if owner_approved:
        return ALLOW, "not listed; owner said yes"
    return ASK, "not listed; ask the owner first"


def check_plan(rules, plan):
    """Return a list of dicts: action, verdict, reason."""
    results = []
    for action, approved in normalize_plan(plan):
        verdict, reason = check_action(rules, action, approved)
        results.append({"action": action, "verdict": verdict, "reason": reason})
    return results


def all_allowed(results):
    return all(r["verdict"] == ALLOW for r in results)


def format_results(results):
    lines = ["%-6s %-24s %s" % (r["verdict"], r["action"], r["reason"]) for r in results]
    counts = {v: sum(1 for r in results if r["verdict"] == v) for v in (ALLOW, ASK, BLOCK)}
    lines.append(
        "Summary: %d allow, %d ask, %d block" % (counts[ALLOW], counts[ASK], counts[BLOCK])
    )
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check a plan against RULES.md")
    parser.add_argument("plan", help="path to a JSON plan file")
    parser.add_argument("--rules", default=DEFAULT_RULES, help="path to RULES.md")
    args = parser.parse_args(argv)
    try:
        rules = load_rules(args.rules)
        with open(args.plan, encoding="utf-8") as fh:
            plan = json.load(fh)
        results = check_plan(rules, plan)
    except (OSError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    print(format_results(results))
    return 0 if all_allowed(results) else 1


if __name__ == "__main__":
    sys.exit(main())
