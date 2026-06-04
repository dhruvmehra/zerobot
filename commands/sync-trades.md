---
description: Pull today's trades from Kite MCP and append to the local trades DB
---

Sync today's trades from Kite MCP into `data/trades.db`.

Steps:
1. Call the Kite MCP tool that returns today's executed trades.
2. For each trade, insert into the `trades` table with `source = 'kite_mcp'`. The UNIQUE constraint on `(trade_date, symbol, action, qty, price, order_id)` makes re-runs idempotent — duplicates are silently ignored.
3. Print: *"Synced N new trades (M already existed)."*
4. If zero trades today, just say so — don't error.

---

**Kite session handling:**

- If the Kite call returns *"Please log in first"*: immediately call `mcp__kite__login`, render the returned URL as a clickable markdown link with the ⚠️ AI-risk warning, and pause. Resume after user confirms login.
- If the Kite call returns *"Invalid session ID"* (transport error): tell the user to run `/mcp` to reconnect, then re-invoke this command. Do not call login — it will fail too.
