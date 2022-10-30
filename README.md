# setup-postgres

This action sets up a PostgreSQL server with PostGIS extension.  The code is based on the [ikalnytskyi/action-setup-postgres](https://github.com/ikalnytskyi/action-setup-postgres) action.

* Runs on Linux, macOS and Windows runners.
* Adds PostgreSQL [binaries](https://www.postgresql.org/docs/current/reference-client.html) (e.g. `psql`) to `PATH`.
* Uses PostgreSQL installed in [GitHub Actions Virtual Environments](https://github.com/actions/virtual-environments).
* Installs the correct version of PostGIS and runs `CREATE EXTENSION postgis` in the new database.
  * Linux version is installed from the [PostGIS apt repository](https://postgis.net/install/).
  * Windows version is installed from the [OSGeo](https://download.osgeo.org/postgis/windows/).
  * MacOS version is installed using [Homebrew package](https://formulae.brew.sh/formula/postgis).
* [Easy to check][action.yml] that IT DOES NOT contain malicious code.

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
