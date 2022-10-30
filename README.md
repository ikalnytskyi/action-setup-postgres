# setup-postgres

This action sets up a PostgreSQL server with PostGIS extension.  The code is based on the [ikalnytskyi/action-setup-postgres](https://github.com/ikalnytskyi/action-setup-postgres) action.

* Runs on Linux, macOS and Windows runners.
* Adds PostgreSQL [binaries][1] (e.g. `psql`) to `PATH`.
* Uses PostgreSQL installed in [GitHub Actions Virtual Environments][2].
* Installs the correct version of PostGIS and runs `CREATE EXTENSION postgis` in the new database.
* [Easy to check][3] that IT DOES NOT contain malicious code.

[1]: https://www.postgresql.org/docs/current/reference-client.html
[2]: https://github.com/actions/virtual-environments
[3]: action.yml

## Usage

| Key        | Value                                               |
|------------|-----------------------------------------------------|
| URI        | `postgresql://postgres:postgres@localhost/postgres` |
| Host       | `localhost`                                         |
| Port       | `5432`                                              |
| Username   | `postgres`                                          |
| Password   | `postgres`                                          |
| Database   | `postgres`                                          |
| Rights     | `--createdb`                                        |
| Cached-dir | `downloads`                                         |

#### Basic

```yaml
steps:
  - uses: nyurik/action-setup-postgis@main
```

#### Advanced

```yaml
steps:
  - uses: nyurik/action-setup-postgis@main
    with:
      username: ci
      password: sw0rdfish
      database: test
      port: 34837
    id: postgres

  - run: pytest -vv tests/
    env:
      DATABASE_URI: ${{ steps.postgres.outputs.connection-uri }}
```

## License

The scripts and documentation in this project are released under the
[MIT License](LICENSE).
