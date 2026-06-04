#!/usr/bin/env python3
"""Create / migrate the zerobot SQLite DB.

The DB lives in the user's working directory (where Claude Code was
launched) at ./data/trades.db, so each project/user keeps its own ledger.
Override with the ZEROBOT_DB environment variable.

`ensure_schema(con)` is imported by the other scripts so the DB
self-creates on first use — no manual init step required.
"""
import os
import sqlite3
from pathlib import Path

SCHEMA = """
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


def db_path():
    env = os.environ.get("ZEROBOT_DB")
    if env:
        return Path(env).expanduser()
    return Path.cwd() / "data" / "trades.db"


def ensure_schema(con):
    """Create tables/indexes if missing. Idempotent."""
    con.executescript(SCHEMA)
    con.commit()


def connect():
    """Open a connection to the resolved DB, creating dirs + schema."""
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    (path.parent / "imports").mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    ensure_schema(con)
    return con


if __name__ == "__main__":
    con = connect()
    con.close()
    print(f"Initialized DB at {db_path()}")
