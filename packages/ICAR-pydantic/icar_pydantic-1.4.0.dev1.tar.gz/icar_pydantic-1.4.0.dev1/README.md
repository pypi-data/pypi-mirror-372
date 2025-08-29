# ICAR-pydantic
Pydantic package that provides ICAR Animal Data Exchange data classes for Python

See [ICAR documentation](https://github.com/adewg/ICAR/wiki) for the details of the specifications.

# Installation

```bash
pip install ICAR-pydantic
```

# Development

## Installation

Requires:
- python
- nodejs

```bash
pip install -r requirements.txt
git clone -b Develop git@github.com:adewg/ICAR.git ICAR-schema
pre-commit install
```

## Bundle

```bash
./scripts/schema_bundle.sh
./scripts/generate_models.sh
./scripts/generate_modules.sh
```

## Run Tests

```bash
python -m unittest discover tests -v
```
