# Contributing

Thank you for helping improve Japanese open-geospatial game QA.

## Good First Contributions

- add a synthetic broken manifest fixture
- document a common map failure class
- add a validator that works on the public manifest schema
- improve English or Japanese documentation
- add adapters for open formats without bundling raw source data

## Data Rules

Do not commit raw GIS source data, map tiles, DEM files, database dumps, or
screenshots that may have unclear redistribution rights. Prefer small synthetic
fixtures that demonstrate the failure shape without copying real source data.

## Development

```bash
python -m unittest discover -s tests -v
PYTHONPATH=src python -m jp_geo_game_qa validate examples/sample_manifest.json
PYTHONPATH=src python -m jp_geo_game_qa validate examples/broken_manifest.json
```

The sample manifest should pass. The broken manifest should fail.

## Pull Request Checklist

- tests pass
- no private paths or secrets are included
- new validators include a passing and failing fixture
- documentation explains why the gate matters for real-time map rendering
