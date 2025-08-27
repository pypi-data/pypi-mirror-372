# leap-bundle

Command line tool to create model bundles for Liquid Edge AI Platform ([LEAP](https://leap.liquid.ai)).

This tool enables everyone to create, manage, and download AI model bundles for deployment on edge devices. Upload your model directories, track bundle creation progress, and download optimized bundles ready for mobile integration.

## Installation

```bash
pip install leap-bundle
```

## Commands

| Command | Description |
| --- | --- |
| `leap-bundle login <api-token>` | Authenticate with LEAP using API token |
| `leap-bundle whoami` | Show current authenticated user |
| `leap-bundle logout` | Logout from LEAP |
| `leap-bundle config` | Show current configuration |
| `leap-bundle validate <input-path>` | Validate directory for bundle creation |
| `leap-bundle create` | Submit new bundle request |
| `leap-bundle list` | List all bundle requests |
| `leap-bundle list <request-id>` | Show details of a specific request |
| `leap-bundle cancel <request-id>` | Cancel a bundle request |
| `leap-bundle download <request-id>` | Download the bundle file for a specific request |

## Development

This package uses `uv` for dependency management.

### Setup

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev
```

### Development Commands

| `uv` command | `npm` command | Description |
| --- | --- | --- |
| `uv run ruff check .` | `npm run lint` | Run code linting |
| `uv run ruff format .` | `npm run format` | Format code using ruff |
| `uv run mypy .` | `npm run typecheck` | Run type checking with mypy |
| `uv run pytest` | `npm run test` | Run tests using pytest |
| | `npm run check` | Run all above checks |

### Local Development

```bash
# Install the package in virtual environment
uv pip install -e .

# Run the CLI
uv run leap-bundle --help
# Or activate the virtual environment and run directly
source .venv/bin/activate
leap-bundle --help
```

## License

[LFM Open License v1.0](https://www.liquid.ai/lfm-license)
