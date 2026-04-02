# Phase 01 verify — network and API-origin hardening

## Verify with code and commands

### Static grep gates
- grep for remaining `10.0.0.102` under:
  - `apps/`
  - `.env.example`
  - `README.md`
  - `docs/`
  - `apps/web/tests/`
- allow test fixture text only if explicitly justified and documented; otherwise remove all of it

### Runtime gates
1. Start API and web with the normal scripts.
2. Confirm:
   - API binds to `0.0.0.0`
   - web binds to `0.0.0.0`
3. From a LAN-accessible browser URL, load:
   - `/`
   - `/studio`
   - `/studio/characters/new`
4. Confirm the browser can post to the API without CORS failure.

### Test gates
- targeted unit tests for any new API base helper
- Playwright smoke on `/studio/characters/new`
- lint
- typecheck

## Phase fails if
- any runtime hardcoded `10.0.0.102` remains
- CORS breaks for LAN access
- the web cannot call the API through the new base helper path
