# setup-postgres

This action sets up a PostgreSQL server for the rest of the job. Here are some
key features:

* Runs on Linux, macOS and Windows runners.
* Adds PostgreSQL [binaries][1] (e.g. `psql`) to `PATH`.
* Uses PostgreSQL installed in [GitHub Actions Virtual Environments][2].
* [Easy to check][3] that IT DOES NOT contain malicious code.

[1]: https://www.postgresql.org/docs/current/reference-client.html
[2]: https://github.com/actions/virtual-environments
[3]: action.yml

## Usage

| Key      | Value                                               |
|----------|-----------------------------------------------------|
| URI      | `postgresql://postgres:postgres@localhost/postgres` |
| Host     | `localhost`                                         |
| Port     | `5432`                                              |
| Username | `postgres`                                          |
| Password | `postgres`                                          |
| Database | `postgres`                                          |

#### Basic

```yaml
steps:
  - uses: ikalnytskyi/action-setup-postgres@v3
```

#### Advanced

```yaml
steps:
  - uses: ikalnytskyi/action-setup-postgres@v3
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
