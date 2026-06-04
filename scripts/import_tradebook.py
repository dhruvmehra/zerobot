#!/usr/bin/env python3
"""
Import a Zerodha Console Tradebook CSV into the local SQLite trades DB.

Usage: python3 import_tradebook.py <path-to-csv>

The Zerodha tradebook export has columns like:
  Symbol, ISIN, Trade Date, Exchange, Segment, Series, Trade Type,
  Auction, Quantity, Price, Trade ID, Order ID, Order Execution Time

This script is tolerant: it lowercases headers and matches on substring
so small variations in export format don't break the import.
"""
import csv
import sys
from pathlib import Path

# Sibling import — when run as a script, scripts/ is on sys.path[0].
from init_db import connect, db_path

if len(sys.argv) < 2:
    print("Usage: import_tradebook.py <csv_path>")
    sys.exit(1)

csv_path = Path(sys.argv[1]).expanduser()
if not csv_path.exists():
    print(f"File not found: {csv_path}")
    sys.exit(1)


def pick(row, *candidates):
    for key in row:
        low = key.lower().strip().replace("_", " ")
        for c in candidates:
            if c in low:
                return row[key]
    return None


con = connect()
cur = con.cursor()

inserted = 0
skipped = 0

with open(csv_path, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        symbol = pick(row, "symbol")
        trade_date = pick(row, "trade date", "date")
        exchange = pick(row, "exchange")
        action_raw = pick(row, "trade type", "type", "buy/sell")
        qty = pick(row, "quantity", "qty")
        price = pick(row, "price")
        trade_id = pick(row, "trade id")
        order_id = pick(row, "order id")

        if not (symbol and trade_date and action_raw and qty and price):
            skipped += 1
            continue

        action = action_raw.strip().upper()
        if action.startswith("B"):
            action = "BUY"
        elif action.startswith("S"):
            action = "SELL"
        else:
            skipped += 1
            continue

        try:
            cur.execute(
                """INSERT OR IGNORE INTO trades
                   (trade_date, symbol, exchange, action, qty, price,
                    order_id, trade_id, source)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    trade_date.strip(),
                    symbol.strip().upper(),
                    (exchange or "").strip().upper(),
                    action,
                    float(qty),
                    float(price),
                    (order_id or "").strip(),
                    (trade_id or "").strip(),
                    "console_csv",
                ),
            )
            if cur.rowcount:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"Row error: {e} — {row}")
            skipped += 1

con.commit()
con.close()
print(f"Imported {inserted} trades, skipped {skipped} from {csv_path.name}")
