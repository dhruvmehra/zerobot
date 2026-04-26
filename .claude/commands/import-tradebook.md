---
description: Import a Zerodha Console tradebook CSV into the local trades DB
argument-hint: "[path-to-csv] (defaults to data/imports/*.csv)"
---

Import Zerodha Console tradebook CSV(s) into `data/trades.db`.

Arguments: $ARGUMENTS

Steps:
1. If a path was given, use it. Otherwise list every `*.csv` under `data/imports/` (relative to the project root) and import each.
2. For each file, run: `python3 scripts/import_tradebook.py <path>` from the project root.
3. After all imports finish, run a quick summary query on the DB and print:
   - total trades, earliest trade date, latest trade date
   - count of BUY vs SELL
   - distinct symbols
4. If any file returned many "skipped" rows, flag it — the CSV format may be non-standard and worth inspecting.
