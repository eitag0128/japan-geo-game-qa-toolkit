# Manifest Schema v1

This schema is intentionally small. It is a QA interchange format, not a
replacement for GIS source data or a runtime mesh format.

## Top-Level Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `schema` | string | yes | Must identify the manifest version. |
| `chunks` | array | yes | Runtime map chunks to validate. |
| `evidence` | object | yes | Visual or runtime evidence references. |

## Chunk Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | string | yes | Stable chunk identifier. |
| `lods` | array of integers | yes | LODs available for this chunk. |
| `features` | array | yes | QA feature summaries for this chunk. |

## Feature Kinds

### Waterbody

```json
{
  "id": "toyohira_river",
  "kind": "waterbody",
  "width_m": 85,
  "internal_centerlines": 0
}
```

Broad waterbodies should render as a coherent surface. If a broad waterbody
still contains internal centerline strokes, it is usually a sign that river
linework leaked into the final visual package.

### Crossing

```json
{
  "id": "bridge_001",
  "kind": "crossing",
  "transport": "road",
  "water": "toyohira_river",
  "status": "bridge",
  "vertical_clearance_m": 4.2,
  "cuts_water": false
}
```

The accepted `status` values are `bridge`, `culvert`, `tunnel`, `underpass`, and
`resolved`. Road-water crossings must not cut the water surface unless the
pipeline has an explicit, documented mask system outside this public schema.

### Road

```json
{
  "id": "urban_primary_001",
  "kind": "road",
  "class": "primary",
  "rendered": true,
  "has_markings": true
}
```

Visible non-service roads should have markings or another explicit visual
treatment. Thin unmarked map lines often pass geometry checks but fail player
readability.

### Rail

```json
{
  "id": "subway_span",
  "kind": "rail",
  "mode": "subway",
  "underground": true,
  "renders_on_surface": false
}
```

Underground rail and subway spans should not appear as terrain-following
surface rail.

## Evidence

```json
{
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

The first release only checks that required checkpoint IDs are present. Future
versions may add screenshot metadata, image hashes, and runtime probe summaries.
