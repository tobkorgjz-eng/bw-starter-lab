#!/usr/bin/env python3
"""Offline review scan for Blade Works PR branches (stdlib only).

Looks at files on disk and reports, with file:line:
  - secret:    strings shaped like tokens, keys or credentials
  - wording:   the banned p-word and hype phrases
  - injection: prompt-injection / unsafe-execution risk patterns in bots and skills
  - network:   imports or calls that reach the network (code must run offline)

It is a heuristic helper for a human reviewer. A clean scan
means none of these patterns matched, nothing more.

Usage:
    python3 tools/review_scan.py PATH [PATH ...]      # human-readable
    python3 tools/review_scan.py --json PATH          # machine-readable
Exit code: 0 no findings, 1 findings, 2 bad usage.
Matched secret values are never printed; only their kind and location.
"""

import json
import os
import re
import sys

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}
TEXT_EXT = {".py", ".md", ".txt", ".json", ".html", ".htm", ".js", ".css",
            ".yml", ".yaml", ".toml", ".cfg", ".ini", ".sh", ".env", ""}

# Patterns are assembled from pieces so this file does not match itself.
_SECRET_PATTERNS = [
    ("github token", r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
    ("aws access key", r"\bAKIA[0-9A-Z]{16}\b"),
    ("api key (sk-)", r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_\-]{20,}"),
    ("slack token", r"\bxox[abprs]-[A-Za-z0-9\-]{10,}"),
    ("private key block", "-----BEGIN " + r"(?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    ("credential in URL", r"https?://[^/\s:@]+:[^/\s@]+@"),
    ("bearer header value", r"(?i)authorization:\s*bearer\s+[A-Za-z0-9_\-\.]{20,}"),
    ("assigned secret", r"(?i)\b(?:pass" + r"word|passwd|secret|api_?key|token)\b\s*[:=]\s*['\"][^'\"\s$<{]{8,}['\"]"),
]
SECRET_RES = [(k, re.compile(p)) for k, p in _SECRET_PATTERNS]

BANNED_WORD_RE = re.compile(r"(?i)\bpro" + r"of\w*")
HYPE_TERMS = [
    "revolutionary", "game-changing", "game changer", "cutting-edge",  # review-scan: ignore
    "best-in-class", "world-class", "unbeatable", "guaranteed", "guarantee",  # review-scan: ignore
    "100%", "never fails", "never miss", "effortless", "seamless",  # review-scan: ignore
    "blazing", "magic", "supercharge", "10x", "state-of-the-art",  # review-scan: ignore
    "fully autonomous", "zero risk", "risk-free", "bulletproof",  # review-scan: ignore
]
HYPE_RE = re.compile(
    r"(?i)(?<![\w-])(" + "|".join(re.escape(t) for t in HYPE_TERMS) + r")(?![\w-])")

_INJECTION_PATTERNS = [
    ("eval/exec on data", r"(?<![\.\w])(?:eval|exec)\s*\("),
    ("shell execution", r"\b(?:os\.system|os\.popen|subprocess\.)"),
    ("shell=True", r"shell\s*=\s*True"),  # review-scan: ignore
    ("unsafe deserialization", r"\b(?:pickle\.loads?|marshal\.loads?|yaml\.load)\s*\("),
    ("html injection sink", r"\.innerHTML\s*[+]?=|document\.write\s*\("),
    ("override phrase", r"(?i)ignore (?:all |any )?(?:previous|prior|above) instructions"),
    ("raw user text in prompt", r"(?i)\{\{?\s*(?:user_?input|message|job_?text|question|client_?text)\s*\}?\}"),
]
INJECTION_RES = [(k, re.compile(p)) for k, p in _INJECTION_PATTERNS]

_NETWORK_PATTERNS = [
    ("network import", r"^\s*(?:import|from)\s+(?:urllib\.request|urllib3|requests|http\.client|socket|httpx|aiohttp|smtplib|ftplib)\b"),
    ("network call", r"\b(?:urlopen|fetch|XMLHttpRequest|WebSocket)\s*\("),
]
NETWORK_RES = [(k, re.compile(p, re.M)) for k, p in _NETWORK_PATTERNS]

EXEMPT_MARK = "review-scan: ignore"


def iter_files(paths):
    for root in paths:
        if os.path.isfile(root):
            yield root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for name in sorted(filenames):
                if os.path.splitext(name)[1].lower() in TEXT_EXT:
                    yield os.path.join(dirpath, name)


def scan_text(text, path="<text>"):
    """Return a list of finding dicts for one file's text."""
    findings = []
    is_test = os.path.basename(path).startswith("test_")
    for lineno, line in enumerate(text.splitlines(), 1):
        if EXEMPT_MARK in line:
            continue

        def add(kind, rule, excerpt):
            findings.append({"file": path, "line": lineno, "kind": kind,
                             "rule": rule, "excerpt": excerpt})

        for rule, rx in SECRET_RES:
            if rx.search(line):
                add("secret", rule, "[value hidden]")
        for m in BANNED_WORD_RE.finditer(line):
            add("wording", "banned word", m.group(0))
        for m in HYPE_RE.finditer(line):
            add("wording", "hype", m.group(0))
        if not is_test:
            for rule, rx in INJECTION_RES:
                if rx.search(line):
                    add("injection", rule, line.strip()[:100])
            for rule, rx in NETWORK_RES:
                if rx.search(line):
                    add("network", rule, line.strip()[:100])
    return findings


def scan_paths(paths):
    findings = []
    for path in iter_files(paths):
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except (UnicodeDecodeError, OSError):
            continue
        findings.extend(scan_text(text, path))
    return findings


def format_findings(findings):
    if not findings:
        return "no findings"
    return "\n".join(
        "{file}:{line}: {kind} ({rule}): {excerpt}".format(**f) for f in findings)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in argv
    paths = [a for a in argv if a != "--json"]
    if not paths:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        print("usage: review_scan.py [--json] PATH [PATH ...]", file=sys.stderr)
        return 2
    findings = scan_paths(paths)
    print(json.dumps(findings, indent=2) if as_json else format_findings(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
