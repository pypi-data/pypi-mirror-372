"""Simple SQLite storage for trade entries.

The module provides two public helpers:

* :func:`init_db` – creates the ``trades`` table if it does not exist.
* :func:`save_trade` – inserts a new trade and returns the generated 16‑character
  identifier.

The database file ``tradejournal.db`` lives next to this module, making the
package self‑contained and writable from the virtual environment.
"""

from __future__ import annotations

import os
import sqlite3
import secrets
import datetime
from pathlib import Path
import yaml

# Resolve a path for the SQLite file that lives in the package directory.
# Store the SQLite database in the user's home directory under ``~/.tradejournal``.
# This location is consistent across OSes and keeps user data separate from the
# package source.
# Determine the configuration directory.
# If the environment variable ``TRADEJOURNAL_ROOT`` is set, use its value;
# otherwise fall back to ``~/.tradejournal``.
_config_root = os.getenv("TRADEJOURNAL_ROOT")
if _config_root:
    _USER_DIR = Path(_config_root).expanduser().resolve()
else:
    _USER_DIR = Path(os.path.expanduser("~/.tradejournal"))

# Ensure the directory exists before creating the database file.
_USER_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = _USER_DIR / "tradejournal.db"
CONFIG_PATH = _USER_DIR / "config.yaml"

# Connection is created lazily; we keep a module‑level reference for reuse.
_conn: sqlite3.Connection | None = None


def _get_connection() -> sqlite3.Connection:
    """Return a SQLite connection, creating it on first use.

    The connection uses ``detect_types`` so that ``datetime`` objects are stored and
    retrieved as ISO‑8601 strings.
    """
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        _conn.execute("PRAGMA foreign_keys = ON")
    return _conn


def init_db() -> None:
    """Create the ``trades`` table if it does not already exist.

    Columns:
        id        – 16‑character primary key (hex string).
        symbol    – ticker symbol (text).
        quantity  – number of shares/contracts (real).
        price     – execution price (real).
        risk      – risk amount or % (real).
        ts        – timestamp when the trade was added (datetime).
    """
    conn = _get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
            id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            risk REAL NOT NULL,
            ts TIMESTAMP NOT NULL
        )
        """
    )
    # Ensure the completions table exists with the required columns. We create it
    # if missing and add any absent columns to preserve existing data.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS completions (
            trade_id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            risk REAL NOT NULL,
            direction TEXT NOT NULL CHECK(direction IN ('up','down')),
            profit REAL NOT NULL DEFAULT 0,
            ts TIMESTAMP NOT NULL
        )
        """
    )
    # Add missing columns for older schemas (SQLite allows ADD COLUMN).
    existing = {row[1] for row in conn.execute("PRAGMA table_info(completions)")}
    required = {"symbol", "quantity", "price", "risk", "direction", "profit", "ts"}
    for col in required - existing:
        # Use generic types; constraints like NOT NULL are acceptable defaults.
        if col == "direction":
            conn.execute("ALTER TABLE completions ADD COLUMN direction TEXT NOT NULL DEFAULT 'up' CHECK(direction IN ('up','down'))")
        elif col == "ts":
            conn.execute("ALTER TABLE completions ADD COLUMN ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP")
        elif col == "symbol":
            conn.execute("ALTER TABLE completions ADD COLUMN symbol TEXT NOT NULL DEFAULT ''")
        elif col == "quantity":
            conn.execute("ALTER TABLE completions ADD COLUMN quantity REAL NOT NULL DEFAULT 0")
        elif col == "price":
            conn.execute("ALTER TABLE completions ADD COLUMN price REAL NOT NULL DEFAULT 0")
        elif col == "risk":
            conn.execute("ALTER TABLE completions ADD COLUMN risk REAL NOT NULL DEFAULT 0")
        elif col == "profit":
            conn.execute("ALTER TABLE completions ADD COLUMN profit REAL NOT NULL DEFAULT 0")
    conn.commit()

    # Ensure a default configuration file exists.
    _ensure_config()


def _generate_id() -> str:
    """Return a 16‑character hexadecimal identifier.

    ``secrets.token_hex(8)`` yields exactly 16 hex characters, providing a
    reasonably unique ID without requiring external libraries.
    """
    return secrets.token_hex(8)


def save_trade(symbol: str, quantity: float, price: float, risk: float) -> str:
    """Persist a trade and return its generated ID.

    The function ensures the database schema exists, generates a unique ID and
    stores the supplied values together with the current UTC timestamp.
    """
    init_db()
    trade_id = _generate_id()
    timestamp = datetime.datetime.utcnow()
    conn = _get_connection()
    conn.execute(
        "INSERT INTO trades (id, symbol, quantity, price, risk, ts) VALUES (?, ?, ?, ?, ?, ?)",
        (trade_id, symbol, quantity, price, risk, timestamp),
    )
    conn.commit()
    return trade_id

