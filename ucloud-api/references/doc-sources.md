# UCloud Documentation Sources

## Source order

Use these sources in order when the SDK alone does not provide enough information to execute a request safely:

1. SDK repository and SDK usage examples
2. UCloud API documentation
3. UCloud product documentation
4. UCloud tools documentation

## Official entry points

- SDK repository: `https://github.com/ucloud/ucloud-sdk-python3`
- API documentation: `https://github.com/UCloudDoc-Team/api`
- Product documentation: `https://docs.ucloud.cn/`
- Tools and SDK overview: `https://docs.ucloud.cn/tools`

## What to verify in each source

### API documentation

Use the API docs to verify:

- Exact action names
- Required request parameters
- Whether `Region`, `Zone`, or `ProjectId` are required
- Response field names
- Action-specific constraints or enumerations

### Product documentation

Use the product docs to verify:

- Product concepts and resource relationships
- Region or availability-zone behavior
- Operational constraints that are not obvious from the API schema
- Product terminology used by the user

### Tools documentation

Use the tools docs to verify:

- Cross-language SDK availability
- CLI naming that may help map product concepts to API actions
- Alternate invocation examples when SDK naming is unclear

## Operational rule

Do not guess missing API fields from product terminology alone. If the SDK and current context are insufficient, inspect the API docs first, then ask the user only for the values that remain unknown.
