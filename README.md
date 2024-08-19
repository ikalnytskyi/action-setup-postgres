# setup-postgres

[![CI build](https://github.com/ikalnytskyi/action-setup-postgres/actions/workflows/ci.yml/badge.svg)](https://github.com/ikalnytskyi/action-setup-postgres/actions)
[![GitHub](https://img.shields.io/badge/github-ikalnytskyi/action--setup--postgres-3795BD?logo=github)](https://github.com/ikalnytskyi/action-setup-postgres)
[![Marketplace](https://img.shields.io/badge/market-setup--postgres-4E31AA?logo=github)](https://github.com/marketplace/actions/setup-postgresql-for-linux-macos-windows)

This action sets up a PostgreSQL server for the rest of the job. Here are some
key features:

* Runs on Linux, macOS and Windows action runners.
* PostgreSQL version can be parametrized.
* Adds PostgreSQL [client applications][1] to `PATH`.
* Supports SSL on-demand.
* Easy [to verify][2] that it DOES NOT contain malicious code.

[1]: https://www.postgresql.org/docs/current/reference-client.html
[2]: action.yml

## Usage

> [!IMPORTANT]
>
> In order to connect to a PostgreSQL server, either use connection parameters
> directly (refer to the table below for default values), or, preferably,
> obtain a connection URI from the `connection-uri` output ([example]).
>
> [example]: #advanced

> [!TIP]
>
> For `libpq`-based applications, such as PostgreSQL client applications, set
> the `PGSERVICE=postgres` environment variable to automatically use the
> correct connection parameters ([example]). The `postgres` value corresponds
> to the service name from the `service-name` output.
>
> [example]: #create-a-new-user-w-database-via-cli

#### Action Parameters

| Key              | Value                                                                              | Default     |
|------------------|------------------------------------------------------------------------------------|-------------|
| username         | The username of the user to setup.                                                 | `postgres`  |
| password         | The password of the user to setup.                                                 | `postgres`  |
| database         | The database name to setup and grant permissions to created user.                  | `postgres`  |
| port             | The server port to listen on.                                                      | `5432`      |
| postgres-version | The PostgreSQL major version to install. Supported values: "14", "15", "16".       | `16`        |

#### Outputs

| Key              | Description                                      | Example                                             |
|------------------|--------------------------------------------------|-----------------------------------------------------|
| connection-uri   | The connection URI to connect to PostgreSQL.     | `postgresql://postgres:postgres@localhost/postgres` |
| service-name     | The service name with connection parameters.     | `postgres`                                          |
| certificate-path | The path to the server certificate if SSL is on. | `/home/runner/work/_temp/pgdata/server.crt`         |

#### User permissions

| Key         | Value |
|-------------|-------|
| usesuper    | true  |
| usecreatedb | true  |

#### Basic

```yaml
steps:
  - uses: ikalnytskyi/action-setup-postgres@v6
```

#### Advanced

```yaml
steps:
  - uses: ikalnytskyi/action-setup-postgres@v6
    with:
      username: ci
      password: sw0rdfish
      database: test
      port: 34837
      postgres-version: "14"
      ssl: true
    id: postgres

  - run: pytest -vv tests/
    env:
      CONNECTION_STR: postgresql://ci:sw0rdfish@localhost:34837/test

  - run: pytest -vv tests/
    env:
      CONNECTION_STR: ${{ steps.postgres.outputs.connection-uri }}

  - run: pytest -vv tests/
    env:
      CONNECTION_STR: service=${{ steps.postgres.outputs.service-name }}
```

## Recipes

#### Create a new user w/ database via CLI

```yaml
steps:
  - uses: ikalnytskyi/action-setup-postgres@v6
    id: postgres

  - run: |
      createuser myuser
      createdb --owner myuser mydatabase
      psql -c "ALTER USER myuser WITH PASSWORD 'mypassword'"
    env:
      # This activates connection parameters for the superuser created by
      # the action in the step above. It's mandatory to set this before using
      # createuser/psql and other libpq-based applications. Otherwise, one
      # would need to supply connection parameters via command line arguments.
      #
      # The service name is the same as the username (i.e. 'postgres') but
      # it's recommended to use action's output to get the name in order to
      # be forward compatible.
      PGSERVICE: ${{ steps.postgres.outputs.service-name }}
    shell: bash
```

#### Create a new user w/ database via psycopg

```yaml
steps:
  - uses: ikalnytskyi/action-setup-postgres@v6
```

```python
import psycopg

# 'postgres' is the username here, but it's recommended to use the
# action's 'service-name' output parameter here.
connection = psycopg.connect("service=postgres")

# CREATE/DROP USER statements don't work within transactions, and with
# autocommit disabled transactions are created by psycopg automatically.
connection.autocommit = True
connection.execute(f"CREATE USER myuser WITH PASSWORD 'mypassword'")
connection.execute(f"CREATE DATABASE mydatabase WITH OWNER 'myuser'")
```

## Rationale

At the time of developing there were no GitHub Actions on the marketplace to
setup a PostgreSQL server on Linux, Windows and macOS action runners. Most
solutions suggest using Docker which is not available on macOS and Windows
runners.

## License

The scripts and documentation in this project are released under the
[MIT License](LICENSE).
