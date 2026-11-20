# Changelog

## Unreleased

- Require `KLE_DEMO_PASSWORD` from the local environment and stop writing demo passwords to a local credentials file.
- Restrict the optional MCP server to a marked synthetic database under `runtime-demo/` and retain loopback-only SSE binding.

- Added repository setup, contribution, security, and privacy documentation.
- Added GitHub issue templates, pull request template, and automated test workflow.
- Expanded ignore rules for local institutional data, generated artifacts, databases, and credentials.
- Documented that private source records and extracted seed data are not distributed.
- Documented the current unauthenticated MCP caller boundary.
- Restricted MCP SSE binding to numeric loopback addresses until caller authentication is implemented.
- Excluded the undocumented institutional logo and web-font binaries from Git while retaining local originals.
