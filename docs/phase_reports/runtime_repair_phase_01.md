# Runtime Repair Phase 01

## Status

Implemented. Paired verification not yet run in this report.

## Goal

Remove fixed-machine IP assumptions from runtime code while keeping the web and API bound to `0.0.0.0`.

## Changes made

- added [runtimeApiBase.ts](/opt/MediaCreator/apps/web/lib/runtimeApiBase.ts) so web fetches now use:
  - explicit `NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL` when set
  - browser-derived `${window.location.protocol}//${window.location.hostname}:8010` on the client
  - internal `MEDIACREATOR_INTERNAL_API_BASE_URL` or `http://127.0.0.1:8010` on the server
- updated [.env.example](/opt/MediaCreator/.env.example) to remove fixed single-IP defaults and add:
  - `MEDIACREATOR_ALLOWED_ORIGINS`
  - `MEDIACREATOR_ALLOWED_ORIGIN_REGEX`
  - `MEDIACREATOR_INTERNAL_API_BASE_URL`
  - `MEDIACREATOR_ALLOWED_DEV_ORIGINS`
- updated [main.py](/opt/MediaCreator/apps/api/app/main.py) to use explicit origins plus a LAN-safe origin regex instead of a single fixed origin
- updated [diagnostics.py](/opt/MediaCreator/apps/api/app/services/diagnostics.py) to use the internal API base instead of a fixed LAN IP
- updated [next.config.mjs](/opt/MediaCreator/apps/web/next.config.mjs) to make `allowedDevOrigins` env-driven instead of fixed
- updated [playwright.config.js](/opt/MediaCreator/apps/web/playwright.config.js) to use env/config-driven host defaults instead of one hardcoded LAN address
- replaced hardcoded public-API fallbacks across the web app routes/components with the shared helper
- updated unit tests, Playwright tests, [README.md](/opt/MediaCreator/README.md), and [operator_runbook.md](/opt/MediaCreator/docs/handoff/operator_runbook.md) to match the new contract

## Result

- runtime code no longer depends on one fixed LAN IP
- bind hosts remain `0.0.0.0`
- server-side web fetches default to `http://127.0.0.1:8010`
- browser-side web fetches derive from the current browser hostname unless a public API base env var is set

## Pre-verification evidence

- `rg -n '10\\.0\\.0\\.102' /opt/MediaCreator` only returns expert guidance text, not runtime code
- `make lint` passed
- `make typecheck` passed
