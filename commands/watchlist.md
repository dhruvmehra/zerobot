---
description: Track stocks of interest with optional entry and/or exit price targets
argument-hint: "[add|remove|set] SYMBOL [entry=PRICE] [exit=PRICE] [notes...]  (no args = show)"
---

Manage the `watchlist` table in `data/trades.db`.

Arguments: $ARGUMENTS

**Routing:**
- No arguments → **show**
- First arg is `add` → **add**
- First arg is `remove` (or `rm`) → **remove**
- First arg is `set` → **update**

---

**show** (no args):

1. `SELECT symbol, exchange, entry_price, exit_price, notes FROM watchlist ORDER BY symbol;`
2. If empty, print "Watchlist is empty. Add with `/watchlist add SYMBOL entry=PRICE` or `exit=PRICE`." and stop.
3. Build a list of `exchange:symbol` instruments and call Kite MCP `get_ltp` for current prices in one call.
4. Render a markdown table:

   | Symbol | LTP | Entry @ | Exit @ | Status | Notes |

   - Show "—" for unset entry/exit prices.
   - **Status logic** (pick the most actionable):
     - If `exit_price` set and `LTP ≥ exit_price` → "🎯 exit zone (+X%)"
     - If `entry_price` set and `LTP ≤ entry_price` → "🎯 entry zone (-X%)"
     - Else if `entry_price` set → "watching, +X% above entry"
     - Else if `exit_price` set → "watching, -X% to exit"
     - Else → "watching"
   - Sort: rows in entry/exit zone first, then by smallest distance to nearest target.
5. Below the table, summarize: *"N name(s) in entry zone: ...   M name(s) in exit zone: ...."* (omit halves with zero counts).
6. **Kite session handling:**
   - If `get_ltp` returns *"Please log in first"*: immediately call `mcp__kite__login`, render the URL as a clickable markdown link with the ⚠️ AI-risk warning, and pause. After user confirms login, retry the LTP fetch and finish the table.
   - If `get_ltp` returns *"Invalid session ID"* (transport error): do NOT call login (it will fail too). Tell the user to run `/mcp` to reconnect the Kite MCP server, then re-invoke `/watchlist`. Render the watchlist rows without LTP/status columns so the user can still see what they're tracking.

---

**add** (`/watchlist add SYMBOL [entry=PRICE] [exit=PRICE] [notes...]`):

1. Parse: `SYMBOL` is required, uppercase it. Default `exchange='NSE'`. (If user passes `BSE:SYMBOL`, split on `:` for exchange.)
2. Look for `entry=NUMBER` and `exit=NUMBER` tokens (case-insensitive) in the remaining args. Either, both, or neither may appear.
3. Everything else (after stripping `entry=…` and `exit=…`) becomes the notes string, joined by spaces.
4. `INSERT OR REPLACE INTO watchlist (symbol, exchange, entry_price, exit_price, notes) VALUES (?, ?, ?, ?, ?);`
5. Confirm in one line with the values that were stored. Omit fields that are null.

Examples the user might type:
- `/watchlist add POWERGRID entry=250 EV grid value entry`
- `/watchlist add PAYTM exit=1300 trim partial here`
- `/watchlist add NTPC entry=350 exit=500 both targets`
- `/watchlist add SRF entry=2200 specialty chem contrarian`

---

**remove** (`/watchlist remove SYMBOL` or `/watchlist rm SYMBOL`):

1. `DELETE FROM watchlist WHERE symbol = ?;` (uppercased)
2. If no rows changed, say *"SYMBOL was not on the watchlist."* Otherwise *"Removed SYMBOL."*

---

**set** (`/watchlist set SYMBOL [entry=PRICE] [exit=PRICE] [notes...]`):

1. Parse `entry=…` and `exit=…` tokens like in `add`. A token of `entry=-` or `entry=none` clears that price (set to NULL). Same for `exit`.
2. `UPDATE watchlist SET entry_price = COALESCE(?, entry_price), exit_price = COALESCE(?, exit_price), notes = COALESCE(?, notes) WHERE symbol = ?;`
3. If no row matched, suggest `/watchlist add` instead.

---

Keep all output compact. No commentary unless asked.
