---
description: Show stocks I've sold with exit price vs current price (re-entry signal)
argument-hint: "[days] (default 180)"
---

Show my recent exits and where those stocks are trading now.

Arguments: $ARGUMENTS (number of days to look back; default 180)

Steps:
1. Query `data/trades.db` for all SELL trades within the lookback window. Group by symbol. For each symbol compute:
   - total_sold_qty
   - weighted_avg_exit_price
   - last_sell_date
2. For each symbol, call Kite MCP to get the current LTP (use the `exchange` stored in the trade row, default NSE).
3. Render a markdown table sorted by `pct_below_exit` descending (best re-entry opportunities first):
   Stock | Last sold | Sold qty | Avg exit ₹ | Current ₹ | % vs exit | Signal
   - `% vs exit = (current - avg_exit) / avg_exit * 100`
   - `Signal`: "↓ reentry zone" if current is >3% below exit, "≈ near exit" if within ±3%, "↑ moved up" if >3% above.
4. After the table, in one line: *"N stocks are trading below your exit price — the biggest gap is X at Y% below."*

Be concise. Skip symbols where MCP can't resolve a quote and note them at the end in one line.

---

**Kite session handling:**

- If a Kite call returns *"Please log in first"*: immediately call `mcp__kite__login`, render the returned URL as a clickable markdown link with the ⚠️ AI-risk warning, and pause. Resume after user confirms login.
- If a Kite call returns *"Invalid session ID"* (transport error): tell the user to run `/mcp` to reconnect, then re-invoke this command. Do not call login — it will fail too.
