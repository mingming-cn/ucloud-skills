---
name: ucloud-api
description: Invoke UCloud APIs through the official Python SDK. Use when an AI agent needs to inspect, create, update, or delete UCloud resources by calling real UCloud OpenAPI actions such as UHost (CVM cloud host), ULB, VPC, EIP, UDB, or other services, especially when the user wants the agent to execute cloud operations instead of only describing them.
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

## Product Naming

- Treat `UHost` as the UCloud cloud host product.
- Treat user requests that mention `CVM`, `ECS`, `EC2`, `VM`, `云主机`, `云服务器`, or similar cloud VM wording as requests for `UHost` unless the context clearly points to another product.
- When mapping a user request to APIs, prefer `UHost` actions and product documentation for these cloud host requests.

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
- Keep SDK and HTTP/client logging disabled by default. Enable verbose or debug logs only when the user explicitly asks to print logs or when the user explicitly asks for verbose debugging output.
- Present user-facing results in a clear, formatted structure. Prefer short sections, Markdown tables, and labeled fields over raw JSON dumps.
- Never print, repeat, or embed `UCLOUD_PUBLIC_KEY`, `UCLOUD_PRIVATE_KEY`, `--public-key`, or `--private-key` in commentary, plans, command previews, patch text, or user-facing summaries.
- Prefer credentials that are already present in environment variables. Treat command lines as visible and unsafe for secrets.
- If credentials are missing and the user provides them in chat, store them in the current process environment or another non-logged local mechanism before execution. Do not pass secrets as CLI flags.
- Keep payload keys in UCloud API casing, for example `Region`, `ProjectId`, `ULBId`.
- Use `--data-file` instead of long inline JSON when the payload is large.
- Do not fabricate parameter names. If the required parameters are unclear, consult official docs before executing.
- If the SDK method name, required fields, or resource semantics are unclear, consult the official API or product docs before making assumptions.
- If the user asks for a write operation and identifiers are ambiguous, query first, then confirm the exact target from the returned data.
- When information is missing, ask only for the fields that block execution, for example `Region`, `ProjectId`, `ULBId`, or credentials.
- After the user replies, normalize the values into the exact API field names and continue without restarting the whole workflow.
- If the user provides mixed free text and structured data, extract the usable values, show the interpreted payload briefly, and then execute.

## Output Style

- Default to concise Markdown with explicit section labels such as `Action`, `Result`, `Resources`, `Errors`, and `Next Steps`.
- For one resource or one operation result, prefer a two-column table such as `Field | Value`.
- For multiple resources, prefer a compact table with only the most decision-relevant columns first, such as resource ID, name, status, region, zone, IP, and billing mode.
- Use bullet lists only when tables would be awkward, for example when listing follow-up actions or caveats.
- Do not dump raw JSON unless the user explicitly asks for the raw response. Summarize first, then include only the key fields that matter for the task.
- When showing interpreted request parameters before execution, present them as a short labeled list or table so the user can verify the scope quickly.
- Mask or omit secrets and sensitive tokens in every formatted output.
- If the result set is large, show a short table with the most relevant rows first and mention that more items exist instead of pasting an excessively long response.

## Creation Defaults

- When creating a service or instance that supports EIP-based public network access, default to creating and binding an EIP unless the user explicitly asks for private-only networking.
- When both security groups and firewall features are available for the target service, default to security groups.
- When generating an initial password for a resource, use only uppercase letters, lowercase letters, and digits. Do not use special characters unless the user explicitly requests them.
- Unless the user explicitly requests a billing mode, prefer hourly prepaid first.
- If hourly prepaid is unavailable for the target service or configuration, try hourly postpaid next, then monthly prepaid.
- If hourly prepaid, hourly postpaid, and monthly prepaid are all unavailable, stop and ask the user whether to try yearly prepaid.
- If automatic EIP creation or security-group attachment requires extra fields, inspect the API docs first, then ask the user only for the remaining missing values.
- Before creating a billable EIP or public resource, mention that the creation flow will include the EIP binding by default.
- After a resource is created successfully, summarize the key resource information for the user instead of only dumping the raw response.
- Include the most important access and inventory fields that apply to the resource, such as username, generated password, internal IP, external IP, resource ID, region, zone, specification, billing mode, and bound security-group or network information, preferably in a table.
- If the created resource is a cloud host, determine the default login username from the operating system distribution before showing the username to the user.
- Use `ubuntu` for Ubuntu images. Use `root` for Debian, RedHat, and Rocky images unless the image metadata or product docs state otherwise.
- If the create response does not contain all key fields, call the matching describe API to fill the missing information before reporting back to the user.

## Missing Information Handling

- Missing credentials:
  Ask for `UCLOUD_PUBLIC_KEY` and `UCLOUD_PRIVATE_KEY`, and tell the user they will be used through environment variables or another non-logged local mechanism only. Do not ask the user to place credentials directly in a command line.
- Missing scope:
  Ask for `ProjectId`, `Region`, or `Zone` only if the chosen action requires them and they are not already available from the environment.
- Missing target resource:
  Ask for the exact identifier such as `ULBId`, `EIPId`, `VPCId`, `InstanceId`, or another action-specific ID.
- Missing action parameters:
  Ask for only the required fields that are still absent after checking the SDK, the API docs, and the current context.
- After receiving the answer:
  Convert the reply into a JSON object, merge it with existing parameters, and continue with the same action instead of asking the user to restate the full request.

## Error Handling

- When an error occurs, first try to diagnose and repair it automatically if the fix is safe and can be derived from the current context, API docs, or lookup APIs.
- Prefer self-repair steps such as filling missing public parameters, correcting action-specific payload fields, retrying with the required `ProjectId`, or switching from unclear SDK helper mode to raw action mode after verification.
- Do not retry blindly. Each retry must be based on a specific diagnosis.
- Keep retries quiet by default. Do not enable SDK logs just because a request failed; enable them only if the user explicitly asks to print logs or requests verbose debugging output.
- If the API returns `299 IAM permission error`, first check the API definition to determine whether `ProjectId` is a required parameter.
- If the API requires `ProjectId` and the request did not include it, treat `299` as a likely missing-`ProjectId` problem. Resolve or ask for `ProjectId`, then retry.
- If the API requires `ProjectId` and the request already included it, or if the API does not require `ProjectId`, treat `299` as a real permission problem.
- For a real permission problem, stop the execution, tell the user they do not currently have permission for that API, and ask them to add the required permission before retrying.
- If the error cannot be repaired safely, show the user the detailed error information in a structured format, including the action name, the key request context that matters for diagnosis, the error code, and the error message.
- When stopping because of an unrecoverable error, give the user concrete next-step suggestions, such as adding IAM permission, providing a missing identifier, confirming the correct region or project, checking balance, or verifying whether the API is available for their account or region.

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

### Override endpoint only

```bash
python ./scripts/invoke_ucloud.py \
  --action DescribeULB \
  --base-url https://api.ucloud.cn \
  --data '{"ProjectId":"org-xxx"}'
```

### Credentials through environment variables

```bash
python ./scripts/invoke_ucloud.py \
  --action DescribeULB \
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
- Read [`references/error-handling.md`](./references/error-handling.md) for the `299 IAM permission error` decision rule.
- Use the official UCloud API documentation to confirm action-specific parameters before execution.
