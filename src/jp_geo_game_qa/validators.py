from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationConfig:
    required_lods: set[int]
    broad_water_min_width_m: float = 50.0
    bridge_min_clearance_m: float = 0.45
    required_checkpoints: tuple[str, ...] = (
        "station_integration",
        "broad_river",
        "road_water_bridge",
        "underground_rail",
        "distant_lod",
    )


DEFAULT_CONFIG = ValidationConfig(required_lods={0, 1, 2})


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any) -> bool:
    return bool(value) if isinstance(value, bool) else str(value).lower() == "true"


def _gate(gate_id: str, failures: list[str], pass_message: str) -> dict[str, Any]:
    if failures:
        return {
            "id": gate_id,
            "status": "FAIL",
            "fail_count": len(failures),
            "message": failures[0],
            "failures": failures,
        }
    return {
        "id": gate_id,
        "status": "PASS",
        "fail_count": 0,
        "message": pass_message,
        "failures": [],
    }


def _iter_chunk_features(manifest: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    for chunk in _as_list(manifest.get("chunks")):
        chunk_dict = _as_dict(chunk)
        chunk_id = str(chunk_dict.get("id") or "<missing-chunk-id>")
        for feature in _as_list(chunk_dict.get("features")):
            rows.append((chunk_id, _as_dict(feature)))
    return rows


def validate_required_lods(manifest: dict[str, Any], config: ValidationConfig) -> dict[str, Any]:
    failures: list[str] = []
    chunks = _as_list(manifest.get("chunks"))
    if not chunks:
        failures.append("manifest has no chunks")
    for chunk in chunks:
        chunk_dict = _as_dict(chunk)
        chunk_id = str(chunk_dict.get("id") or "<missing-chunk-id>")
        lods = set()
        for item in _as_list(chunk_dict.get("lods")):
            try:
                lods.add(int(item))
            except (TypeError, ValueError):
                failures.append(f"chunk {chunk_id} has non-integer LOD: {item!r}")
        missing = sorted(config.required_lods - lods)
        if missing:
            failures.append(f"chunk {chunk_id} missing required LODs: {missing}")
    return _gate(
        "REQUIRED_LOD_COVERAGE",
        failures,
        f"all chunks include LODs {sorted(config.required_lods)}",
    )


def validate_broad_water(manifest: dict[str, Any], config: ValidationConfig) -> dict[str, Any]:
    failures: list[str] = []
    checked = 0
    for chunk_id, feature in _iter_chunk_features(manifest):
        if feature.get("kind") != "waterbody":
            continue
        width_m = _as_float(feature.get("width_m"))
        if width_m < config.broad_water_min_width_m:
            continue
        checked += 1
        internal_centerlines = int(_as_float(feature.get("internal_centerlines")))
        if internal_centerlines > 0:
            feature_id = str(feature.get("id") or "<missing-feature-id>")
            failures.append(
                f"chunk {chunk_id} broad waterbody {feature_id} has {internal_centerlines} internal centerlines"
            )
    return _gate(
        "BROAD_WATER_NO_INTERNAL_CENTERLINES",
        failures,
        f"checked {checked} broad waterbodies",
    )


def validate_crossings(manifest: dict[str, Any], config: ValidationConfig) -> dict[str, Any]:
    failures: list[str] = []
    checked = 0
    valid_statuses = {"bridge", "culvert", "tunnel", "underpass", "resolved"}
    for chunk_id, feature in _iter_chunk_features(manifest):
        if feature.get("kind") != "crossing":
            continue
        checked += 1
        feature_id = str(feature.get("id") or "<missing-feature-id>")
        status = str(feature.get("status") or "")
        if status not in valid_statuses:
            failures.append(f"chunk {chunk_id} crossing {feature_id} has unresolved status: {status!r}")
        if _as_bool(feature.get("cuts_water")):
            failures.append(f"chunk {chunk_id} crossing {feature_id} cuts the water surface")
        if status == "bridge":
            clearance = _as_float(feature.get("vertical_clearance_m"), default=-999.0)
            if clearance < config.bridge_min_clearance_m:
                failures.append(
                    f"chunk {chunk_id} bridge {feature_id} clearance {clearance:.2f}m "
                    f"is below {config.bridge_min_clearance_m:.2f}m"
                )
    return _gate(
        "ROAD_WATER_CROSSINGS_RESOLVED",
        failures,
        f"checked {checked} crossings",
    )


def validate_road_markings(manifest: dict[str, Any], _config: ValidationConfig) -> dict[str, Any]:
    failures: list[str] = []
    checked = 0
    exempt_classes = {"service", "private", "track", "footway", "path"}
    for chunk_id, feature in _iter_chunk_features(manifest):
        if feature.get("kind") != "road":
            continue
        if str(feature.get("class") or "") in exempt_classes:
            continue
        if feature.get("rendered", True) is False:
            continue
        checked += 1
        if not _as_bool(feature.get("has_markings")):
            feature_id = str(feature.get("id") or "<missing-feature-id>")
            failures.append(f"chunk {chunk_id} visible road {feature_id} lacks markings")
    return _gate(
        "VISIBLE_ROADS_HAVE_MARKINGS",
        failures,
        f"checked {checked} visible roads",
    )


def validate_underground_rail(manifest: dict[str, Any], _config: ValidationConfig) -> dict[str, Any]:
    failures: list[str] = []
    checked = 0
    for chunk_id, feature in _iter_chunk_features(manifest):
        if feature.get("kind") != "rail":
            continue
        mode = str(feature.get("mode") or "")
        underground = _as_bool(feature.get("underground"))
        if not underground and mode != "subway":
            continue
        checked += 1
        if _as_bool(feature.get("renders_on_surface")):
            feature_id = str(feature.get("id") or "<missing-feature-id>")
            failures.append(f"chunk {chunk_id} underground rail {feature_id} renders on the surface")
    return _gate(
        "UNDERGROUND_RAIL_NOT_SURFACE",
        failures,
        f"checked {checked} underground rail spans",
    )


def validate_visual_checkpoints(manifest: dict[str, Any], config: ValidationConfig) -> dict[str, Any]:
    evidence = _as_dict(manifest.get("evidence"))
    checkpoints = {str(item) for item in _as_list(evidence.get("game_view_checkpoints"))}
    failures = [
        f"missing required visual checkpoint evidence: {checkpoint}"
        for checkpoint in config.required_checkpoints
        if checkpoint not in checkpoints
    ]
    return _gate(
        "VISUAL_CHECKPOINT_EVIDENCE_PRESENT",
        failures,
        f"all required visual checkpoints present: {list(config.required_checkpoints)}",
    )


def validate_manifest(
    manifest: dict[str, Any],
    *,
    config: ValidationConfig = DEFAULT_CONFIG,
) -> dict[str, Any]:
    gates = [
        validate_required_lods(manifest, config),
        validate_broad_water(manifest, config),
        validate_crossings(manifest, config),
        validate_road_markings(manifest, config),
        validate_underground_rail(manifest, config),
        validate_visual_checkpoints(manifest, config),
    ]
    status = "PASS" if all(gate["status"] == "PASS" for gate in gates) else "FAIL"
    return {
        "schema": manifest.get("schema"),
        "status": status,
        "gates": gates,
        "fail_count": sum(gate["fail_count"] for gate in gates),
    }
