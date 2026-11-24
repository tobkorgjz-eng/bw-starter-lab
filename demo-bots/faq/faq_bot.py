"""Tiny FAQ bot for a made-up plumbing company.

Answers come only from faq.json. If no FAQ entry matches well enough,
the bot replies with the fallback ("I'll check with the owner").
Python 3 standard library only; no network calls.
"""

import json
import os
import re
import sys

DEFAULT_FAQ_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faq.json")

# Common words that should not count as a match on their own.
STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "does", "you", "your", "i", "my",
    "me", "we", "can", "what", "how", "of", "to", "for", "in", "on", "it",
    "and", "or", "be", "with", "have", "has", "any", "much", "there",
}


def tokenize(text):
    """Lowercase words (letters, digits, hyphens), minus stopwords."""
    words = re.findall(r"[a-z0-9][a-z0-9\-]*", text.lower())
    return [w for w in words if w not in STOPWORDS]


def load_faq(path=DEFAULT_FAQ_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class FaqBot:
    def __init__(self, data, min_score=1):
        self.business = data.get("business", "")
        self.fallback = data["fallback"]
        self.faqs = data["faqs"]
        self.min_score = min_score

    def score(self, entry, words):
        # Only curated keywords count, so generic words like "fix" in the
        # question text don't cause false matches.
        keywords = {k.lower() for k in entry.get("keywords", [])}
        return sum(1 for w in set(words) if w in keywords)

    def best_match(self, message):
        words = tokenize(message)
        best, best_score = None, 0
        for entry in self.faqs:
            s = self.score(entry, words)
            if s > best_score:
                best, best_score = entry, s
        if best_score < self.min_score:
            return None
        return best

    def answer(self, message):
        if not message or not message.strip():
            return self.fallback
        entry = self.best_match(message)
        return entry["answer"] if entry else self.fallback


def main(argv=None):
    bot = FaqBot(load_faq())
    argv = sys.argv[1:] if argv is None else argv
    if argv:
        print(bot.answer(" ".join(argv)))
        return 0
    print(f"{bot.business} FAQ bot. Type a question (blank line to quit).")
    while True:
        try:
            line = input("> ")
        except EOFError:
            break
        if not line.strip():
            break
        print(bot.answer(line))
    return 0


if __name__ == "__main__":
    sys.exit(main())
