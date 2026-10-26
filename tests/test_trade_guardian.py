"""
Tests for TradeGuardian.
"""
import sys
from pathlib import Path

SDK_PATH = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SDK_PATH))

import csv
from datetime import datetime, timedelta, timezone

import pytest

from athena.tools.trade_guardian import TradeGuardian


@pytest.fixture
def temp_journal(tmp_path):
    csv_path = tmp_path / "trade_journal.csv"
    headers = ["trade_id", "pair", "direction", "entry_time", "exit_time", "entry_price", "exit_price", "pnl", "notes"]
    now = datetime.now(timezone.utc)

    trades = [
        # sweet spot (0-15m)
        ["1", "EURUSD", "LONG", (now - timedelta(minutes=10)).isoformat(), now.isoformat(), "1.1", "1.2", "100", ""],
        ["2", "EURUSD", "LONG", (now - timedelta(minutes=12)).isoformat(), now.isoformat(), "1.1", "1.2", "-50", ""],
        # optimal (15-60m)
        ["3", "EURUSD", "LONG", (now - timedelta(minutes=30)).isoformat(), now.isoformat(), "1.1", "1.2", "200", ""],
        ["4", "EURUSD", "LONG", (now - timedelta(minutes=45)).isoformat(), now.isoformat(), "1.1", "1.2", "-100", ""],
        # danger (60-120m)
        ["5", "EURUSD", "LONG", (now - timedelta(minutes=90)).isoformat(), now.isoformat(), "1.1", "1.2", "50", ""],
        ["6", "EURUSD", "LONG", (now - timedelta(minutes=100)).isoformat(), now.isoformat(), "1.1", "1.2", "-150", ""],
        # ruin zone (>120m)
        ["7", "EURUSD", "LONG", (now - timedelta(minutes=150)).isoformat(), now.isoformat(), "1.1", "1.2", "-500", ""],
        ["8", "EURUSD", "LONG", (now - timedelta(minutes=200)).isoformat(), now.isoformat(), "1.1", "1.2", "-1000", ""],
        # 5-15 mins
        ["9", "EURUSD", "LONG", (now - timedelta(minutes=8)).isoformat(), now.isoformat(), "1.1", "1.2", "300", ""],
        ["10", "EURUSD", "LONG", (now - timedelta(minutes=14)).isoformat(), now.isoformat(), "1.1", "1.2", "250", ""],
    ]

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(trades)

    return csv_path

def test_load_journal(temp_journal):
    tg = TradeGuardian(temp_journal)
    trades = tg.load_journal()
    assert len(trades) == 10
    assert "duration_minutes" in trades[0]

def test_duration_computation_accuracy(temp_journal):
    tg = TradeGuardian(temp_journal)
    trades = tg.load_journal()
    assert abs(trades[0]["duration_minutes"] - 10) < 0.1

def test_bucket_classification_correctness(temp_journal):
    tg = TradeGuardian(temp_journal)
    analysis = tg.duration_analysis()
    assert analysis["sweet_spot"]["count"] == 4  # 10, 12, 8, 14 mins
    assert analysis["optimal"]["count"] == 2
    assert analysis["danger"]["count"] == 2
    assert analysis["ruin_zone"]["count"] == 2

def test_win_rate_calculation(temp_journal):
    tg = TradeGuardian(temp_journal)
    analysis = tg.duration_analysis()
    # sweet spot: 3 wins (100, 300, 250), 1 loss (-50) -> 75%
    assert analysis["sweet_spot"]["win_rate"] == 0.75

def test_profit_factor_calculation(temp_journal):
    tg = TradeGuardian(temp_journal)
    analysis = tg.duration_analysis()
    # sweet spot: wins=650, losses=50 -> 650/50 = 13.0
    assert analysis["sweet_spot"]["profit_factor"] == 13.0

def test_check_active_trade_green(temp_journal):
    tg = TradeGuardian(temp_journal)
    entry = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
    res = tg.check_active_trade(entry)
    assert res["alert_level"] == "green"
    assert res["warning_message"] is None

def test_check_active_trade_yellow(temp_journal):
    tg = TradeGuardian(temp_journal)
    entry = (datetime.now(timezone.utc) - timedelta(minutes=40)).isoformat()
    res = tg.check_active_trade(entry)
    assert res["alert_level"] == "yellow"
    assert res["warning_message"] == "Approaching optimal exit window"

def test_check_active_trade_red(temp_journal):
    tg = TradeGuardian(temp_journal)
    entry = (datetime.now(timezone.utc) - timedelta(minutes=55)).isoformat()
    res = tg.check_active_trade(entry)
    assert res["alert_level"] == "red"
    assert res["warning_message"] == "EXIT NOW — 60-minute guillotine imminent"

def test_check_active_trade_critical(temp_journal):
    tg = TradeGuardian(temp_journal)
    entry = (datetime.now(timezone.utc) - timedelta(minutes=70)).isoformat()
    res = tg.check_active_trade(entry)
    assert res["alert_level"] == "critical"
    assert res["warning_message"] == "HOLDING LIMIT BREACHED — empirical ruin zone"

def test_sweet_spot_stats(temp_journal):
    tg = TradeGuardian(temp_journal)
    stats = tg.sweet_spot_stats()
    assert stats["count"] == 4

def test_ruin_zone_trades(temp_journal):
    tg = TradeGuardian(temp_journal)
    ruin = tg.ruin_zone_trades()
    assert len(ruin) == 2
    assert float(ruin[0]["pnl"]) == -500.0

