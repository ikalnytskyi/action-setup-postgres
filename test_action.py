import typing as t
import os

import psycopg
import pytest


@pytest.fixture(scope="function")
def connection_factory() -> t.Callable[[str], psycopg.Connection]:
    def factory(connection_uri: str) -> psycopg.Connection:
        return psycopg.connect(connection_uri)
    return factory


@pytest.fixture(scope="function")
def connection(connection_factory) -> psycopg.Connection:
    return connection_factory(os.getenv("CONNECTION_URI"))


def test_connection_uri():
    """Test that CONNECTION_URI matches EXPECTED_CONNECTION_URI."""

    connection_uri = os.getenv("CONNECTION_URI")
    expected_connection_uri = os.getenv("EXPECTED_CONNECTION_URI")
    assert connection_uri == expected_connection_uri


def test_user_permissions(connection: psycopg.Connection):
    """Test that a user can create databases but is not a superuser."""

    with connection:
        record = connection \
            .execute("SELECT usecreatedb, usesuper FROM pg_user WHERE usename = CURRENT_USER") \
            .fetchone()
        assert record

        usecreatedb, usesuper = record
        assert usecreatedb
        assert not usesuper


def test_user_create_insert_select(connection: psycopg.Connection):
    """Test that a user has CRUD permissions in a database."""

    table_name = "test_setup_postgres"

    with connection, connection.transaction(force_rollback=True):
        records = connection \
            .execute(f"CREATE TABLE {table_name}(eggs INTEGER, rice VARCHAR)") \
            .execute(f"INSERT INTO {table_name}(eggs, rice) VALUES (1, '42')") \
            .execute(f"SELECT * FROM {table_name}") \
            .fetchall()
        assert records == [(1, "42")]


def test_user_create_drop_database(connection: psycopg.Connection):
    """Test that a user has no permissions to create databases."""

    # CREATE/DROP DATABASE statements don't work within transactions, and with
    # autocommit disabled transactions are created by psycopg automatically.
    connection.autocommit = True

    database_name = "foobar42"
    connection.execute(f"CREATE DATABASE {database_name}")
    connection.execute(f"DROP DATABASE {database_name}")
