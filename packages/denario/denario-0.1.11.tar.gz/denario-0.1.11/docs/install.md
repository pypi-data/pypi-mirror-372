# Installation

## Install from PyPI

To install Denario, just do (we recommend using python3.12)

```bash
python3 -m venv Denario_env
source Denario_env/bin/activate
pip install denario
```

## Build from source

### pip

You will need python 3.12 installed.

Download Denario:

```bash
git clone https://github.com/AstroPilot-AI/Denario.git
cd Denario
```

Create and activate a virtual environment

```bash
python3 -m venv Denario_env
source Denario_env/bin/activate
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

which will create the virtual environment and install the dependencies and project. Activate the virtual environment, if needed, with

```bash
source .venv/bin/activate
```