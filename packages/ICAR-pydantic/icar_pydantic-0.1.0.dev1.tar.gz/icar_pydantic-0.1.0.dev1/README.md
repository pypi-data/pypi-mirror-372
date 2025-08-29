# ICAR-pydantic
Pydantic package that provides ICAR Animal Data Exchange data classes for Python


# Installation

Requires:
- python
- nodejs

```bash
pip install -r requirements.txt
git clone -b Develop git@github.com:adewg/ICAR.git ICAR-schema
pre-commit install
```

# Bundle

```bash
./scripts/schema_bundle.sh
./scripts/generate_models.sh
./scripts/generate_modules.sh
```
