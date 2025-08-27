# Git Tag Deploy

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![PyPI version](https://img.shields.io/pypi/v/git-tag-deploy.svg)](https://pypi.org/project/git-tag-deploy/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Pre-commit Hooks](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A lightweight **developer tool** to deploy multiple Git-tagged versions of a FastAPI application simultaneously, each on its own dynamically assigned port. Includes a simple FastAPI endpoint to view all active deployments.

---

## Features

- Deploy any number of Git tags from your repository.
- Automatically assigns free ports in the range `8001-9000`.
- Each deployment runs in its own daemon process — terminates automatically when the main starter process exits.
- Provides a `/deployments` FastAPI endpoint to check which versions are running and on which ports.
- Simple CLI for one-command deployment.

---

## Installation

Install via pip using the pypi package:

```bash
pip install git-tag-deploy
````

This installs the package and registers the `git-tag-deploy` CLI.

---

## Usage

1. Ensure you have a `deployment.yaml` file in your repository, listing the apps and Git tags to deploy.
2. Run the CLI:

```bash
git-tag-deploy
```

The CLI will:

* Deploy all Git-tagged apps to dynamically assigned ports.
* Print the deployed apps and ports in the console.
* Start a FastAPI server on port `5000` to expose `/deployments`.

Example console output:

```
Starting deployments...

Deployments started:
 - service1: tag=v1.0.0, port=8001
 - service2: tag=v1.1.0, port=8002

FastAPI status server running at http://127.0.0.1:5000/deployments
```

Visit [http://127.0.0.1:5000/deployments](http://127.0.0.1:5000/deployments) to see JSON information of all active deployments.

---

## Project Structure

```
tenbatsu24-git-tag-deployment/
├── pyproject.toml        # Project configuration and dependencies
└── git_tag_deploy/       # Main package
    ├── __init__.py
    ├── cli.py            # CLI entry point
    ├── deployer.py       # Deployment logic and process management
    └── server.py         # FastAPI endpoint for deployment info
```

---

## Dependencies

* Python 3.10+
* [PyYAML](https://pyyaml.org/) – for reading deployment configuration
* [FastAPI](https://fastapi.tiangolo.com/) – for the status server
* [uvicorn](https://www.uvicorn.org/) – ASGI server for deployed apps

---

## How It Works

* Reads the `deployment.yaml` file to determine which Git tags to deploy.
* Clones the repository for each tag into a temporary directory.
* Starts each deployment in a **daemonized process**, running uvicorn on a free port.
* Tracks deployments in memory (`tag` + `port`) for the FastAPI `/deployments` endpoint.

---

## Future Improvements
* [ ] Implement logging for deployment processes.
* [ ] Add health checks for deployed applications.
* [ ] Clean up temporary directories after deployments.
* [ ] Custom deployment scripts/hooks. (not just uvicorn app.main:app)
* [ ] Docker support for containerized deployments of git tags.

## License

This project is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for details.
