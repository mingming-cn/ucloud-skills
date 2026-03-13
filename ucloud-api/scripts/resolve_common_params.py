#!/usr/bin/env python3
"""Resolve common UCloud parameters with built-in lookup APIs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import invoke_ucloud


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve Region, Zone, ProjectId, and balance with common UCloud APIs.",
    )
    parser.add_argument(
        "--need",
        action="append",
        choices=("region", "zone", "project", "balance"),
        default=[],
        help="Requested resolution target. Repeatable.",
    )
    parser.add_argument("--region", help="Known Region value.")
    parser.add_argument("--zone", help="Known Zone value.")
    parser.add_argument("--project-id", help="Known ProjectId value.")
    parser.add_argument("--region-hint", help="Region hint for matching lookup results.")
    parser.add_argument("--zone-hint", help="Zone hint for matching lookup results.")
    parser.add_argument("--project-hint", help="Project hint for matching lookup results.")
    parser.add_argument("--public-key", help="Override UCLOUD_PUBLIC_KEY.")
    parser.add_argument("--private-key", help="Override UCLOUD_PRIVATE_KEY.")
    parser.add_argument("--base-url", help="Override UCLOUD_BASE_URL.")
    parser.add_argument(
        "--balance-data",
        default="{}",
        help="Optional JSON object payload for GetBalance.",
    )
    return parser


def normalize_need(values: list[str]) -> list[str]:
    if values:
        return values
    return ["region", "zone", "project"]


def find_list(response: Any, candidate_keys: tuple[str, ...]) -> list[dict[str, Any]]:
    serialized = invoke_ucloud.serialize(response)
    if isinstance(serialized, dict):
        for key in candidate_keys:
            value = serialized.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def compact_option(item: dict[str, Any], preferred_keys: tuple[str, ...]) -> dict[str, Any]:
    result = {}
    for key in preferred_keys:
        value = item.get(key)
        if value not in (None, ""):
            result[key] = value
    if result:
        return result
    return item


def build_lookup_args(base_args: argparse.Namespace, action: str, data: dict[str, Any]) -> argparse.Namespace:
    return argparse.Namespace(
        action=action,
        service=None,
        method=None,
        data=json.dumps(data, ensure_ascii=False),
        data_file=None,
        public_key=base_args.public_key,
        private_key=base_args.private_key,
        project_id=base_args.project_id,
        region=base_args.region,
        zone=base_args.zone,
        base_url=base_args.base_url,
    )


def invoke_action(client: Any, base_args: argparse.Namespace, action: str, data: dict[str, Any]) -> Any:
    action_args = build_lookup_args(base_args, action, data)
    payload = invoke_ucloud.merge_defaults(invoke_ucloud.load_payload(action_args), action_args)
    return invoke_ucloud.invoke(client, action_args, payload)


def text_matches(item: dict[str, Any], hint: str | None) -> bool:
    if not hint:
        return True
    needle = hint.strip().lower()
    for value in item.values():
        if isinstance(value, str) and needle in value.lower():
            return True
    return False


def resolve_single(items: list[dict[str, Any]], hint: str | None) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    matched = [item for item in items if text_matches(item, hint)]
    if len(matched) == 1:
        return matched[0], matched
    return None, matched


def resolve_region(client: Any, args: argparse.Namespace, result: dict[str, Any]) -> None:
    known_region = args.region or os.getenv("UCLOUD_REGION")
    if known_region:
        result["resolved"]["Region"] = known_region
        return

    response = invoke_action(client, args, "ListRegions", {})
    regions = find_list(response, ("Regions", "RegionSet", "DataSet"))
    options = [compact_option(item, ("Region", "RegionName")) for item in regions]
    selected, matched = resolve_single(options, args.region_hint)
    result["lookups"]["ListRegions"] = options
    if selected:
        result["resolved"]["Region"] = selected.get("Region")
    elif matched:
        result["choices"]["Region"] = matched
    elif options:
        result["choices"]["Region"] = options


def resolve_zone(client: Any, args: argparse.Namespace, result: dict[str, Any]) -> None:
    known_zone = args.zone or os.getenv("UCLOUD_ZONE")
    if known_zone:
        result["resolved"]["Zone"] = known_zone
        return

    region = result["resolved"].get("Region") or args.region or os.getenv("UCLOUD_REGION")
    if not region:
        result["missing"].append("Region")
        return

    response = invoke_action(client, args, "ListZones", {"Region": region})
    zones = find_list(response, ("Zones", "ZoneSet", "DataSet"))
    options = [compact_option(item, ("Zone", "ZoneName", "Region")) for item in zones]
    selected, matched = resolve_single(options, args.zone_hint)
    result["lookups"]["ListZones"] = options
    if selected:
        result["resolved"]["Zone"] = selected.get("Zone")
    elif matched:
        result["choices"]["Zone"] = matched
    elif options:
        result["choices"]["Zone"] = options


def resolve_project(client: Any, args: argparse.Namespace, result: dict[str, Any]) -> None:
    known_project = args.project_id or os.getenv("UCLOUD_PROJECT_ID")
    if known_project:
        result["resolved"]["ProjectId"] = known_project
        return

    response = invoke_action(client, args, "GetProjectList", {})
    projects = find_list(response, ("ProjectSet", "ProjectList", "DataSet"))
    options = [compact_option(item, ("ProjectId", "ProjectName")) for item in projects]
    selected, matched = resolve_single(options, args.project_hint)
    result["lookups"]["GetProjectList"] = options
    if selected:
        result["resolved"]["ProjectId"] = selected.get("ProjectId")
    elif len(options) == 1:
        result["resolved"]["ProjectId"] = options[0].get("ProjectId")
    elif matched:
        result["choices"]["ProjectId"] = matched
    elif options:
        result["choices"]["ProjectId"] = options


def resolve_balance(client: Any, args: argparse.Namespace, result: dict[str, Any]) -> None:
    try:
        payload = json.loads(args.balance_data)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in --balance-data: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit("--balance-data must be a JSON object.")
    response = invoke_action(client, args, "GetBalance", payload)
    result["balance"] = invoke_ucloud.serialize(response)


def main() -> int:
    args = build_parser().parse_args()
    args.need = normalize_need(args.need)
    client = invoke_ucloud.build_client(args)
    result = {
        "resolved": {},
        "choices": {},
        "missing": [],
        "lookups": {},
    }

    if "region" in args.need:
        resolve_region(client, args, result)
    if "zone" in args.need:
        resolve_zone(client, args, result)
    if "project" in args.need:
        resolve_project(client, args, result)
    if "balance" in args.need:
        resolve_balance(client, args, result)

    result["missing"] = sorted(set(result["missing"]))
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
