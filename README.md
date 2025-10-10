# setup-postgres

[![CI build](https://img.shields.io/github/actions/workflow/status/ikalnytskyi/action-setup-postgres/ci.yml?style=for-the-badge&logo=github&label=Tests)](https://github.com/ikalnytskyi/action-setup-postgres/actions)
[![GitHub](https://img.shields.io/badge/github-ikalnytskyi/action--setup--postgres-3795BD?logo=github&style=for-the-badge)](https://github.com/ikalnytskyi/action-setup-postgres)
[![Marketplace](https://img.shields.io/badge/market-setup--postgres-4E31AA?logo=github&style=for-the-badge)](https://github.com/marketplace/actions/setup-postgresql-for-linux-macos-windows)

This action sets up a PostgreSQL server for the rest of the job. Here are some
key features:

* Runs on Linux, macOS and Windows action runners, including [partner][0] runners.
* PostgreSQL version can be parametrized.
* Adds PostgreSQL [client applications][1] to `PATH`.
* Supports SSL on-demand.
* Easy [to verify][2] that it DOES NOT contain malicious code.

[0]: https://github.com/actions/partner-runner-images/
[1]: https://www.postgresql.org/docs/current/reference-client.html
[2]: action.yml

#### Inputs

| Key              | Value                                                                                    | Default     |
|------------------|------------------------------------------------------------------------------------------|-------------|
| username         | The username of the user to setup.                                                       | `postgres`  |
| password         | The password of the user to setup.                                                       | `postgres`  |
| database         | The database name to setup and grant permissions to created user.                        | `postgres`  |
| port             | The server port to listen on.                                                            | `5432`      |
| postgres-version | The PostgreSQL major version to install. Supported values: "14", "15", "16", "17", "18". | `18`        |

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


## Usage

> [!IMPORTANT]
>
> In order to connect to a PostgreSQL server, either use connection parameters
> directly (see [basic] example), or, preferably, obtain a connection URI from
> the `connection-uri` output (see [recommended] example).
>
> [basic]: #basic
> [recommended]: #recommended

> [!TIP]
>
> For `libpq`-based applications, such as PostgreSQL client applications, set
> the `PGSERVICE=postgres` environment variable to automatically use the
> correct connection parameters (see [example]). The `postgres` value
> corresponds to the service name from the `service-name` output.
>
> [example]: #how-do-i-create-a-new-database-with-a-new-user

#### Basic

```yaml
steps:
  - uses: ikalnytskyi/action-setup-postgres@v8

  - run: psql postgresql://postgres:postgres@localhost:5432/postgres -c "SELECT 1"
  - run: psql service=postgres -c "SELECT 1"
  - run: psql -c "SELECT 1"
    env:
      PGSERVICE: postgres
```

#### Recommended

```yaml
steps:
  - uses: ikalnytskyi/action-setup-postgres@v8
    id: postgres

  - run: psql ${{ steps.postgres.outputs.connection-uri }} -c "SELECT 1"
  - run: psql service=${{ steps.postgres.outputs.service-name }} -c "SELECT 1"
  - run: psql -c "SELECT 1"
    env:
      PGSERVICE: ${{ steps.postgres.outputs.service-name }}
```

#### Parametrized

```yaml
steps:
  - uses: ikalnytskyi/action-setup-postgres@v8
    with:
      username: ci
      password: sw0rdfish
      database: test
      port: 34837
      postgres-version: "14"
      ssl: true
    id: postgres

  - run: psql ${{ steps.postgres.outputs.connection-uri }} -c "SELECT 1"
  - run: psql service=${{ steps.postgres.outputs.service-name }} -c "SELECT 1"
  - run: psql -c "SELECT 1"
    env:
      PGSERVICE: ${{ steps.postgres.outputs.service-name }}
```

## FAQ

#### How do I create a new database with a new user?

```yaml
steps:
  - uses: ikalnytskyi/action-setup-postgres@v8
    id: postgres

  - env:
      PGSERVICE: "${{ steps.postgres.outputs.service-name }}"
    run: |
      createuser myuser
      createdb --owner myuser mydatabase
      psql -c "ALTER USER myuser WITH PASSWORD 'mypassword'"
```

## Rationale

At the time of developing there were no GitHub Actions on the marketplace to
setup a PostgreSQL server on Linux, Windows and macOS action runners. Most
solutions suggest using Docker which is not available on macOS and Windows
runners.

## License

The scripts and documentation in this project are released under the
[MIT License](LICENSE).
