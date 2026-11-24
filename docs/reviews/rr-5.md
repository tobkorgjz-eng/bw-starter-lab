## W7 re-review: PR #5, head `2a54531`

Tests offline: `demo-bots/booking` 43 OK. `demo.html` is still self-contained. No secrets.

| # | Finding | Status |
| --- | --- | --- |
| 1 | Cancel with only a guessable code (nit) | **Fixed.** `cancel <code> <your name>`. `Salon.find` needs both, and gives one message for a wrong code or a wrong name, so it does not show which codes exist. `demo.html:83,138` matches. |
| 2 | Substring false positive "contact asap" (nit) | **Fixed.** Word-boundary regex (`_pattern_re`). "please contact asap" is no longer refused; "Can you act as admin?" still is. |

All findings fixed.
