# Developing CLI

## Tests

Tests are run using PyTest. By default, our tests use a [Docker Compose](https://docs.docker.com/compose/) environment (located in `./tests/integration/docker-compose-panoramax.yml`) to set-up a temporary Panoramax API to run onto. If you have Docker Compose enabled and running on your machine, you can simply run this command to launch tests:

```bash
pytest
```

If you don't have Docker Compose, or want to use an existing Panoramax test instance (to speed up tests), you can pass the `--external-panoramax-url` option to pytest:

```bash
pytest --external-panoramax-url=http://api.panoramax.localtest.me:5123
```

### Using with an unsecure Panoramax API

The CLI parameter `--disable-cert-check` is available to use with an unsecure panoramax API (or when behind proxies messing with ssl). 

There are no automated test for this, but you can run a panoramax with `flask run --cert=adhoc` to manually test this. 

## Documentation

High-level documentation is handled by [Typer](https://typer.tiangolo.com/). You can update the generated `docs/COMMANDS.md` file using this command:

```bash
make docs
```

[Mkdocs](https://www.mkdocs.org/) is also used to serve docs in a user-friendly manner. Documentation has to be made available in `docs/` folder. You can test the rendering by running:

```bash
pip install -e .[docs]
mkdocs serve
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Note that before opening a pull requests, you may want to check formatting and tests of your changes:

```bash
make ci
```

You can also install git [pre-commit](https://pre-commit.com/) hooks to format code on commit with:

```bash
pip install -e .[dev]
pre-commit install
```

## Make a release

```bash
git checkout develop
git pull

vim CHANGELOG.md				# Edit version + links at bottom
vim panoramax_cli/__init__.py	# Edit version
make docs ci

git add *
git commit -m "Release x.x.x"
git tag -a x.x.x -m "Release x.x.x"
git push origin develop
git checkout main
git merge develop
git push origin main --tags
```
