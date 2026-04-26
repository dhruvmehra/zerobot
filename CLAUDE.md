# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

**zerobot** is a personal portfolio assistant for a Zerodha value investor. It is not a webapp, service, or dashboard — it is a thin layer of slash commands and Python scripts that Claude Code drives from the terminal. The "UI" is the Claude Code REPL.

## Architecture

Three moving parts wired together by slash commands:

1. **Kite hosted MCP** (`https://mcp.kite.trade/mcp`, configured in `.mcp.json`) — live holdings, LTPs, and today's executed trades. Kite only retains a limited trade-history window, which is the reason for (2).
2. **Local SQLite** at `data/trades.db` (project-relative; resolved in `scripts/` via `Path(__file__).resolve().parent.parent / "data" / "trades.db"`) — the long-term memory of every BUY/SELL. Schema in `scripts/init_db.py`. The `UNIQUE(trade_date, symbol, action, qty, price, order_id)` constraint is load-bearing: it makes `/sync-trades` and CSV re-imports idempotent via `INSERT OR IGNORE`.
3. **Slash commands** in `.claude/commands/` — the only entry points users invoke. They orchestrate Kite MCP calls + DB queries and render markdown tables back in chat.

Bootstrap flow: user exports a Zerodha Console **Tradebook** CSV (not the P&L statement — that's a different, aggregated report without per-trade rows) → drops it in `data/imports/` → runs `/import-tradebook` (one-time historical load) → runs `/sync-trades` daily to append new trades from Kite MCP.

## Slash commands → where the work actually happens

| Command | What it does | Touches |
|---|---|---|
| `/portfolio` | Current holdings + first-buy date + LTCG status | Kite MCP (holdings, LTP) + DB (earliest BUY per symbol) |
| `/exits` | Sold stocks vs current price — re-entry signal | DB (SELLs within N days) + Kite MCP (LTPs) |
| `/sync-trades` | Append today's Kite trades to DB | Kite MCP → DB |
| `/import-tradebook [path]` | Import Zerodha Console CSV(s) into DB | `scripts/import_tradebook.py` |
| `/watchlist [add\|remove\|set] [SYMBOL] [buy_zone] [notes]` | Track stocks of interest with optional buy-zone price | DB (`watchlist` table) + Kite MCP for LTP |

Data flow direction is always **Kite → DB** (writes) and **DB + Kite → chat** (reads). Nothing writes back to Kite.

## Common commands

```bash
# Create / migrate the SQLite DB (idempotent)
python3 scripts/init_db.py

# Manually import one CSV (the /import-tradebook command calls this)
python3 scripts/import_tradebook.py <path-to-csv>

# Inspect the DB
sqlite3 data/trades.db ".schema trades"
sqlite3 data/trades.db "SELECT COUNT(*), MIN(trade_date), MAX(trade_date) FROM trades;"
```

There are no tests, no linter, no build step — the repo is ~100 lines of Python plus markdown command specs.

## Extending

When adding portfolio/trade features: extend an existing slash command or add a new one in `.claude/commands/`, and extend the `trades` schema in `scripts/init_db.py` if needed. The CSV importer in `scripts/import_tradebook.py` uses substring-matched column picking (`pick(row, "trade date", "date")`) to tolerate Zerodha export drift — keep that tolerance if you touch it.

User is a **value investor, not a trader**: features should frame around holding period, cost basis, LTCG, and exit-vs-current-price — not intraday, F&O, or technicals. Don't propose dashboards, webapps, or BI tools; the chat-query-only design was deliberate.
