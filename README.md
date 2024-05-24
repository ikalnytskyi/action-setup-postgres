# action-setup-postgis

[![GitHub](https://img.shields.io/badge/github-nyurik/action--setup--postgis-8da0cb?logo=github)](https://github.com/nyurik/action-setup-postgis)
[![CI build](https://github.com/nyurik/action-setup-postgis/actions/workflows/ci.yml/badge.svg)](https://github.com/nyurik/action-setup-postgis/actions)
[![Marketplace](https://img.shields.io/badge/market-action--setup--postgis-6F42C1?logo=github)](https://github.com/marketplace/actions/setup-postgis-service-for-linux-macos-windows)

This GitHub action sets up a PostgreSQL server with PostGIS extension. The code is based on
the [ikalnytskyi/action-setup-postgres](https://github.com/ikalnytskyi/action-setup-postgres) action.

* Runs on Linux, macOS and Windows GitHub runners.
* Adds PostgreSQL [binaries](https://www.postgresql.org/docs/current/reference-client.html) (e.g. `psql`) to `PATH`.
* Uses PostgreSQL installed in [GitHub Actions Virtual Environments](https://github.com/actions/virtual-environments).
* Installs the correct version of PostGIS and runs `CREATE EXTENSION postgis` in the new database.
  * Linux version is installed from the [PostGIS apt repository](https://postgis.net/install/).
  * Windows version is installed from the [OSGeo](https://download.osgeo.org/postgis/windows/).
  * MacOS version is installed using [Homebrew package](https://formulae.brew.sh/formula/postgis).
* [Easy to check](action.yml) that IT DOES NOT contain malicious code.

See also [action-setup-nginx](https://github.com/nyurik/action-setup-nginx) to configure NGINX service.

## Usage

```yaml
steps:
  - uses: nyurik/action-setup-postgis@v2

  - run: psql "$DB_CONN_STR" -c 'SELECT 1;'
    env:
      DB_CONN_STR: ${{ steps.pg.outputs.connection-uri }}
```

> [!IMPORTANT]
>
> In order to connect to a PostgreSQL server, use either connection parameters
> from the table below ([link](#connection-parameters)), or retrieve a
> connection URI from the `connection-uri` output ([link](#advanced)).

> [!TIP]
>
> `libpq`-using applications may choose to set the `PGSERVICE=postgres`
> environment variable instead ([link](#create-a-new-user-w-database-via-cli)),
> where `postgres` is the service name extracted from the `service-name`
> output.

#### Input parameters

| Key        | Value                                                                                                | Default     |
|------------|------------------------------------------------------------------------------------------------------|-------------|
| username   | The username of the user to setup.                                                                   | `postgres`  |
| password   | The password of the user to setup.                                                                   | `postgres`  |
| database   | The database name to setup and grant permissions to created user.                                    | `postgres`  |
| port       | The server port to listen on.                                                                        | `5432`      |
| cached-dir | Where should the temporary downloads be placed. Used to download and cache PostGIS binary.           | `downloads` |

#### Outputs

| Key            | Description                                  | Example                                             |
|----------------|----------------------------------------------|-----------------------------------------------------|
| connection-uri | The connection URI to connect to PostgreSQL. | `postgresql://postgres:postgres@localhost/postgres` |
| service-name   | The service name with connection parameters. | `postgres`                                          |

#### User permissions

| Key         | Value |
|-------------|-------|
| usesuper    | true  |
| usecreatedb | true  |

#### Advanced Usage

```yaml
steps:
  - uses: nyurik/action-setup-postgis@v2
    with:
      username: ci
      password: sw0rdfish
      database: test
      port: 34837
    id: pg

  - run: psql "$CONNECTION_STR" -c 'SELECT 1;'
    env:
      CONNECTION_STR: ${{ steps.pg.outputs.connection-uri }}
```

## Recipes

#### Create a new user w/ database via CLI

```yaml
steps:
  - uses: ikalnytskyi/action-setup-postgres@v6 

  - run: |
      createuser myuser
      createdb --owner myuser mydatabase
      psql -c "ALTER USER myuser WITH PASSWORD 'mypassword'"
    env:
      # This activates connection parameters for the superuser created by
      # the action in the step above. It's mandatory to set this before using
      # createuser/psql and other libpq-using applications.
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
