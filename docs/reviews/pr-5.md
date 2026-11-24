## W7 review: PR #5 (booking bot), head `50e75ad`

**Checks**
- Tests, offline (network namespace disabled): `demo-bots/booking` 36 OK (`test_booking`, `test_safety`, `test_demo_html`).
- `demo.html` is self-contained: no `http(s)://`, `src=`, `href=`, `<link>`, `@import`, `url(`, `fetch`, `XMLHttpRequest`, `WebSocket` or `sendBeacon`. Output uses `textContent`, and there is no storage.
- Secrets/tokens: none. Wording: none (the README is careful: "a simple tripwire, not a complete filter"). Network: none.

**Findings**

No blocking findings. The ask-before-acting gate holds. Only an exact yes/no word counts ("yes please" and a new `book` command while a question is open are both refused), the slot is checked again at "yes", and the name rule stops a name imitating a bot reply.

1. *Nit, before anyone shares a `Salon` between customers:* `demo-bots/booking/booking.py:157` makes sequential codes (`MC001`, `MC002`, ...). `booking.py:268-273` (`_ask_cancel`) shows the full booking, customer name included, and lets anyone cancel it with only the code. So in a shared schedule, anyone could step through codes, read other customers' names and times, and cancel their bookings. In the current demo each tab or process holds its own schedule, so the risk is only on paper today.
   *Fix:* use `cancel <code> <name>` and refuse unless the name matches, or use random codes from `secrets.token_hex(3)` with an injectable generator for tests. Mention the limit in the README "Limits" line.
2. *Nit, false positives:* `booking.py:51` (`INJECTION_PATTERNS`) is a substring check, so "act as" fires inside "please cont**act as**ap". *Fix:* match on word boundaries (`re.search(r"\b" + re.escape(p) + r"\b", low)`), in `demo.html` as well, plus a test.
