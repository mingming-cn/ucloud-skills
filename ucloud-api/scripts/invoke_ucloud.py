#!/usr/bin/env python3
"""Invoke UCloud OpenAPI through the official Python SDK."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Invoke UCloud OpenAPI through the Python SDK.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--action", help="Raw OpenAPI action name, for example DescribeULB.")
    mode.add_argument(
        "--service",
        help="SDK service accessor name, for example ulb or cvm. Requires --method.",
    )
    parser.add_argument(
        "--method",
        help="SDK service method name, for example describe_ulb. Requires --service.",
    )
    parser.add_argument(
        "--data",
        default="{}",
        help="Inline JSON object payload.",
    )
    parser.add_argument(
        "--data-file",
        help="Path to a JSON file containing the request payload.",
    )
    parser.add_argument("--public-key", help="Override UCLOUD_PUBLIC_KEY.")
    parser.add_argument("--private-key", help="Override UCLOUD_PRIVATE_KEY.")
    parser.add_argument("--project-id", help="Default ProjectId if absent in payload.")
    parser.add_argument("--region", help="Default Region if absent in payload.")
    parser.add_argument("--zone", help="Default Zone if absent in payload.")
    parser.add_argument("--base-url", help="Override SDK base URL.")
    return parser


def load_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.data_file:
        raw = Path(args.data_file).read_text(encoding="utf-8")
    else:
        raw = args.data
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON payload: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit("Payload must be a JSON object.")
    return payload


def get_credentials(args: argparse.Namespace) -> tuple[str, str]:
    public_key = args.public_key or os.getenv("UCLOUD_PUBLIC_KEY")
    private_key = args.private_key or os.getenv("UCLOUD_PRIVATE_KEY")
    if not public_key or not private_key:
        raise SystemExit(
            "Missing credentials. Set UCLOUD_PUBLIC_KEY and UCLOUD_PRIVATE_KEY, "
            "or pass --public-key and --private-key."
        )
    return public_key, private_key


def merge_defaults(payload: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    defaults = {
        "ProjectId": args.project_id or os.getenv("UCLOUD_PROJECT_ID"),
        "Region": args.region or os.getenv("UCLOUD_REGION"),
        "Zone": args.zone or os.getenv("UCLOUD_ZONE"),
    }
    merged = dict(payload)
    for key, value in defaults.items():
        if value and key not in merged:
            merged[key] = value
    return merged


def serialize(value: Any) -> Any:
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return value.to_dict()
    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if hasattr(value, "__dict__"):
        return {k: serialize(v) for k, v in vars(value).items() if not k.startswith("_")}
    return value


def build_client(args: argparse.Namespace):
    try:
        from ucloud.client import Client
    except ImportError as exc:
        raise SystemExit(
            "The 'ucloud' SDK is not installed in this environment. "
            "Install ucloud-sdk-python3 before invoking the API."
        ) from exc

    public_key, private_key = get_credentials(args)
    config = {
        "public_key": public_key,
        "private_key": private_key,
    }
    if args.project_id or os.getenv("UCLOUD_PROJECT_ID"):
        config["project_id"] = args.project_id or os.getenv("UCLOUD_PROJECT_ID")
    if args.region or os.getenv("UCLOUD_REGION"):
        config["region"] = args.region or os.getenv("UCLOUD_REGION")
    base_url = args.base_url or os.getenv("UCLOUD_BASE_URL")
    if base_url:
        config["base_url"] = base_url
    return Client(config)


def invoke(client: Any, args: argparse.Namespace, payload: dict[str, Any]) -> Any:
    if args.action:
        return client.invoke(args.action, payload)

    if not args.method:
        raise SystemExit("--method is required when --service is used.")

    accessor = getattr(client, args.service, None)
    if accessor is None:
        raise SystemExit(f"Unknown service accessor on client: {args.service}")

    service_client = accessor()
    method = getattr(service_client, args.method, None)
    if method is None:
        raise SystemExit(
            f"Unknown method '{args.method}' for service '{args.service}'."
        )
    return method(payload)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    payload = merge_defaults(load_payload(args), args)
    client = build_client(args)
    response = invoke(client, args, payload)
    print(json.dumps(serialize(response), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
