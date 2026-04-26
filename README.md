# zerobot

A personal portfolio assistant for Zerodha investors, built as a thin layer of Claude Code slash commands over the Kite MCP and a local SQLite trade ledger. No webapp, no dashboard, no proactive alerts — pull-only via the Claude Code terminal.

Designed for the value investor who:
- Cares about holding period, cost basis, LTCG eligibility, and exit-vs-current-price
- Finds Zerodha Console trader-oriented and noisy
- Makes low-frequency, thesis-driven decisions

## Architecture

Three moving parts wired together by slash commands:

1. **Kite hosted MCP** (`https://mcp.kite.trade/mcp`) — live holdings, LTPs, today's executed trades. Configured in `.mcp.json`.
2. **Local SQLite** at `data/trades.db` — long-term memory of every BUY/SELL. Schema in `scripts/init_db.py`. Solves Kite's limited trade-history window.
3. **Slash commands** in `.claude/commands/` — the only entry points. They orchestrate Kite MCP calls + DB queries and render markdown tables back in chat.

Data flow is always **Kite → DB** (writes) and **DB + Kite → chat** (reads). Nothing writes back to Kite *automatically* — order placement is possible via the MCP but only on explicit user request.

## First time using zerobot? Quickstart

Five-minute tour from empty DB to a live portfolio view.

### 1. Clone and initialize

```bash
git clone https://github.com/dhruvmehra/zerobot.git
cd zerobot
python3 scripts/init_db.py
```

The init script creates `data/trades.db` (empty) and `data/imports/` (where you'll drop tradebook CSVs).

### 2. Open the folder in Claude Code

Either run `claude` from inside the `zerobot` folder, or open the folder via the Claude Code desktop app. The Kite MCP is already configured via `.mcp.json` — Claude will detect it.

### 3. Log into Kite

In Claude Code chat, type:

> log me into Kite

Claude responds with a clickable Zerodha auth link plus an AI-risk warning. Click it, complete the auth in your browser, return to chat and say *"done"*. The session persists for the rest of the conversation.

### 4. Export your trade history

Zerodha Console caps each Tradebook export at one FY, so you'll do this once per FY going back as far as your account history.

1. Go to [console.zerodha.com](https://console.zerodha.com) → **Reports → Tradebook**
2. Pick segment = **Equity**, set the date range to a financial year (Apr 1 → Mar 31)
3. Click **Download CSV**
4. Repeat for each FY

Drop every downloaded CSV into `data/imports/`.

### 5. Import them all

In chat:

> /import-tradebook

Walks every CSV, inserts new trades, and prints a summary (total trades, date range, BUY/SELL split, distinct symbols). Safe to re-run — duplicate trades are silently ignored.

### 6. See your portfolio

> /portfolio

Renders current holdings with first-buy date, days held, LTCG eligibility, unrealized P&L per stock, and totals.

### 7. Optional: build a watchlist

```
/watchlist add POWERGRID entry=255 EV grid value entry
/watchlist add CIPLA entry=1400 pharma inflection
/watchlist
```

Tracks stocks of interest with entry or exit price targets. The show view auto-fetches live LTPs and flags any name that has dropped into entry zone or risen into exit zone.

### What's next

- `/sync-trades` daily after market close to keep the DB current
- `/exits [days]` to spot stocks you sold that have come back below your exit price (re-entry signals)
- Ask Claude conversational questions: *"what's my realized P&L this FY?"*, *"which holdings are LTCG-eligible?"*, *"what sectors look attractive right now?"*

### Common first-time gotchas

- **Kite session expires** every few hours — slash commands auto-surface a fresh login link; just click and say done.
- **MCP transport breaks** (rare, shows *"Invalid session ID"*) — run `/mcp` to reconnect.
- **IPO allotments and bonus/split shares** don't appear in the equity tradebook export. If `/portfolio` shows quantity mismatches or blank "first bought" dates, tell Claude the corporate-action details — it can inject synthetic BUY rows so cost basis and LTCG timers stay correct.

## Slash commands

| Command | What it does |
|---|---|
| `/portfolio` | Current holdings, first-buy date per symbol from DB, days held, LTCG status, unrealized P&L |
| `/exits [days]` | Stocks you've sold within N days vs current LTP — re-entry signal |
| `/sync-trades` | Append today's executed Kite trades to the local DB (idempotent) |
| `/import-tradebook [path]` | Bulk import Zerodha Console Tradebook CSVs (one or all in `data/imports/`) |
| `/watchlist [add\|remove\|set] [SYMBOL] ...` | Track stocks of interest with optional entry/exit price targets |

Each command's full spec lives in its `.md` file under `.claude/commands/`.

## Notes on data correctness

The trades table uses `UNIQUE(trade_date, symbol, action, qty, price, order_id, trade_id)` so re-running imports is idempotent. A few corporate-action edge cases require manual handling (synthetic BUY rows) because they don't appear in the equity tradebook export:

- **IPO allotments** — not in the secondary-market tradebook; cost basis must be added manually
- **Stock splits** — adjust the existing BUY row's qty/price
- **Bonus issues** — add a synthetic BUY row at ₹0 cost basis on the record date (per Section 55(2)(aa)(iiia))
- **Demergers** — split each original BUY row into the demerged entities at the post-demerger cost-basis ratio

Claude can do these adjustments interactively — just describe the corporate action.

## Privacy

This repo contains zero personal trade data. The `.gitignore` excludes:
- `data/trades.db` — your actual trades and holdings
- `data/imports/` — your raw tradebook CSVs (which include your Zerodha client ID in filenames)
- `data/*.png` — any rendered portfolio/P&L charts
- `.claude/settings.local.json` — your local permission grants

Your data lives only on your machine.