def list_trades(limit: int | None = None) -> list[tuple]:
    """Return stored trades as a list of rows.

    Each row is a tuple matching the ``trades`` table columns:
    ``(id, symbol, quantity, price, risk, ts)``.
    If ``limit`` is provided, only the most recent ``limit`` rows (ordered by
    timestamp descending) are returned.
    """
    conn = _get_connection()
    cur = conn.cursor()
    if limit is not None:
        cur.execute(
            "SELECT id, symbol, quantity, price, risk, ts FROM trades ORDER BY ts DESC LIMIT ?",
            (limit,),
        )
    else:
        cur.execute(
            "SELECT id, symbol, quantity, price, risk, ts FROM trades ORDER BY ts DESC"
        )
    return cur.fetchall()

def get_completed_ids() -> set[str]:
    """Return a set of trade IDs that have been marked completed.

    Used to filter out completed trades from the regular ``list`` view.
    """
    conn = _get_connection()
    cur = conn.execute("SELECT trade_id FROM completions")
    return {row[0] for row in cur.fetchall()}

def delete_trade(trade_id: str) -> bool:
    """Delete a trade by its identifier.

    Returns ``True`` if a row was deleted, ``False`` otherwise (e.g., the ID
    does not exist). The database schema is ensured to exist before the
    operation.
    """
    # Ensure the DB and table are present.
    init_db()
    conn = _get_connection()
    cur = conn.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
    conn.commit()
    return cur.rowcount > 0

def complete_trade(trade_id: str, direction: str) -> bool:
    """Mark a trade as completed with the given direction.

    ``direction`` must be either ``"up"`` or ``"down"``. The trade row is copied
    into the ``completions`` table (including its original details) before being
    removed from ``trades``. Returns ``True`` on success, ``False`` if the trade
    does not exist or an error occurs.
    """
    if direction not in {"up", "down"}:
        raise ValueError("direction must be 'up' or 'down'")
    conn = _get_connection()
    # Retrieve the full trade row.
    cur = conn.execute(
        "SELECT id, symbol, quantity, price, risk FROM trades WHERE id = ?",
        (trade_id,),
    )
    row = cur.fetchone()
    if not row:
        return False
    trade_id, symbol, quantity, price, risk = row
    timestamp = datetime.datetime.utcnow()
    try:
        # Compute profit based on direction.
        # Upside = price * (1 + risk * 0.02)
        # Downside = price * (1 - risk * 0.01)
        # Profit = Upside - price if up, else Downside - price.
        if direction == "up":
            profit_price = price * (1 + risk * 0.02)
        else:
            profit_price = price * (1 - risk * 0.01)
        # Profit is the difference between the adjusted price and the original
        # price, multiplied by the quantity to reflect total monetary profit.
        profit = (profit_price - price) * quantity

        # Insert into completions with full details, including profit.
        conn.execute(
            "INSERT OR REPLACE INTO completions (trade_id, symbol, quantity, price, risk, direction, profit, ts) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (trade_id, symbol, quantity, price, risk, direction, profit, timestamp),
        )
        # Remove from trades.
        conn.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
        conn.commit()
        return True
    except sqlite3.Error:
        return False

def list_completions() -> list[tuple]:
    """Return a list of completed trades.

    Each row is ``(trade_id, symbol, direction, ts)`` ordered by most recent
    completion first.
    """
    conn = _get_connection()
    cur = conn.execute(
        """
        SELECT trade_id, symbol, direction, ts, profit
        FROM completions
        ORDER BY ts DESC
        """
    )
    return cur.fetchall()

def _ensure_config() -> None:
    """Create ``config.yaml`` with defaults if it does not exist.

    The defaults are stored in a dictionary and written using ``yaml.safe_dump``
    for proper YAML formatting.
    """
    if not CONFIG_PATH.is_file():
        default_config = {
            "default_risk": 5,
            "verbosity": 2,
            # Updated column ordering; "BuyValue" renamed to "Value".
            "column_ordering": [
                "ID",
                "Symbol",
                "Qty",
                "Risk",
                "DownPrice",
                "Price",
                "UpPrice",
                "Timestamp",
                "Downside",
                "Value",
                "Upside",
            ],
        }
        # Use safe_dump to avoid arbitrary code execution on load.
        yaml.safe_dump(default_config, CONFIG_PATH.open("w"), default_flow_style=False)


def load_config() -> dict:
    """Load the YAML configuration file.

    Returns an empty dict if the file cannot be read for any reason.
    """
    try:
        with CONFIG_PATH.open("r") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}
