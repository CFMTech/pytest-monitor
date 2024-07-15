# -*- coding: utf-8 -*-
from __future__ import annotations
import os
import sqlite3
import sys
import pytest

try:
    import psycopg
except ImportError:
    import psycopg2 as psycopg

from pytest_monitor.handler import PostgresDBHandler, SqliteDBHandler


# helper function
def reset_db(db_context: psycopg.Connection | sqlite3.Connection):
    """Empty all tables inside the database to provide a clean slate for the next test."""
    # cleanup_cursor.execute("DROP DATABASE postgres")
    # cleanup_cursor.execute("CREATE DATABASE postgres")
    cleanup_cursor = db_context.cursor()
    cleanup_cursor.execute("DROP TABLE IF EXISTS TEST_METRICS")
    cleanup_cursor.execute("DROP TABLE IF EXISTS TEST_SESSIONS")
    cleanup_cursor.execute("DROP TABLE IF EXISTS EXECUTION_CONTEXTS")
    db_context.commit()
    cleanup_cursor.close()

    # cleanup_cursor.execute("CREATE SCHEMA public;")
    # cleanup_cursor.execute("ALTER DATABASE postgres SET search_path TO public;")
    # cleanup_cursor.execute("ALTER ROLE postgres SET search_path TO public;")
    # cleanup_cursor.execute("ALTER SCHEMA public OWNER to postgres;")
    # cleanup_cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
    # cleanup_cursor.execute("GRANT ALL ON SCHEMA public TO public;")


@pytest.fixture()
def connected_PostgresDBHandler():
    """Provide a DBHandler connected to a Postgres database."""
    os.environ["PYTEST_MONITOR_DB_NAME"] = "postgres"
    os.environ["PYTEST_MONITOR_DB_USER"] = "postgres"
    os.environ["PYTEST_MONITOR_DB_PASSWORD"] = "testing_db"
    os.environ["PYTEST_MONITOR_DB_HOST"] = "localhost"
    os.environ["PYTEST_MONITOR_DB_PORT"] = "5432"
    db = PostgresDBHandler()
    yield db
    reset_db(db._PostgresDBHandler__cnx)
    db._PostgresDBHandler__cnx.close()


def test_sqlite_handler():
    """Test for working sqlite database"""
    # db handler
    db = SqliteDBHandler(":memory:")
    session, metrics, exc_context = db.query(
        "SELECT name FROM sqlite_master where type='table'", (), many=True
    )
    assert session[0] == "TEST_SESSIONS"
    assert metrics[0] == "TEST_METRICS"
    assert exc_context[0] == "EXECUTION_CONTEXTS"


def test_postgres_handler(connected_PostgresDBHandler):
    """Test for working postgres database"""
    db = connected_PostgresDBHandler
    tables = db.query(
        "SELECT tablename FROM pg_tables where schemaname='public'",
        (),
        many=True,
    )
    tables = [table for (table,) in tables]
    try:
        assert "test_sessions" in tables
        assert "test_metrics" in tables
        assert "execution_contexts" in tables
    except Exception as e:
        print(
            "There might be no postgresql database available, consider using docker containers in project",
            file=sys.stderr,
        )
        raise e
