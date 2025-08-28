# scsketch

## Installation

```sh
pip install scsketch
```

or with [uv](https://github.com/astral-sh/uv):

```sh
uv add scsketch
```

## Development

We recommend using [uv](https://github.com/astral-sh/uv) for development.
It will automatically manage virtual environments and dependencies for you.

```sh
uv run jupyter lab example.ipynb
```

Alternatively, create and manage your own virtual environment:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
jupyter lab example.ipynb
```

Open `example.ipynb` in JupyterLab, VS Code, or your favorite editor
to start developing. Changes made in `src/scsketch/static/` will be reflected
in the notebook.
