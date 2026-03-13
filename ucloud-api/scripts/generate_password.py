#!/usr/bin/env python3
"""Generate an alphanumeric password for UCloud resource creation."""

from __future__ import annotations

import argparse
import secrets
import string


ALPHANUMERIC = string.ascii_letters + string.digits


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate an alphanumeric password without special characters.",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=16,
        help="Password length. Default: 16.",
    )
    return parser


def generate_password(length: int) -> str:
    if length <= 0:
        raise SystemExit("Password length must be greater than 0.")
    return "".join(secrets.choice(ALPHANUMERIC) for _ in range(length))


def main() -> int:
    args = build_parser().parse_args()
    print(generate_password(args.length))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
