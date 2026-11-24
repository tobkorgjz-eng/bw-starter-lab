#!/usr/bin/env python3
"""Check a bot's planned actions against RULES.md.

Usage:
    python3 check_rules.py plan.json [--rules RULES.md]
                           [--approvals owner_approvals.json] [--approve ACTION ...]

plan.json is written by the bot. It is a JSON list; each item is an action
name string or an object like {"action": "send_email"}. The bot cannot
approve its own actions: any approval field inside the plan (such as
"owner_approved") is ignored.

Approval comes only from the owner, outside the plan:
    --approvals FILE   a JSON list of action names the owner said yes to
    --approve ACTION   one action the owner said yes to (repeatable)

Verdicts per action:
    ALLOW    - in "May do alone"
    ALLOW    - needs the owner's yes (or not listed) and the owner approved it
    ASK      - needs the owner's yes (or not listed) and the owner did not
    BLOCK    - in "Never does" (owner approval does not change this)

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
# Fields a bot might use to try to approve its own action. Never trusted.
_SELF_APPROVAL_KEYS = ("owner_approved", "approved", "approval")

DEFAULT_RULES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RULES.md")


class RulesError(ValueError):
    """RULES.md, the plan, or the owner approvals are malformed."""


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
    """Turn a plan list into [(action, self_approval_attempted)].

    Any approval field in the plan is ignored; we only note that it was there.
    """
    if not isinstance(plan, list):
        raise RulesError("plan must be a JSON list")
    out = []
    for i, item in enumerate(plan):
        if isinstance(item, str):
            action, attempted = item, False
        elif isinstance(item, dict):
            action = item.get("action")
            attempted = any(k in item for k in _SELF_APPROVAL_KEYS)
        else:
            raise RulesError("item %d: must be a string or an object" % i)
        if not isinstance(action, str) or not action.strip():
            raise RulesError("item %d: missing action name" % i)
        out.append((action.strip(), attempted))
    return out


def normalize_approvals(approvals):
    """Turn the owner's approvals (a list of action names) into a set."""
    if approvals is None:
        return frozenset()
    if not isinstance(approvals, (list, tuple, set, frozenset)):
        raise RulesError("owner approvals must be a JSON list of action names")
    out = set()
    for i, name in enumerate(approvals):
        if not isinstance(name, str) or not name.strip():
            raise RulesError("owner approval %d: must be an action name" % i)
        out.add(name.strip())
    return frozenset(out)


def load_approvals(path):
    with open(path, encoding="utf-8") as fh:
        return normalize_approvals(json.load(fh))


def check_action(rules, action, owner_approvals=frozenset()):
    """Return (verdict, reason) for one action.

    owner_approvals is the set of action names the owner said yes to,
    supplied outside the bot's plan.
    """
    cat = rules.get(action)
    approved = action in owner_approvals
    if cat == NEVER:
        return BLOCK, "never allowed"
    if cat == ALONE:
        return ALLOW, "may do alone"
    if cat == NEEDS_YES:
        if approved:
            return ALLOW, "owner said yes"
        return ASK, "needs the owner's yes"
    if approved:
        return ALLOW, "not listed; owner said yes"
    return ASK, "not listed; ask the owner first"


def check_plan(rules, plan, owner_approvals=None):
    """Return a list of dicts: action, verdict, reason."""
    approvals = normalize_approvals(owner_approvals)
    results = []
    for action, attempted in normalize_plan(plan):
        verdict, reason = check_action(rules, action, approvals)
        if attempted:
            reason += " (approval inside the plan ignored)"
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
    parser.add_argument("plan", help="path to the bot's JSON plan file")
    parser.add_argument("--rules", default=DEFAULT_RULES, help="path to RULES.md")
    parser.add_argument(
        "--approvals", metavar="FILE",
        help="owner's approvals: JSON list of action names the owner said yes to",
    )
    parser.add_argument(
        "--approve", metavar="ACTION", action="append", default=[],
        help="an action the owner said yes to (repeatable)",
    )
    args = parser.parse_args(argv)
    try:
        rules = load_rules(args.rules)
        approvals = set(normalize_approvals(args.approve))
        if args.approvals:
            approvals |= load_approvals(args.approvals)
        with open(args.plan, encoding="utf-8") as fh:
            plan = json.load(fh)
        results = check_plan(rules, plan, approvals)
    except (OSError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    print(format_results(results))
    return 0 if all_allowed(results) else 1


if __name__ == "__main__":
    sys.exit(main())
