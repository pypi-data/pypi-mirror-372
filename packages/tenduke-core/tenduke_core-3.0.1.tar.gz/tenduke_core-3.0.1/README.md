# 10Duke Python core library

This repository contains the shared code between the 10Duke Enterprise and 10Duke Scale SDKs.

## Contents

- [Why?](#why)
- [Installation](#installation)
- [Development](#development)
- [Getting involved](#getting-involved)
- [Resources](#resources)
- [License](#license)

## Why

The 10Duke Enterprise and 10Duke Scale SDK client libraries both need similar
functionality in areas such as authentication and configuration

In order to reduce complexity in those libraries, promote similar developer experience
using those libraries, and reduce effort developing and maintaining those libraries,
this project established a shared, core library that provides that functionality to
both client libraries.

## Installation

### Using pip

```bash
pip install tenduke_core
```

### Using poetry

```bash
poetry add tenduke_core
```

## Development

To get started with working on the code, clone this repository.

```bash
git clone git@gitlab.com:10Duke/core/python-core.git
```

Then you need to install the tools and dependencies.

Install poetry:

```bash
curl -sSL https://install.python-poetry.org | python3
```

Start the virtual environment for the project:

```bash
poetry shell
```

Resolve dependencies:

```bash
poetry lock
```

Install dependencies:

```bash
poetry install
```

The tests can be run using

```bash
pytest .
```

For linux or macOS, a `Makefile` is provided to automate these, and other, development tasks.

### Code formatting / linting

This project is using:

- [ruff](https://github.com/astral-sh/ruff) for linting and code formatting
- [markdownlint](https://github.com/markdownlint/markdownlint) for linting markdown.

### Bumping version and releasing

The project is using [Semantic Versioning](https://semver.org/).

The version shall be set using `poetry version`. This will update the version number in
`pyproject.toml`.

That change shall be committed in a new revision.

That revision shall be tagged (for example `git tag v1.1.1`).

The new tag shall be pushed (`git push --tags`).

That will trigger the creation of a new package and the publishing of that package to the GitLab
package repository.

[Publishing to PyPi](./docs/publishing.md) requires additional steps.

## Getting involved

We welcome contributions! [Contributing](./CONTRIBUTING) explains what kind of contributions we
welcome.

## Resources

- [10Duke Enterprise documentation](https://docs.enterprise.10duke.com/index.html)
- [10Duke Scale documentation](https://docs.scale.10duke.com/index.html)
- [10Duke.com](https://www.10duke.com/) - Find more information about 10Duke products and services

## License

10Duke Python core library is licensed under the [MIT](./LICENSE) license.
