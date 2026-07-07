# Security Policy

**Snapshot date:** 2026-07-07

## Reporting Vulnerabilities

If you discover a security vulnerability in a listed project, report it to the project maintainers
following their disclosure policy.

For issues with the compendium itself (data integrity, credential leaks),
please open an issue.

## Security Notes in the Catalog

MCP servers with filesystem, shell, browser, credential, database, email, cloud,
or infrastructure access are flagged with security notes in the catalog.

## Best Practices for MCP Security

- Validate MCP server source code before deployment
- Use permission systems to limit server capabilities
- Never expose MCP servers with shell/filesystem access to untrusted users
- Review MCP server configurations for credential exposure
- Run MCP servers in isolated environments where possible

*Snapshot: 2026-07-07*