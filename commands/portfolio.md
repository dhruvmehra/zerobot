---
description: Show current holdings with buy date, cost basis, gain/loss, and LTCG status
---

Show my current portfolio.

Steps:
1. Call the Kite MCP tool to fetch current holdings (symbol, qty, avg cost, last price).
2. For each holding, look up the **earliest BUY trade_date** from `data/trades.db` (trades table) to show when the position was first opened. If the symbol has no trades in the DB, leave the buy date blank.
3. Compute for each row:
   - `unrealized_rupees = (last_price - avg_cost) * qty`
   - `unrealized_pct = (last_price - avg_cost) / avg_cost * 100`
   - `days_held = today - earliest_buy_date`
   - `ltcg_status`: "✓ eligible" if days_held >= 365, else "in N days"
4. Render a markdown table sorted by `unrealized_rupees` descending. Columns:
   Stock | First bought | Days | Qty | Avg cost | LTP | Unrealized ₹ | % | LTCG
5. Below the table print: total invested, total current value, total unrealized P&L (₹ and %).

Keep the output compact. No commentary unless I ask a follow-up.

---

**Kite session handling (applies to every step that calls Kite MCP):**

- If a Kite call returns *"Please log in first"* or any auth-required error: immediately call `mcp__kite__login`, render the returned URL as a clickable markdown link with the standard ⚠️ AI-risk warning, and pause. Resume from where you stopped after the user confirms login.
- If a Kite call returns *"Invalid session ID"* or a transport-level error: do NOT call `mcp__kite__login` (it will fail the same way). Tell the user the MCP connection is broken and instruct them to run `/mcp` (Claude Code's MCP-reconnect command) and then re-invoke this slash command. Stop.
