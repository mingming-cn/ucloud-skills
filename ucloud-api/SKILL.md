---
name: ucloud-api
description: Invoke UCloud APIs through the official Python SDK. Use when Codex needs to inspect, create, update, or delete UCloud resources by calling real UCloud OpenAPI actions such as CVM, ULB, VPC, EIP, UDB, or other services, especially when the user wants an agent to execute cloud operations instead of only describing them.
---

# UCloud API

Use the bundled script to call UCloud OpenAPI through `ucloud-sdk-python3`. Prefer this skill when the user wants actual cloud operations, resource inspection, or parameterized automation against a UCloud account.

## Preconditions

- Require Python 3.
- Require the `ucloud` SDK package to be installed in the execution environment.
- Require credentials in environment variables:
  - `UCLOUD_PUBLIC_KEY`
  - `UCLOUD_PRIVATE_KEY`
- Support optional defaults:
  - `UCLOUD_PROJECT_ID`
  - `UCLOUD_REGION`
  - `UCLOUD_ZONE`
  - `UCLOUD_BASE_URL`

If the SDK is missing, stop and either install it with user approval or explain that the environment is not ready for live API calls.
If credentials, target identifiers, region, zone, project, or action-specific parameters are missing, ask the user for the exact missing items, parse the reply into the request payload, and then continue the execution flow.

## Source Priority

Use sources in this order when deciding how to invoke an API:

1. SDK code and examples in `ucloud-sdk-python3`
2. UCloud API documentation for action names, required parameters, and response fields
3. UCloud product documentation for product semantics, region or deployment constraints, and resource concepts
4. UCloud tools documentation for cross-checking SDK or CLI naming and usage patterns

If the SDK does not expose enough information to choose the correct action, required fields, or resource scope, consult the official docs before asking the user or executing a request.

## Invocation Flow

1. Translate the user request into either:
   - a service and SDK method pair such as `ulb + describe_ulb`
   - a raw OpenAPI action such as `DescribeULB`
2. Check the SDK and, if needed, official UCloud docs to determine the correct action, required parameters, and whether `ProjectId`, `Region`, or `Zone` are needed.
3. Check whether credentials, target resource identifiers, and action-specific required fields are present.
4. If any required information is missing, ask the user a concise follow-up question that lists only the missing fields.
5. Parse the user reply into structured values and merge them into the JSON payload.
6. Add `ProjectId`, `Region`, or `Zone` only when the API needs them and the user or environment provides them.
7. Run [`scripts/invoke_ucloud.py`](./scripts/invoke_ucloud.py).
8. Review the JSON response before taking a follow-up destructive action.

## Choose the Call Mode

Use SDK method mode first when the service client and method are obvious from the SDK naming:

```bash
python ./scripts/invoke_ucloud.py \
  --service ulb \
  --method describe_ulb \
  --data '{"ULBId":"ulb-xxxx"}'
```

Use raw action mode when the SDK helper is unclear or absent:

```bash
python ./scripts/invoke_ucloud.py \
  --action DescribeULB \
  --data '{"ULBId":"ulb-xxxx"}'
```

## Working Rules

- Prefer read-only actions first when the request could affect existing resources.
- Echo the concrete action name in the commentary before executing writes or deletes.
- Keep payload keys in UCloud API casing, for example `Region`, `ProjectId`, `ULBId`.
- Use `--data-file` instead of long inline JSON when the payload is large.
- Do not fabricate parameter names. If the required parameters are unclear, consult official docs before executing.
- If the SDK method name, required fields, or resource semantics are unclear, consult the official API or product docs before making assumptions.
- If the user asks for a write operation and identifiers are ambiguous, query first, then confirm the exact target from the returned data.
- When information is missing, ask only for the fields that block execution, for example `Region`, `ProjectId`, `ULBId`, or credentials.
- After the user replies, normalize the values into the exact API field names and continue without restarting the whole workflow.
- If the user provides mixed free text and structured data, extract the usable values, show the interpreted payload briefly, and then execute.

## Creation Defaults

- When creating a service or instance that supports EIP-based public network access, default to creating and binding an EIP unless the user explicitly asks for private-only networking.
- When both security groups and firewall features are available for the target service, default to security groups.
- When generating an initial password for a resource, use only uppercase letters, lowercase letters, and digits. Do not use special characters unless the user explicitly requests them.
- If automatic EIP creation or security-group attachment requires extra fields, inspect the API docs first, then ask the user only for the remaining missing values.
- Before creating a billable EIP or public resource, mention that the creation flow will include the EIP binding by default.

## Missing Information Handling

- Missing credentials:
  Ask for `UCLOUD_PUBLIC_KEY` and `UCLOUD_PRIVATE_KEY`, unless the user prefers to set them as environment variables directly.
- Missing scope:
  Ask for `ProjectId`, `Region`, or `Zone` only if the chosen action requires them and they are not already available from the environment.
- Missing target resource:
  Ask for the exact identifier such as `ULBId`, `EIPId`, `VPCId`, `InstanceId`, or another action-specific ID.
- Missing action parameters:
  Ask for only the required fields that are still absent after checking the SDK, the API docs, and the current context.
- After receiving the answer:
  Convert the reply into a JSON object, merge it with existing parameters, and continue with the same action instead of asking the user to restate the full request.

## Common Lookup APIs

When common parameters are missing, use these APIs for discovery before asking the user:

- `ListRegions`: query available regions when `Region` is missing or the user gives only a city or product name.
- `ListZones`: query available zones when `Zone` is missing and the chosen region is known or can be inferred.
- `GetProjectList`: query accessible projects when `ProjectId` is missing.
- `GetBalance`: query account balance before create flows when quota or billing readiness may matter.

Use these lookup APIs to narrow the missing values first. If multiple valid options remain after lookup, present the short list to the user and ask them to choose.

Use [`scripts/resolve_common_params.py`](./scripts/resolve_common_params.py) to automate these lookups before asking the user.

## Script Usage

### Inline JSON

```bash
python ./scripts/invoke_ucloud.py \
  --action DescribeInstance \
  --data '{"Region":"cn-bj2"}'
```

### JSON file

```bash
python ./scripts/invoke_ucloud.py \
  --service cvm \
  --method describe_instance \
  --data-file ./request.json
```

### Override credentials or endpoint

```bash
python ./scripts/invoke_ucloud.py \
  --action DescribeULB \
  --public-key "$UCLOUD_PUBLIC_KEY" \
  --private-key "$UCLOUD_PRIVATE_KEY" \
  --base-url https://api.ucloud.cn \
  --data '{"ProjectId":"org-xxx"}'
```

### Generate an alphanumeric password

```bash
python ./scripts/generate_password.py --length 20
```

### Resolve common parameters

```bash
python ./scripts/resolve_common_params.py \
  --need region \
  --need zone \
  --need project \
  --region-hint beijing
```

### Resolve balance only

```bash
python ./scripts/resolve_common_params.py --need balance
```

## References

- Read [`references/sdk-usage.md`](./references/sdk-usage.md) for the SDK calling pattern and environment conventions.
- Read [`references/doc-sources.md`](./references/doc-sources.md) for the documentation lookup order and URL entry points.
- Read [`references/common-lookups.md`](./references/common-lookups.md) for the shared discovery APIs used to fill missing public parameters.
- Use the official UCloud API documentation to confirm action-specific parameters before execution.
