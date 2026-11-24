# Starter Kit Templates

Copy these when onboarding a new client. The house rules they refer to are in
`../rules/` (see `../README.md` for the whole pack). Everything here is generic and uses
made-up businesses only.

| Path | What it is |
| --- | --- |
| `new-client-layout/` | Empty folder layout to copy and rename for each new client |
| `prompts/` | Prompt templates: receptionist, scheduler, follow-up writer |
| `onboarding-checklist.md` | Step-by-step checklist for setting up a new client |
| `CLIENT-README.md` | Plain-English guide to hand to the client |
| `tests/` | `unittest` checks that the templates and checklist are well-formed |

## Placeholders

Templates use `{{UPPER_SNAKE_CASE}}` placeholders, for example
`{{BUSINESS_NAME}}`. Replace every placeholder before going live.

## Running the tests

Python 3 standard library only, no network. Run from this folder:

```sh
cd starter-kit/templates
python3 -m unittest -v
```
