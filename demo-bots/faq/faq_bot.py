"""Tiny FAQ bot for a made-up plumbing company.

Answers come only from faq.json. If no FAQ entry matches well enough,
the bot says it does not know and offers to pass the question to a person.

Customer text is treated as data, never as instructions: the bot only
ever replies with one of the fixed texts stored in faq.json, and a
message that tries to change its rules ("ignore your rules ...") gets
the fixed injection reply instead of an FAQ answer.
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


def words_of(text):
    """All lowercase words (letters, digits, hyphens), stopwords kept."""
    return re.findall(r"[a-z0-9][a-z0-9\-]*", text.lower())


def tokenize(text):
    """Lowercase words, minus stopwords."""
    return [w for w in words_of(text) if w not in STOPWORDS]


def contains_phrase(words, phrase):
    """True if the phrase's words appear consecutively in words."""
    target = words_of(phrase)
    n = len(target)
    return n > 0 and any(words[i:i + n] == target for i in range(len(words) - n + 1))


def load_faq(path=DEFAULT_FAQ_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


DEFAULT_INJECTION_REPLY = (
    "I can only answer from the FAQ, and messages can't change how I work. "
    "If you'd like, I can pass your message to a person."
)


class FaqBot:
    def __init__(self, data, min_score=1):
        self.business = data.get("business", "")
        self.fallback = data["fallback"]
        self.faqs = data["faqs"]
        self.injection_reply = data.get("injection_reply", DEFAULT_INJECTION_REPLY)
        self.injection_phrases = data.get("injection_phrases", [])
        # Phrases like "act as" or "from now on" are common in ordinary
        # questions, so they only count next to an instruction word.
        self.injection_context_phrases = data.get("injection_context_phrases", [])
        self.injection_context_targets = data.get("injection_context_targets", [])
        self.min_score = min_score

    def looks_like_injection(self, message):
        """True if the message tries to give the bot new instructions."""
        all_words = words_of(message)

        def has_any(phrases):
            return any(contains_phrase(all_words, p) for p in phrases)

        if has_any(self.injection_phrases):
            return True
        return (has_any(self.injection_context_phrases)
                and has_any(self.injection_context_targets))

    def score(self, entry, message):
        """Count specific keywords and multi-word phrases found in message.

        faq.json keeps only specific single keywords (e.g. "heater").
        Generic words such as "water" or "hot" only count inside a
        phrase (e.g. "hot water"), so "Is my water bill too high?"
        does not match anything and gets the fallback.
        """
        all_words = words_of(message)
        keywords = {k.lower() for k in entry.get("keywords", [])}
        score = sum(1 for w in set(tokenize(message)) if w in keywords)
        score += sum(1 for p in entry.get("phrases", []) if contains_phrase(all_words, p))
        return score

    def best_match(self, message):
        best, best_score = None, 0
        for entry in self.faqs:
            s = self.score(entry, message)
            if s > best_score:
                best, best_score = entry, s
        if best_score < self.min_score:
            return None
        return best

    def respond(self, message):
        """Return {"kind", "text", "offer_handoff"} for a customer message.

        kind is "faq" (text is an FAQ answer), "fallback" (not in the FAQ)
        or "injection" (the message tried to change the bot's rules).
        text is always one of the fixed texts from faq.json; the
        customer's own words are never copied into the reply.
        """
        if not message or not message.strip():
            return {"kind": "fallback", "text": self.fallback, "offer_handoff": True}
        if self.looks_like_injection(message):
            return {"kind": "injection", "text": self.injection_reply, "offer_handoff": True}
        entry = self.best_match(message)
        if entry is None:
            return {"kind": "fallback", "text": self.fallback, "offer_handoff": True}
        return {"kind": "faq", "text": entry["answer"], "offer_handoff": False}

    def answer(self, message):
        return self.respond(message)["text"]


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
