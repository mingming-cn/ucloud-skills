# UCloud SDK Usage

## Canonical pattern

The official `ucloud-sdk-python3` documentation shows two useful calling styles:

- Service helper style: `client.ulb().describe_ulb({...})`
- Raw action style: `client.invoke("DescribeULB", {...})`

Design this skill around those two patterns:

1. Prefer helper methods when the service and method names are known.
2. Fall back to `invoke` for unsupported or hard-to-locate helpers.
3. If the SDK does not make the correct action, required fields, or scope obvious, consult `references/doc-sources.md` before guessing.

## Credential conventions

Use these environment variables by default:

- `UCLOUD_PUBLIC_KEY`
- `UCLOUD_PRIVATE_KEY`
- `UCLOUD_PROJECT_ID`
- `UCLOUD_REGION`
- `UCLOUD_ZONE`
- `UCLOUD_BASE_URL`

Do not hardcode credentials in command lines or files unless the user explicitly asks and understands the risk.

## Parameter handling

- Keep request payloads as JSON objects.
- Inject `ProjectId`, `Region`, and `Zone` only when missing and environment defaults exist.
- Preserve official field names exactly as expected by UCloud OpenAPI.

## Operational guidance

- Start with read-only actions for discovery.
- For mutating actions, inspect target resources first so identifiers are precise.
- Keep the raw API response in JSON for downstream parsing and summaries.
- For create flows, default to EIP creation and binding when the target service supports public EIP access, unless the user asks for private-only deployment.
- Prefer security groups over firewall-based controls when both are supported.
- Generate initial passwords with letters and digits only unless the user explicitly asks for special characters.
