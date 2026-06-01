# Publish Checklist

## Repository Setup

- Create public GitHub repository: `japan-geo-game-qa-toolkit`
- Copy only this candidate folder's contents into the new repository root.
- Do not copy parent project history unless the private project has already been scrubbed.
- Confirm `LICENSE`, `README.md`, `pyproject.toml`, `src/`, `examples/`, `tests/`, and `docs/` are present.

## Verification

```bash
python -m unittest discover -s tests -v
PYTHONPATH=src python -m jp_geo_game_qa validate examples/sample_manifest.json
PYTHONPATH=src python -m jp_geo_game_qa validate examples/broken_manifest.json
```

Expected:

- sample manifest returns `PASS`
- broken manifest returns `FAIL`

## Secret / Path Scan

```bash
rg -n "Google Drive|G:|D:|KS100|StreamingAssets|GeoAuthoritative|LargeData|OpenAI API key|sk-" .
```

Expected:

- no hits except this checklist line

## Application Prep

- Fill in actual GitHub repository URL.
- Confirm you are the primary maintainer.
- Submit the application from the OpenAI Codex for Open Source page.
