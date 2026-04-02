# Runtime Repair Phase 01 Verification

## Status

PASS

## Static grep gates

Final command:

```bash
rg -n '10\.0\.0\.102' \
  /opt/MediaCreator/apps \
  /opt/MediaCreator/.env.example \
  /opt/MediaCreator/README.md \
  /opt/MediaCreator/docs \
  /opt/MediaCreator/apps/web/tests || true
```

Final result:
- no matches

Repair note:
- the first grep run caught old fixed-IP text in this phase report under `docs/`
- that text was removed and the grep gate was rerun cleanly

## Runtime gates

Started with the normal scripts:

```bash
/opt/MediaCreator/scripts/run-api.sh
/opt/MediaCreator/scripts/run-web.sh
```

Bind confirmation:

```bash
ss -ltnp | rg ':3000|:8010'
```

Result:
- `0.0.0.0:3000` listening
- `0.0.0.0:8010` listening

LAN-style route checks:

```bash
curl -I http://<current-lan-host>:3000/
curl -I http://<current-lan-host>:3000/studio
curl -I http://<current-lan-host>:3000/studio/characters/new
```

Result:
- all three routes returned `HTTP/1.1 200 OK`

CORS/preflight confirmation:

```bash
curl -i -X OPTIONS http://127.0.0.1:8010/api/v1/photosets \
  -H 'Origin: http://<current-lan-host>:3000' \
  -H 'Access-Control-Request-Method: POST'
```

Result:
- `HTTP/1.1 200 OK`
- `access-control-allow-origin: http://<current-lan-host>:3000`

## Test gates

Targeted helper unit test:

```bash
cd /opt/MediaCreator/apps/web
../../infra/bin/pnpm exec vitest run tests/unit/runtime-api-base.test.ts
```

Result:
- `1` file passed
- `4` tests passed

Playwright smoke:

```bash
cd /opt/MediaCreator/apps/web
MEDIACREATOR_PLAYWRIGHT_HOST=<current-lan-host> \
MEDIACREATOR_PLAYWRIGHT_WEB_BASE_URL=http://<current-lan-host>:3000 \
MEDIACREATOR_PLAYWRIGHT_API_BASE_URL=http://<current-lan-host>:8010 \
../../infra/bin/pnpm exec playwright test \
  tests/e2e/home.spec.ts \
  tests/e2e/studio.spec.ts \
  tests/e2e/character-upload-qc.spec.ts
```

Final result:
- `3 passed`

Repair notes:
- the first Playwright run failed because the local Chromium binary was missing
- repaired with:

```bash
cd /opt/MediaCreator/apps/web
../../infra/bin/pnpm exec playwright install chromium
```

- a follow-up rerun exposed a Next.js `allowedDevOrigins` hostname-format mismatch
- repaired by normalizing `allowedDevOrigins` to hostnames in `next.config.mjs` and passing `MEDIACREATOR_ALLOWED_DEV_ORIGINS=${PLAYWRIGHT_HOST}` in `playwright.config.js`
- the final Playwright rerun passed cleanly

Lint:

```bash
make lint
```

Result:
- passed

Typecheck:

```bash
make typecheck
```

Result:
- passed

## Conclusion

Phase 01 is verified complete:
- no runtime or test/docs contract under the verified paths hardcodes one fixed LAN IP
- API and web still bind to `0.0.0.0`
- the browser-facing route works through the LAN URL
- the browser/API path can post without CORS failure
