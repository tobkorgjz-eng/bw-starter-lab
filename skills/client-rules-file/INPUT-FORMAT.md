# Answers file format (input to `rules_tool.py build`)

One JSON object, UTF-8. This is the hand-off point from the client-intake
skill: whatever the intake collects, these fields are what the rules file
needs.

| Field | Required | Type | Meaning |
| --- | --- | --- | --- |
| `business_name` | yes | text | Name as the owner writes it. Becomes the title. |
| `owner_name` | yes | text | The one person who can give the assistant a yes. |
| `ask_channel` | yes | text | How the assistant asks the owner (e.g. "text message to the shop phone"). |
| `may_do_alone` | yes | list of text | Actions the assistant may take without asking. |
| `ask_first` | yes | list of text | Actions that need the owner's yes first. |
| `never_do` | yes | list of text | Actions the assistant never takes. |
| `business_type` | no | text | Short description, shown in About. |
| `answer_wait` | no | text | What to do while waiting for an answer. |
| `notes` | no | text | Anything else the owner wants written down. |

Rules for the lists:

- Each list needs at least one item.
- One action per item, one short sentence. A trailing full stop is dropped
  and extra spaces are collapsed.
- The same action must not appear in two lists.

Unknown fields are ignored, so an intake file with extra answers can be
passed in as is.

Example: [examples/maple-lane-bakery/answers.json](examples/maple-lane-bakery/answers.json).

## From a client-intake brief

`rules_tool.py from-brief BRIEF.md -o answers.json` builds this file from
a brief in the client-intake format (`skills/client-intake/`):

| Brief | Answers field |
| --- | --- |
| `# Client brief: <name>` | `business_name` |
| `- Owner / final yes: <name>, <role>` (People) | `owner_name` (text before the comma) |
| `- How to ask for a yes: …` (People) | `ask_channel` |
| `- What it does: …` (Business) | `business_type` |
| `## May do alone` | `may_do_alone` |
| `## Needs the owner's yes` | `ask_first` |
| `## Never does` | `never_do` |
| `- Backup yes: …`, `## Limits and exceptions` | `notes` |

A brief item like `` `offer_discount` — offer any discount `` becomes
"Offer any discount (offer_discount)". Test fixture:
[fixtures/brief-willowbrook-dog-grooming.md](fixtures/brief-willowbrook-dog-grooming.md).
