# Phase 01 build — network and API-origin hardening

## Goal
Remove fixed-machine IP assumptions from runtime code while keeping the servers bound to `0.0.0.0`.

## Exact decisions
- Keep `scripts/run-api.sh` and `scripts/run-web.sh` binding to `0.0.0.0`.
- Replace every runtime fallback of `http://10.0.0.102:8010` with a shared API-base helper.
- Use server-side internal API default `http://127.0.0.1:8010`.
- Use browser-side derived API base `${window.location.protocol}//${window.location.hostname}:8010` when no explicit public API base is configured.
- Replace the single-origin CORS setup with explicit env origins plus a LAN-safe regex.
- Remove fixed `allowedDevOrigins: ["10.0.0.102"]` from `apps/web/next.config.mjs` and make it env-driven or remove it entirely if not needed.

## Files to inspect and edit
- `.env.example`
- `README.md`
- `apps/api/app/main.py`
- `apps/web/next.config.mjs`
- every `API_BASE_URL` constant under `apps/web/**`
- `apps/web/playwright.config.js`
- unit/e2e tests that hardcode `10.0.0.102`
- operator docs that hardcode `10.0.0.102`

## Exact steps
1. Create one shared API-base helper module for the web app. Use it everywhere instead of local `const API_BASE_URL = ...` constants.
2. Keep the server-side fetch path internal (`127.0.0.1`) by default.
3. Keep the browser-side fetch path derived from the current browser hostname by default.
4. Update `apps/api/app/main.py` so CORS is not tied to one single hardcoded host.
5. Add env support:
   - `MEDIACREATOR_ALLOWED_ORIGINS`
   - `MEDIACREATOR_ALLOWED_ORIGIN_REGEX`
   - `MEDIACREATOR_INTERNAL_API_BASE_URL`
6. Update `.env.example` to stop teaching `10.0.0.102` as the default contract.
7. Update docs and tests to use env/config-driven values.

## Required code patterns
Use the patterns in:
- `CODE_EXAMPLES.md` section 4
- `CODE_EXAMPLES.md` section 6

## Do not do
- do not bind the servers to any single LAN IP
- do not use `0.0.0.0` as a browser fetch default
- do not leave any runtime fallback to `10.0.0.102`

## Done when
- no runtime code path requires `10.0.0.102`
- the web and API still bind to `0.0.0.0`
- the browser can open the app via a non-10.0.0.102 LAN address and still talk to the API
- tests/docs are aligned with the new contract
