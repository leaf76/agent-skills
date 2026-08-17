# Security

This repository is a library of Agent Skills (Markdown + helper scripts). It should not contain live secrets.

## Do not commit

- API keys, tokens, passwords, cookies, or session material
- `.env`, `.dev.vars`, `auth.json`, `credentials.json`, `*.pem`
- Product-specific test accounts or internal hostnames

Use environment variables or a secret manager instead.

## Reporting a vulnerability

Please use [GitHub private vulnerability reporting](https://github.com/leaf76/agent-skills/security/advisories/new) rather than a public issue.

If the report is about a copied upstream skill (Cloudflare / OpenAI / others), also notify the upstream project. See [NOTICE](NOTICE).

## Scope

In scope: secrets accidentally committed here, unsafe helper scripts, instructions that would leak credentials if followed as written.

Out of scope: running a copied upstream skill against your own infrastructure, or issues that only exist in third-party CLIs this repo documents (`wrangler`, Hermes Chrome, Grok CLI, and similar).
