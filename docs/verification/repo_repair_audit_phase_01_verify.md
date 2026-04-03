# Repo Repair Audit Phase 01 Verification

## Status

PASS

## Checks

1. `PLANS.md` no longer presents clearly unimplemented capabilities as all-`PASS`
2. `README.md` no longer claims `POST /api/v1/photosets` returns immediately
3. `README.md` no longer claims blanket `202` behavior where the route still returns `201`
4. export/reconstruction wording now distinguishes base/proxy GLB, detail-prep artifact, and the absence of a refined mesh claim
5. no new wording in the Phase 01 edit set reintroduced a broader overclaim

## Diff snippets

```diff
-| 05 | Job orchestration and background worker foundation | PASS |
+| 05 | Job orchestration and background worker foundation | PARTIAL |
-| 18 | High-detail 3D reconstruction/refinement path | PASS |
+| 18 | High-detail 3D reconstruction/refinement path | PARTIAL |
-| 25 | Tagged image/video generation workspace and external LoRA use | PASS |
+| 25 | Tagged image/video generation workspace and external LoRA use | PARTIAL |
-| 26 | Diagnostics, settings, final verification, polish, and handoff | PASS |
+| 26 | Diagnostics, settings, final verification, polish, and handoff | PARTIAL |
```

```diff
- photoset upload and QC return immediately
+ `POST /api/v1/photosets` currently returns `201 Created` only after inline upload staging, QC, derivative writes, and photoset persistence complete

- Long-running POST routes return `202 Accepted` and a `job_public_id`.
+ Queued job endpoints return a `job_public_id`.
+ - `POST /api/v1/photosets` returns `201 Created` after inline ingest/QC completes
```

```diff
- "Latest high-detail reconstruction job completed successfully."
+ "Latest high-detail reconstruction job finished the current truthful scope: the riggable base/proxy GLB and, when the capture set qualifies, a detail-prep artifact. No refined mesh is claimed."
```

## Status-code evidence

Command:

```bash
rg -n '@router.post\(\"\", response_model=PhotosetDetailResponse, status_code=201\)' \
  /opt/MediaCreator/apps/api/app/api/routes/photosets.py
```

Result:

```text
/opt/MediaCreator/apps/api/app/api/routes/photosets.py:67:@router.post("", response_model=PhotosetDetailResponse, status_code=201)
```

## Grep evidence for repaired docs/status text

Command:

```bash
rg -n 'Queued job endpoints return a `job_public_id`|Current 3D truth:|Current generation truth:|\| 05 \| .* \| PARTIAL \||\| 18 \| .* \| PARTIAL \||\| 25 \| .* \| PARTIAL \||\| 26 \| .* \| PARTIAL \|' \
  /opt/MediaCreator/PLANS.md \
  /opt/MediaCreator/README.md
```

Result:

```text
/opt/MediaCreator/README.md:135:Current 3D truth:
/opt/MediaCreator/README.md:182:Current generation truth:
/opt/MediaCreator/README.md:191:Queued job endpoints return a `job_public_id`. Follow those jobs with:
/opt/MediaCreator/PLANS.md:13:| 05 | Job orchestration and background worker foundation | PARTIAL |
/opt/MediaCreator/PLANS.md:26:| 18 | High-detail 3D reconstruction/refinement path | PARTIAL |
/opt/MediaCreator/PLANS.md:33:| 25 | Tagged image/video generation workspace and external LoRA use | PARTIAL |
/opt/MediaCreator/PLANS.md:34:| 26 | Diagnostics, settings, final verification, polish, and handoff | PARTIAL |
```

## Test proof

Commands:

```bash
cd /opt/MediaCreator/apps/api && .venv/bin/pytest -q tests/test_exports_api.py
cd /opt/MediaCreator/apps/web && ../../infra/bin/pnpm exec vitest run tests/unit/reconstruction-status.test.tsx
make -C /opt/MediaCreator lint
make -C /opt/MediaCreator typecheck
```

Results:

- `tests/test_exports_api.py`: `1 passed`
- `tests/unit/reconstruction-status.test.tsx`: `1 passed`
- `make lint`: passed
- `make typecheck`: passed

## Conclusion

Phase 01 passes. Repo status, README route behavior, and saved-3D wording now match the current audited implementation more closely, without claiming async ingest or refined-mesh output that does not exist yet.
