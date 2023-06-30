# setup-postgres

This action sets up a PostgreSQL server for the rest of the job. Here are some
key features:

* Runs on Linux, macOS and Windows action runners.
* Adds PostgreSQL [client applications][1] to `PATH`.
* Supports PostgreSQL version parametrization.
* Easy [to prove][2] that it DOES NOT contain malicious code.

By default PostgreSQL 15 is used.

[1]: https://www.postgresql.org/docs/current/reference-client.html
[2]: action.yml

## Usage

#### Connection parameters

| Key      | Value                                               |
|----------|-----------------------------------------------------|
| URI      | `postgresql://postgres:postgres@localhost/postgres` |
| Host     | `localhost`                                         |
| Port     | `5432`                                              |
| Username | `postgres`                                          |
| Password | `postgres`                                          |
| Database | `postgres`                                          |
| Service  | `postgres`                                          |

#### User permissions

| Key         | Value |
|-------------|-------|
| usesuper    | true  |
| usecreatedb | true  |

#### Basic

```yaml
steps:
  - uses: ikalnytskyi/action-setup-postgres@v5
```

#### Advanced

```yaml
steps:
  - uses: ikalnytskyi/action-setup-postgres@v5
    with:
      username: ci
      password: sw0rdfish
      database: test
      port: 34837
      postgres-version: "13"
    id: postgres

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
  - uses: ikalnytskyi/action-setup-postgres@v5

  - run: |
      createuser myuser
      createdb --owner myuser mydatabase
      psql -c "ALTER USER myuser WITH PASSWORD 'mypassword'"

    env:
      # This activates connection parameters for the superuser created by
      # the action in the step above. It's mandatory to set this before using
      # createuser/psql/etc tools.
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
  - uses: ikalnytskyi/action-setup-postgres@v5
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
