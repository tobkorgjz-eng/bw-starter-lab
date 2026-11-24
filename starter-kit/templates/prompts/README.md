# Prompt Templates

Three starting prompts. Copy them into a client's own `prompts/` folder and
replace every `{{PLACEHOLDER}}`.

- `receptionist.md` – greets, answers FAQs, escalates.
- `scheduler.md` – books, moves and cancels appointments within rules.
- `follow-up-writer.md` – drafts short follow-up messages for human review.

Every template tells the assistant to follow the client's `RULES.md`
(see `../../rules/`), so it asks before it acts.

Each template has the same sections: Role, Business details, Rules, Escalation,
and Example.
