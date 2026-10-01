# Security policy

## Scope

Cine Agent Skills is primarily an offline planning library and CLI. The optional
runtime can read project files, persist local state, connect to a user-configured
MCP server, and call explicitly allowlisted tools. It must not receive secrets
through project artifacts or untrusted prompts.

## Supported line

The active prerelease line is `0.3.x`. Historical package versions are retained
for migration evidence, not as active runtime targets.

## Report a vulnerability

Please do not disclose exploitable details in a public issue. Use GitHub's
**Security** tab and submit a private vulnerability report when that feature is
available for the repository. If private reporting is unavailable, open an
issue titled `Security contact requested` without technical details and wait for
maintainer instructions.

Include, when safe to share privately:

- the affected commit, version, or file;
- a minimal reproduction;
- impact and likely attack boundary;
- any mitigation already tested.

Do not include API keys, MCP credentials, private scripts, production media, or
personal data in an issue or pull request.

## Runtime safety expectations

- Keep MCP state and receipts outside validated source packages.
- Use explicit tool allowlists and negotiated input schemas.
- Treat disconnected, malformed, oversized, or ambiguous external results as
  blocked or unknown; do not blindly replay side effects.
- Never enable arbitrary model-supplied Python execution as a shortcut around
  the standard MCP boundary.
