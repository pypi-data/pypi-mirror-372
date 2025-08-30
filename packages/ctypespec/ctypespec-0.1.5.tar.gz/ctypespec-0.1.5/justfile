
@default: venv update-version build test

@venv:
    uv sync --extra dev

@update-version:
    uv run ctypespec/_version.py

@build:
    uv build --no-sources

@test:
    uv run python tests/test_ctyp.py

@publish: default
    uv publish --token "$(pass show pypi/token)"
