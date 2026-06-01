# Japan Geo Game QA Toolkit

Small, data-source-neutral QA checks for games and simulations that turn Japanese
open geospatial data into runtime map packages.

This repository is designed as an open source spin-out candidate from a private
game production pipeline. It intentionally does not include proprietary game
code, raw GIS source data, local machine paths, cached map tiles, or licensed
third-party datasets.

## Why This Exists

Japanese open geospatial data is excellent, but shipping it inside a real-time
Unity or game runtime is still hard. Developers often need to resolve issues
before runtime:

- expected map chunks are missing one or more LOD packages
- broad rivers are accidentally rendered as many internal centerlines
- roads cut water surfaces instead of becoming bridges, culverts, or tunnels
- underground rail or subway spans appear as surface rail
- map QA claims pass without required visual checkpoints

This toolkit provides a small public validation format and CLI so teams can gate
those issues before a build is treated as playable.

## Current Scope

The first public candidate validates a JSON manifest, not a project-specific DB.
The manifest can be produced by any pipeline that uses GSI, OSM, PLATEAU, KSJ,
or another data source.

Included gates:

- required LOD coverage per chunk
- broad-waterbody internal centerline rejection
- road-water crossing resolution
- road marking coverage for visible roads
- underground rail and subway surface-leak rejection
- required visual checkpoint evidence

## Install

Use any Python 3.10+ environment. No third-party packages are required.

```bash
python -m pip install -e .
```

You can also run the CLI directly from the source tree:

```bash
PYTHONPATH=src python -m jp_geo_game_qa validate examples/sample_manifest.json
```

On PowerShell:

```powershell
$env:PYTHONPATH="src"; python -m jp_geo_game_qa validate examples/sample_manifest.json
```

## Usage

Validate the good sample:

```bash
jggqa validate examples/sample_manifest.json
```

Validate and print JSON output:

```bash
jggqa validate examples/sample_manifest.json --json
```

Confirm that the broken sample fails:

```bash
jggqa validate examples/broken_manifest.json
```

## Manifest Shape

```json
{
  "schema": "jp-geo-game-qa/manifest-v1",
  "chunks": [
    {
      "id": "demo_0_0",
      "lods": [0, 1, 2],
      "features": [
        {
          "id": "toyohira_river",
          "kind": "waterbody",
          "width_m": 85,
          "internal_centerlines": 0
        },
        {
          "id": "bridge_001",
          "kind": "crossing",
          "transport": "road",
          "water": "toyohira_river",
          "status": "bridge",
          "vertical_clearance_m": 4.2,
          "cuts_water": false
        }
      ]
    }
  ],
  "evidence": {
    "game_view_checkpoints": [
      "station_integration",
      "broad_river",
      "road_water_bridge",
      "underground_rail",
      "distant_lod"
    ]
  }
}
```

## Public Data Policy

This toolkit is a validator and sample schema. It does not redistribute raw GIS
source data. If you generate manifests from GSI, OSM, PLATEAU, KSJ, or other
sources, you are responsible for following the source licenses and attribution
requirements.

## Roadmap

- SQLite adapter for chunk package tables
- GeoJSON adapter for QA-only fixtures
- negative fixture library for common broken map classes
- GitHub Actions workflow template
- Unity editor evidence manifest exporter

## License

MIT. See `LICENSE`.
