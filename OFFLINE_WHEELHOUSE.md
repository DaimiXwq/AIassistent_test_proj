# Offline wheelhouse: include transitive dependencies

Short answer: **yes, each package in `requirements.txt` has transitive dependencies**.

You do **not** need to manually list all transitive dependencies in `requirements.txt` if you build the wheelhouse correctly.

## Recommended flow (online machine)

1. Create a clean virtual environment.
2. Upgrade packaging tools.
3. Download wheels for `requirements.txt` **with dependencies**.
4. Export an installed lock (`pip freeze`) for reproducibility.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel

# Downloads direct + transitive dependencies into wheelhouse/
pip download -r requirements.txt -d wheelhouse

# Optional but recommended: validate installation only from local wheelhouse
pip install --no-index --find-links=wheelhouse -r requirements.txt

# Capture exact installed set (includes transitives)
pip freeze > requirements.lock.txt
```

## Install on offline machine

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install --no-index --find-links=wheelhouse -r requirements.txt
```

## Important notes

- If offline target OS/Python differs from the online builder, prepare wheelhouse for that exact target.
- `torch` and `tokenizers` wheels are platform-specific; build/download for the same Python version and architecture as offline host.
- For `sentence-transformers`, also pre-download model files (e.g. `all-MiniLM-L6-v2`) to a local path.
