#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "trades.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
(DB_PATH.parent / "imports").mkdir(parents=True, exist_ok=True)

schema = """
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date TEXT NOT NULL,
    symbol TEXT NOT NULL,
    exchange TEXT,
    action TEXT NOT NULL CHECK(action IN ('BUY','SELL')),
    qty REAL NOT NULL,
    price REAL NOT NULL,
    order_id TEXT,
    trade_id TEXT,
    source TEXT NOT NULL,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(trade_date, symbol, action, qty, price, order_id, trade_id)
);

CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_date ON trades(trade_date);
CREATE INDEX IF NOT EXISTS idx_trades_action ON trades(action);

CREATE TABLE IF NOT EXISTS watchlist (
    symbol TEXT PRIMARY KEY,
    exchange TEXT NOT NULL DEFAULT 'NSE',
    entry_price REAL,
    exit_price REAL,
    notes TEXT,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

con = sqlite3.connect(DB_PATH)
con.executescript(schema)
con.commit()
con.close()
print(f"Initialized DB at {DB_PATH}")
