import json
import os
import unittest

from faq_bot import DEFAULT_FAQ_PATH, FaqBot, load_faq, tokenize


class TestFaqData(unittest.TestCase):
    def test_faq_json_is_valid(self):
        data = load_faq()
        self.assertIn("fallback", data)
        self.assertIn("check with the owner", data["fallback"])
        self.assertGreater(len(data["faqs"]), 0)
        for entry in data["faqs"]:
            self.assertTrue(entry["question"])
            self.assertTrue(entry["answer"])


class TestFaqBot(unittest.TestCase):
    def setUp(self):
        self.data = load_faq()
        self.bot = FaqBot(self.data)

    def answer_for(self, question):
        for entry in self.data["faqs"]:
            if entry["question"] == question:
                return entry["answer"]
        raise KeyError(question)

    def test_hours(self):
        self.assertEqual(self.bot.answer("When are you open?"),
                         self.answer_for("What are your business hours?"))

    def test_emergency(self):
        self.assertEqual(self.bot.answer("I have a burst pipe, help!"),
                         self.answer_for("Do you offer emergency service?"))

    def test_price(self):
        self.assertEqual(self.bot.answer("How much do you charge?"),
                         self.answer_for("How much does a call-out cost?"))

    def test_drain(self):
        self.assertEqual(self.bot.answer("My kitchen sink is clogged"),
                         self.answer_for("Can you unclog drains?"))

    def test_case_insensitive(self):
        self.assertEqual(self.bot.answer("ARE YOU LICENSED?"),
                         self.answer_for("Are you licensed and insured?"))

    def test_unknown_falls_back(self):
        self.assertEqual(self.bot.answer("Do you sell pizza?"), self.data["fallback"])

    def test_generic_verb_does_not_match(self):
        self.assertEqual(self.bot.answer("Can you fix my roof?"), self.data["fallback"])

    def test_empty_falls_back(self):
        self.assertEqual(self.bot.answer(""), self.data["fallback"])
        self.assertEqual(self.bot.answer("   "), self.data["fallback"])

    def test_stopwords_only_falls_back(self):
        self.assertEqual(self.bot.answer("what is the"), self.data["fallback"])

    def test_answers_only_from_faq(self):
        allowed = {e["answer"] for e in self.data["faqs"]} | {self.data["fallback"]}
        for q in ["hours?", "pizza", "water heater broken", "free quote", "random words"]:
            self.assertIn(self.bot.answer(q), allowed)

    def test_custom_data(self):
        bot = FaqBot({"fallback": "I'll check with the owner.",
                      "faqs": [{"question": "Parking?", "keywords": ["parking"],
                                "answer": "Street parking only."}]})
        self.assertEqual(bot.answer("Is there parking?"), "Street parking only.")
        self.assertEqual(bot.answer("Hours?"), "I'll check with the owner.")


class TestTokenize(unittest.TestCase):
    def test_removes_stopwords_and_lowercases(self):
        self.assertEqual(tokenize("What ARE your Hours?"), ["hours"])


class TestDemoPage(unittest.TestCase):
    def test_index_html_has_no_external_resources(self):
        path = os.path.join(os.path.dirname(DEFAULT_FAQ_PATH), "index.html")
        with open(path, encoding="utf-8") as f:
            html = f.read().lower()
        for bad in ["http://", "https://", "fetch(", "xmlhttprequest", "websocket", "//cdn"]:
            self.assertNotIn(bad, html)

    def test_index_html_embeds_same_faq_data(self):
        path = os.path.join(os.path.dirname(DEFAULT_FAQ_PATH), "index.html")
        with open(path, encoding="utf-8") as f:
            html = f.read()
        start = html.index('id="faq-data">') + len('id="faq-data">')
        end = html.index("</script>", start)
        self.assertEqual(json.loads(html[start:end]), load_faq())


if __name__ == "__main__":
    unittest.main()
