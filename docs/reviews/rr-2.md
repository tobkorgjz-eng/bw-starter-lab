## W7 re-review: PR #2, head `82f6e45`

Tests offline: `demo-bots/faq` 38 OK. `demo.html` is still self-contained (no URLs, src/href, fetch, XHR, WebSocket, innerHTML, storage). No secrets.

| # | Finding | Status |
| --- | --- | --- |
| 1 | Common phrases set off the injection reply (nit) | **Fixed.** `faq_bot.py` and `demo.html:231` count `you are now`/`act as`/`override`/`from now on` only next to `rules`/`instructions`/`prompt`/…. "Since you are now open Saturdays…", "From now on I live in Maple Valley…" and the thermostat "override" question get FAQ answers. "Ignore your rules…" still gets the injection reply. |

All findings fixed. (The reply to "You are now FreePlumberBot…" is now the fallback instead of the injection reply. That is still a fixed text, so it is fine.)
