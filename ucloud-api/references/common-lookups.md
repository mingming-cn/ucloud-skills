# Common Lookup APIs

Use these APIs when shared request scope is missing and the value can be discovered from the account context.

## Region and zone discovery

- `ListRegions`
  Use when `Region` is missing.
- `ListZones`
  Use when `Zone` is missing.

Preferred flow:

1. Call `ListRegions` if no region is known.
2. Once `Region` is known, call `ListZones` if the action also needs a zone.
3. If multiple options remain, show the user a concise list and ask them to choose.

## Project discovery

- `GetProjectList`
  Use when `ProjectId` is missing and the account may contain multiple projects.

If only one project is returned, use it directly. If multiple projects are returned, ask the user to choose the exact project.

## Balance check

- `GetBalance`
  Use before billable create flows when account balance may affect the operation, or when the user asks about account readiness.

## Operational rule

Prefer these lookup APIs over asking broad questions like "which region?" or "which project?" when the value can be discovered from the account. Ask the user only after discovery still leaves multiple valid choices or no usable result.

Use `./scripts/resolve_common_params.py` to bundle these lookups into one step and return:

- `resolved`: directly usable values
- `choices`: multiple valid candidates that still require user selection
- `missing`: upstream values still required before the next lookup can run
- `balance`: raw balance response when requested
