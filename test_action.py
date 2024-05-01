import locale
import os
import pathlib
import subprocess
import typing as t

import psycopg
import furl
import pytest


ConnectionFactory = t.Callable[[str], psycopg.Connection]


@pytest.fixture(scope="function")
def is_windows() -> bool:
    """Returns True if running on Windows."""

    return os.name == "nt"


@pytest.fixture(scope="function")
def is_windows_server_2019(is_windows: bool) -> bool:
    """Returns True if running on Windows Server 2019."""

    if not is_windows:
        return False

    windows_caption = subprocess.check_output(["wmic", "os", "get", "Caption"], text=True)
    return "Windows Server 2019" in windows_caption


@pytest.fixture(scope="function")
def connection_uri() -> str:
    """Read and return connection URI from environment."""

    connection_uri = os.getenv("CONNECTION_URI")
    if connection_uri is None:
        pytest.fail("CONNECTION_URI: environment variable is not set")
    return connection_uri


@pytest.fixture(scope="function")
def service_name() -> str:
    """Read and return connection URI from environment."""

    service_name = os.getenv("SERVICE_NAME")
    if service_name is None:
        pytest.fail("SERVICE_NAME: environment variable is not set")
    return service_name


@pytest.fixture(scope="function")
def connection_factory() -> ConnectionFactory:
    """Return 'psycopg.Connection' factory."""

    def factory(connection_uri: str) -> psycopg.Connection:
        return psycopg.connect(connection_uri)
    return factory


@pytest.fixture(scope="function", params=["uri", "kv-string"])
def connection(
    request: pytest.FixtureRequest,
    connection_factory: ConnectionFactory,
    connection_uri: str,
    service_name: str,
) -> psycopg.Connection:
    """Return 'psycopg.Connection' for connection URI set in environment."""

    if request.param == "uri":
        return connection_factory(connection_uri)
    elif request.param == "kv-string":
        return connection_factory(f"service={service_name}")
    raise RuntimeError("f{request.param}: unknown value")


def test_connection_uri(connection_uri: str):
    """Test that CONNECTION_URI matches EXPECTED_CONNECTION_URI."""

    assert connection_uri == os.getenv("EXPECTED_CONNECTION_URI")


def test_service_name(service_name: str):
    """Test that SERVICE_NAME matches EXPECTED_SERVICE_NAME."""

    assert service_name == os.getenv("EXPECTED_SERVICE_NAME")


def test_server_encoding(connection: psycopg.Connection):
    """Test that PostgreSQL's encoding matches the one we passed to initdb."""

    assert connection.execute("SHOW SERVER_ENCODING").fetchone()[0] == "UTF8"


def test_locale(connection: psycopg.Connection, is_windows_server_2019: bool):
    """Test that PostgreSQL's locale matches the one we paased to initdb."""

    locale_exp = "en_US.UTF-8"

    if is_windows_server_2019:
        locale_exp = "en-US"

    lc_collate = connection.execute("SHOW LC_COLLATE").fetchone()[0]
    lc_ctype = connection.execute("SHOW LC_CTYPE").fetchone()[0]

    assert locale.normalize(lc_collate) == locale_exp
    assert locale.normalize(lc_ctype) == locale_exp


def test_environment_variables(is_windows: bool):
    """Test that only expected 'PG*' variables are set."""

    pg_environ = {k: v for k, v in os.environ.items() if k.startswith("PG")}

    # In case of Windows, there might be a mix of forward and backward slashes
    # as separators. So let's compare paths semantically instead.
    pg_servicefile = pathlib.Path(pg_environ.pop("PGSERVICEFILE", ""))
    pg_servicefile_exp = pathlib.Path(os.environ["RUNNER_TEMP"], "pgdata", "pg_service.conf")
    assert pg_servicefile.resolve() == pg_servicefile_exp.resolve()
    
    if is_windows:
        pg_environ_exp = {
            "PGBIN": "",
            "PGDATA": "",
            "PGPASSWORD": "",
            "PGROOT": "",
            "PGUSER": "",
        }
    else:
        pg_environ_exp = {}
    assert pg_environ == pg_environ_exp


def test_user_permissions(connection: psycopg.Connection):
    """Test that a user has super/createdb permissions."""

    with connection:
        record = connection \
            .execute("SELECT usecreatedb, usesuper FROM pg_user WHERE usename = CURRENT_USER") \
            .fetchone()
        assert record

        usecreatedb, usesuper = record
        assert usecreatedb
        assert usesuper


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


