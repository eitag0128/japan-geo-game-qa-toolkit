from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .validators import DEFAULT_CONFIG, ValidationConfig, validate_manifest


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jggqa",
        description="Validate a game map QA manifest.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="validate a JSON QA manifest")
    validate.add_argument("manifest", type=Path)
    validate.add_argument(
        "--json",
        action="store_true",
        help="print machine-readable validation output",
    )
    validate.add_argument(
        "--required-lods",
        default=",".join(str(item) for item in sorted(DEFAULT_CONFIG.required_lods)),
        help="comma-separated LODs required for every chunk",
    )
    validate.add_argument(
        "--required-checkpoints",
        default=",".join(DEFAULT_CONFIG.required_checkpoints),
        help="comma-separated visual checkpoint ids required in evidence.game_view_checkpoints",
    )
    return parser


def parse_csv_ints(value: str) -> set[int]:
    out: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            out.add(int(item))
        except ValueError as exc:
            raise SystemExit(f"invalid integer in --required-lods: {item}") from exc
    return out


def parse_csv_strings(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


def print_text_report(report: dict[str, Any]) -> None:
    status = report["status"]
    print(f"status: {status}")
    print(f"checked_gates: {len(report['gates'])}")
    for gate in report["gates"]:
        prefix = "PASS" if gate["status"] == "PASS" else "FAIL"
        print(f"- {prefix} {gate['id']}: {gate['message']}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        config = ValidationConfig(
            required_lods=parse_csv_ints(args.required_lods),
            required_checkpoints=parse_csv_strings(args.required_checkpoints),
        )
        report = validate_manifest(load_json(args.manifest), config=config)
        if args.json:
            json.dump(report, sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
        else:
            print_text_report(report)
        return 0 if report["status"] == "PASS" else 1

    parser.error(f"unknown command: {args.command}")
    return 2
