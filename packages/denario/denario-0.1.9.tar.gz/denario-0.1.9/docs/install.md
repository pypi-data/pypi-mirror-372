# Installation

## Install from PyPI

To install Denario, just run

```bash
pip install denario
```

## Build from source

### pip

You will need python 3.12 installed.

Create a virtual environment

```bash
python3 -m venv .venv
```

Activate the virtual environment

```bash
source .venv/bin/activate
```

And install the project
```bash
pip install -e .
```

### uv

You can also install the project using [uv](https://docs.astral.sh/uv/), just running:

```bash
uv sync
```

which will create the virtual environment and install the dependencies and project. Activate the virtual environment if needed with

```bash
source .venv/bin/activate
```