def test_user_create_insert_non_ascii(connection: psycopg.Connection):
    """Test that non-ASCII characters can be stored and fetched."""

    table_name = "test_setup_postgres"

    with connection, connection.transaction(force_rollback=True):
        records = connection \
            .execute(f"CREATE TABLE {table_name}(eggs INTEGER, rice VARCHAR)") \
            .execute(f"INSERT INTO {table_name}(eggs, rice) VALUES (1, 'Україна')") \
            .execute(f"INSERT INTO {table_name}(eggs, rice) VALUES (2, 'ウクライナ')") \
            .execute(f"SELECT * FROM {table_name}") \
            .fetchall()
        assert records == [(1, "Україна"), (2, "ウクライナ")]


def test_user_create_drop_database(connection: psycopg.Connection):
    """Test that a user has permissions to create databases."""

    # CREATE/DROP DATABASE statements don't work within transactions, and with
    # autocommit disabled transactions are created by psycopg automatically.
    connection.autocommit = True

    database = "databas3"
    connection.execute(f"CREATE DATABASE {database}")
    connection.execute(f"DROP DATABASE {database}")


def test_user_create_drop_user(
    connection: psycopg.Connection,
    connection_factory: ConnectionFactory,
    connection_uri: str
):
    """Test that a user has permissions to create users."""

    # CREATE/DROP USER statements don't work within transactions, and with
    # autocommit disabled transactions are created by psycopg automatically.
    connection.autocommit = True

    username = "us3rname"
    password = "passw0rd"
    database = "databas3"

    connection.execute(f"CREATE USER {username} WITH PASSWORD '{password}'")
    connection.execute(f"CREATE DATABASE {database} WITH OWNER '{username}'")

    try:
        # Smoke test that created user can successfully log-in and execute
        # queries for its own database.
        connection_uri = furl.furl(
            connection_uri, username=username, password=password, path=database).url
        test_user_create_insert_select(connection_factory(connection_uri))

    finally:
        connection.execute(f"DROP DATABASE {database}")
        connection.execute(f"DROP USER {username}")


def test_client_applications(
    connection_factory: ConnectionFactory,
    service_name: str,
    connection_uri: str,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that PostgreSQL client applications can be used."""

    # Request connection parameters from the connection service file prepared
    # by our action.
    monkeypatch.setenv("PGSERVICE", service_name)

    username = "us3rname"
    password = "passw0rd"
    database = "databas3"

    subprocess.check_call(["createuser", username])
    subprocess.check_call(["createdb", "--owner", username, database])
    subprocess.check_call(["psql", "-c", f"ALTER USER {username} WITH PASSWORD '{password}'"])

    try:
        # Smoke test that created user can successfully log-in and execute
        # queries for its own database.
        connection_uri = furl.furl(
            connection_uri, username=username, password=password, path=database).url
        test_user_create_insert_select(connection_factory(connection_uri))

    finally:
        subprocess.check_call(["dropdb", database])
        subprocess.check_call(["dropuser", username])


def test_libpq_applications(service_name: str, monkeypatch: pytest.MonkeyPatch):
    """Test that libpq-using applications can be used."""

    # Request connection parameters from the connection service file prepared
    # by our action.
    monkeypatch.setenv("PGSERVICE", service_name)

    with psycopg.connect() as connection:
        assert connection \
            .execute("SELECT usename FROM pg_user WHERE usename = CURRENT_USER") \
            .fetchone()


def test_auth_wrong_username(connection_factory: ConnectionFactory, connection_uri: str):
    """Test that wrong username is rejected!"""

    connection_furl = furl.furl(connection_uri, username="wrong")

    with pytest.raises(psycopg.OperationalError) as excinfo:
        connection_factory(connection_furl.url)

    assert 'password authentication failed for user "wrong"' in str(excinfo.value)


def test_auth_wrong_password(connection_factory: ConnectionFactory, connection_uri: str):
    """Test that wrong password is rejected!"""

    connection_furl = furl.furl(connection_uri, password="wrong")
    username = connection_furl.username

    with pytest.raises(psycopg.OperationalError) as excinfo:
        connection_factory(connection_furl.url)

    assert f'password authentication failed for user "{username}"' in str(excinfo.value)
