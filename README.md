# setup-postgres

This action sets up a PostgreSQL server for the rest of the job. Here are some
key features:

* Runs on Linux, macOS and Windows action runners.
* Adds PostgreSQL [client applications][1] to `PATH`.
* Uses PostgreSQL binaries baked into [GitHub Actions Runner Images][2].
* Easy [to prove][3] that it DOES NOT contain malicious code.

[1]: https://www.postgresql.org/docs/current/reference-client.html
[2]: https://github.com/actions/runner-images
[3]: action.yml

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

#### User permissions

| Key         | Value |
|-------------|-------|
| usesuper    | true  |
| usecreatedb | true  |

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

## Rationale

At the time of developing there were no GitHub Actions on the marketplace to
setup a PostgreSQL server on Linux, Windows and macOS action runners. Most
solutions suggest using Docker which is not available on macOS and Windows
runners.

## License

The scripts and documentation in this project are released under the
[MIT License](LICENSE).
