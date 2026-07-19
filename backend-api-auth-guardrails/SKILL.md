---
name: backend-api-auth-guardrails
description: Use when backend, API, authentication, authorization, session, token, password, webhook, rate limit, audit log, CORS, CSRF, client error response, OIDC multi-RP browser logout, or front-channel logout work is in scope.
---

# Backend API Auth Guardrails

This is a domain-specific expansion of `/Users/cy76/.codex/AGENTS.md`. It may add backend, API, and auth requirements, but it must never weaken `AGENTS.md`, `SECURITY`, secrets handling, input validation, production safety, or destructive-command restrictions.

## API Contracts

- Prefer backward-compatible changes; do not break public API contracts without approval or versioning.
- Prefer `RESTful` resource naming, HTTP methods, status codes, and versioning. If deviating from `RESTful`, explain the trade-off.
- Keep payloads minimal. Prefer incremental reads, partial reads, `PATCH`, or equivalent partial updates over full refetches, page refreshes, or whole-resource overwrites.
- Validate external input before use, including type, range, state, and authorization.
- Query capabilities such as `pagination`, `filter`, `sort`, and `search` must use explicit allowlists and reasonable limits.

## Authentication And Authorization

- Prefer standard auth models: `OIDC`, `OAuth 2.0`, `JWT`, or `server-side session`. Do not invent account verification, token, session, or signature protocols.
- Web defaults: use `OIDC` login, create a backend `server-side session`, and maintain login with `HttpOnly Secure SameSite` cookies.
- Cloudflare session state: prefer `Durable Objects` or `Redis` when strong consistency or immediate revoke is required; use `KV` only when eventual consistency is acceptable.
- Mobile defaults: use `OIDC Authorization Code + PKCE` with short-lived access tokens and rotating refresh tokens.
- Token-based auth must validate issuer, audience, expiry, rotation, revoke/logout, and permission-change refresh or revalidation behavior.
- Always distinguish `authentication` from `authorization`; protected resources are `deny by default`.
- Bearer token APIs must validate `iss`, `aud`, `exp`, and check `scope`, `role`, or `permission` explicitly.

## Passwords, Sessions, And Browser Auth

- If local password login exists, hash passwords with `Argon2id` or `bcrypt`; never store plaintext, reversible encryption, or custom hashes.
- Email/phone identity or recovery channels need verification plus short-lived, one-time-use verification mechanisms.
- `password reset`, recovery, disable/suspend/delete/restore, and key account-data changes must define permission boundaries, expiry, replay protection, rate limits, retention, and audit trail.
- Password, email, role, or permission changes must handle existing sessions, refresh tokens, and remember-me tokens with revoke or re-auth requirements.
- Browser-based auth should not store sensitive tokens in `localStorage`.
- Cookie auth must handle `HttpOnly`, `Secure`, `SameSite`, and `CSRF`; cross-origin access must use an explicit `CORS allowlist`.

## OIDC Multi-RP Browser Logout (Front-Channel)

Use this section when **one identity provider** serves **multiple browser apps** on different origins and “sign out everywhere in this browser” is required.

### When to use / when not to use

- **Use** for multi-subdomain web products that share OIDC SSO but keep **independent local sessions** (cookies or SPA tokens per origin).
- **Do not use** as a substitute for all-device logout (that needs account-wide session/refresh revoke + product UX).
- **Do not assume** “RP-initiated logout” alone clears other RPs: browser same-origin policy blocks clearing foreign cookies.

### Correct model

1. **RP logout path:** clear local session first, then top-level navigate to IdP `end_session` / `/oauth/logout` with `client_id`, allowlisted `post_logout_redirect_uri`, and **`id_token_hint` when available**.
2. **IdP revoke gate:** bare cross-site GET may clear only the IdP SSO cookie; **server session revoke** typically needs POST (CSRF-safe) or GET with `id_token_hint` bound to the current session subject.
3. **IdP fan-out:** when RPs register `frontchannel_logout_uri(s)`, return an HTML intermediate page that loads each allowlisted URI in a hidden iframe (`iss` + optional `sid`), then redirect to `post_logout_redirect_uri`.
4. **RP front-channel endpoint:** e.g. `GET /auth/frontchannel-logout?iss=…&sid=…` — verify `iss` exactly, clear this origin’s cookies/tokens, `Cache-Control: no-store`, allow framing only from the IdP (`Content-Security-Policy: frame-ancestors <issuer>`). Do **not** redirect back to the IdP (loop risk).
5. **`sid`:** put central session id on `id_token` so RPs can bind local sessions and match front-channel notifications.

### Pitfalls (easy to get wrong)

- **CSP:** global `default-src 'self'` **blocks** cross-origin RP iframes. Logout HTML must allow `frame-src` for allowlisted RP origins (page-specific CSP and/or preserve response CSP over global security headers).
- **Config source:** if front-channel URIs live only in env `OIDC_CLIENTS_JSON` while runtime clients also come from D1, ensure fan-out still sees every registered URI (env merge or D1 column).
- **Deploy order:** ship RP front-channel endpoints **before or with** IdP fan-out; missing endpoints just 404 and leave that origin signed in.
- **Consumer serde:** IdP JSON may return `"profile": null`. `#[serde(default)]` handles **missing** fields, **not** null — use null-as-default or `Option` or consumers will 5xx on login callbacks for new accounts.
- **Email gates:** some products require **verified email** for shared-auth login; unverified E2E accounts pass central login but fail RP callback with product-specific errors.
- **Test hygiene:** cookie assertions must use **exact cookie names** (e.g. `session` must not match `zillurl_page_session` via substring).

### Minimal verification

- Discovery advertises front-channel support when implemented.
- Logout HTML lists only allowlisted iframe targets.
- Wrong `iss` on RP front-channel → 4xx without clearing unrelated sessions when `sid` is bound.
- Real browser: login A + B → logout A → refresh B is signed out; silent SSO does not re-auth without central session.

## Abuse, Webhooks, And Errors

- `login`, `signup`, `password reset`, `OTP`, `verification resend`, and `token refresh` endpoints need rate limiting, cooldowns, retry limits, and replay protection.
- Webhooks and async event sources must verify signatures, check timestamp/replay, and use idempotent consumers.
- Security-sensitive operations such as permission changes, failed login, password reset, key account-data changes, and token revoke require `audit log`.
- `audit log` and normal logs must not record passwords, tokens, OTPs, or other sensitive secrets.
- Client errors must be safe and include `error`, `code`, and `trace_id`.
- Use existing `X-Request-ID` when present; otherwise generate UUID v4. Include trace ID in logs and error responses. Production logs should be JSON.