def test_empty_journal(tmp_path):
    csv_path = tmp_path / "empty.csv"
    with open(csv_path, "w") as f:
        f.write("trade_id,pair,direction,entry_time,exit_time,entry_price,exit_price,pnl,notes\n")
    tg = TradeGuardian(csv_path)
    trades = tg.load_journal()
    assert len(trades) == 0

def test_missing_columns(tmp_path):
    csv_path = tmp_path / "bad.csv"
    with open(csv_path, "w") as f:
        f.write("trade_id,pair\n")
        f.write("1,EURUSD\n")
    tg = TradeGuardian(csv_path)
    with pytest.raises(ValueError, match="Missing columns"):
        tg.load_journal()

def test_generate_report(temp_journal):
    tg = TradeGuardian(temp_journal)
    report = tg.generate_report()
    assert "=== Trade Duration Analysis Report ===" in report
    assert "[SWEET_SPOT]" in report
    assert "Win Rate: 75.0%" in report

def test_missing_journal_file_raises_error(tmp_path):
    missing_path = tmp_path / "nonexistent_journal.csv"
    tg = TradeGuardian(missing_path)
    with pytest.raises(FileNotFoundError, match="Trade journal not found"):
        tg.load_journal()
    with pytest.raises(FileNotFoundError, match="Trade journal not found"):
        tg.generate_report()


@pytest.fixture
def temp_sqlite_journal(tmp_path):
    import sqlite3
    db_path = tmp_path / "journal.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instrument TEXT NOT NULL,
            direction TEXT NOT NULL,
            risk_usd REAL,
            realized_pnl REAL NOT NULL,
            time_entered TEXT,
            time_exited TEXT,
            duration_minutes INTEGER,
            process_type TEXT,
            notes TEXT
        )
    """)
    now = datetime.now(timezone.utc)
    cur.executemany("""
        INSERT INTO campaigns (instrument, direction, risk_usd, realized_pnl, time_entered, time_exited, duration_minutes, process_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        ("XAUUSD", "BUY", 100.0, 150.0, (now - timedelta(minutes=10)).isoformat(), now.isoformat(), 10, "Good Process"),
        ("BTCUSD", "SELL", 100.0, -50.0, (now - timedelta(minutes=12)).isoformat(), now.isoformat(), 12, "Good Process"),
        ("XAUUSD", "BUY", 100.0, 300.0, (now - timedelta(minutes=30)).isoformat(), now.isoformat(), 30, "Good Process"),
        ("EURUSD", "BUY", 100.0, -100.0, (now - timedelta(minutes=45)).isoformat(), now.isoformat(), 45, "Good Process"),
        ("XAUUSD", "SELL", 100.0, 50.0, (now - timedelta(minutes=90)).isoformat(), now.isoformat(), 90, "Bad Process"),
        ("BTCUSD", "BUY", 100.0, -150.0, (now - timedelta(minutes=100)).isoformat(), now.isoformat(), 100, "Bad Process"),
        ("XAUUSD", "BUY", 100.0, -500.0, (now - timedelta(minutes=150)).isoformat(), now.isoformat(), 150, "Bad Process"),
        ("BTCUSD", "SELL", 100.0, -1000.0, (now - timedelta(minutes=200)).isoformat(), now.isoformat(), 200, "System Drift"),
    ])
    conn.commit()
    conn.close()
    return db_path


def test_sqlite_journal_loading(temp_sqlite_journal):
    tg = TradeGuardian(temp_sqlite_journal)
    trades = tg.load_journal()
    assert len(trades) == 8
    assert trades[0]["pair"] == "XAUUSD"
    assert trades[0]["duration_minutes"] == 10
    assert trades[0]["pnl"] == 150.0
    analysis = tg.duration_analysis()
    assert analysis["sweet_spot"]["count"] == 2
    assert analysis["optimal"]["count"] == 2
    assert analysis["danger"]["count"] == 2
    assert analysis["ruin_zone"]["count"] == 2
    report = tg.generate_report()
    assert "=== Trade Duration Analysis Report ===" in report
    assert "[SWEET_SPOT]" in report


def test_sqlite_journal_computed_duration(tmp_path):
    import sqlite3
    db_path = tmp_path / "journal_computed.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instrument TEXT NOT NULL,
            direction TEXT NOT NULL,
            realized_pnl REAL NOT NULL,
            time_entered TEXT,
            time_exited TEXT,
            duration_minutes INTEGER
        )
    """)
    now = datetime.now(timezone.utc)
    cur.execute("""
        INSERT INTO campaigns (instrument, direction, realized_pnl, time_entered, time_exited, duration_minutes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("XAUUSD", "BUY", 75.0, (now - timedelta(minutes=25)).isoformat(), now.isoformat(), None))
    conn.commit()
    conn.close()

    tg = TradeGuardian(db_path)
    trades = tg.load_journal()
    assert len(trades) == 1
    assert abs(trades[0]["duration_minutes"] - 25) < 0.1
    assert trades[0]["pnl"] == 75.0


def test_journal_auto_discovery_env(temp_sqlite_journal, monkeypatch):
    monkeypatch.setenv("ATHENA_TRADE_JOURNAL_PATH", str(temp_sqlite_journal))
    tg = TradeGuardian()
    assert tg.journal_path == temp_sqlite_journal
    trades = tg.load_journal()
    assert len(trades) == 8


