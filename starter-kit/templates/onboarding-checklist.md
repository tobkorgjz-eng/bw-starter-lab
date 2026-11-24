# New Client Onboarding Checklist

Work through each step in order. Tick a box only when the step is fully done.
Client: {{BUSINESS_NAME}}

## 1. Kick-off

- [ ] Confirm the client's business name, hours and service area
- [ ] Agree which assistant roles they want (receptionist, scheduler, follow-up writer)
- [ ] Agree the tone of voice and any words to avoid
- [ ] Name the team contact who handles escalations

## 2. Folder setup

- [ ] Copy `new-client-layout/` to a new folder named after the client (lowercase, hyphens)
- [ ] Fill in `config/` with business details (no passwords or keys)
- [ ] Copy the needed templates from `prompts/` into the client's `prompts/` folder
- [ ] Copy `starter-kit/rules/RULES.md` into the client's `rules/` folder
- [ ] Edit the rules with the client: may do alone, needs the owner's yes, never does
- [ ] Add frequently asked questions to `knowledge/`

## 3. Prompt setup

- [ ] Replace every `{{PLACEHOLDER}}` in the client's prompts
- [ ] Check that opening hours match in every prompt
- [ ] Check that escalation instructions name the right team contact

## 4. Testing

- [ ] Try ten sample conversations using made-up customer details
- [ ] Confirm the assistant hands off anything it cannot answer
- [ ] Run `check_rules.py` on a sample plan and confirm it asks before "needs a yes" actions
- [ ] Confirm the assistant refuses payment details and advice it should not give
- [ ] Record the results in `notes/`

## 5. Go-live

- [ ] Send the client a filled-in copy of `CLIENT-README.md`
- [ ] Agree a go-live date and a review date two weeks later
- [ ] Client signs off on the test results

## 6. After go-live

- [ ] Review the first week of `logs/` with the client
- [ ] Update prompts and FAQs based on what was learned
