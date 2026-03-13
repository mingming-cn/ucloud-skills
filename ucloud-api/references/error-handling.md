# Error Handling

## General rule

When a call fails:

1. Diagnose the error from the API definition, current request payload, known defaults, and recent lookup results.
2. Try to repair the problem automatically if the repair is safe and specific.
3. Retry only when there is a concrete diagnosis, not as a blind repeat.
4. If the problem cannot be repaired safely, stop and report the error details to the user.
5. Provide concrete next actions the user can take before retrying.

Safe repair examples:

- Add a missing `ProjectId`, `Region`, or `Zone`
- Resolve shared parameters with `ListRegions`, `ListZones`, or `GetProjectList`
- Correct an obvious payload omission confirmed by the API definition
- Switch from SDK helper mode to raw action mode when the helper is unclear but the action is known
- Fall back through the default billing order: hourly prepaid, hourly postpaid, monthly prepaid, then ask before trying yearly prepaid
- Call a follow-up describe API after a successful create action if the create response omits key fields the user needs
- Infer the correct default cloud-host username from the image distribution before reporting login information

When reporting an unrecoverable error, include:

- API action or service and method
- Relevant request scope such as `ProjectId`, `Region`, `Zone`, or target resource ID
- Error code
- Error message
- Recommended next steps
## `299 IAM permission error`

Use this decision rule when an API call fails with `299 IAM permission error`:

1. Check the API definition.
2. Determine whether the API requires `ProjectId`.
3. If the API requires `ProjectId` and the request did not include it, treat the `299` as a likely missing-`ProjectId` issue first.
4. Resolve `ProjectId` with `GetProjectList` or ask the user for the exact project, then retry.
5. If the API requires `ProjectId` and the request already included it, or if the API does not require `ProjectId`, treat the `299` as a real permission error.
6. Tell the user they currently lack permission for that API and need to add the required permission before retrying.

## Operational note

Do not immediately conclude that `299` always means missing permission. Check the `ProjectId` requirement first, because some APIs surface the same error when `ProjectId` is required but omitted.
