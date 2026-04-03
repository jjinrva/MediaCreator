# Repo Repair Audit Phase 04 Verification

## Status

PASS

## Checks

1. the base/proxy GLB is still generated and retrievable
2. the export payload names the stage truthfully
3. detail-prep remains separate from refined mesh
4. no UI/API text claims a refined mesh unless a real refined artifact exists
5. preview export remains an explicit, test-backed action in the create-character flow

## Truth contract evidence

Command:

```bash
rg -n "def _detail_level|riggable-base-plus-detail-prep|riggable-base-only|refined_detail_mesh_generated|No refined mesh|Current saved 3D stage" \
  /opt/MediaCreator/apps/api/app/services/reconstruction.py \
  /opt/MediaCreator/apps/api/app/services/exports.py \
  /opt/MediaCreator/apps/web/components/reconstruction-status/ReconstructionStatus.tsx
```

Result:

```text
/opt/MediaCreator/apps/web/components/reconstruction-status/ReconstructionStatus.tsx:24:    case "riggable-base-plus-detail-prep":
/opt/MediaCreator/apps/web/components/reconstruction-status/ReconstructionStatus.tsx:26:    case "riggable-base-only":
/opt/MediaCreator/apps/web/components/reconstruction-status/ReconstructionStatus.tsx:108:        <span>{`Current saved 3D stage: ${describeDetailLevel(detailLevel)}`}</span>
/opt/MediaCreator/apps/api/app/services/exports.py:110:                "detail-prep artifact. No refined mesh is claimed at this stage."
/opt/MediaCreator/apps/api/app/services/exports.py:123:                "artifact. No refined mesh is claimed."
/opt/MediaCreator/apps/api/app/services/exports.py:180:def _detail_level(
/opt/MediaCreator/apps/api/app/services/exports.py:186:        return "riggable-base-plus-detail-prep"
/opt/MediaCreator/apps/api/app/services/exports.py:188:        return "riggable-base-only"
/opt/MediaCreator/apps/api/app/services/exports.py:198:    if detail_level == "riggable-base-plus-detail-prep":
/opt/MediaCreator/apps/api/app/services/exports.py:202:            "No refined mesh artifact is claimed yet."
/opt/MediaCreator/apps/api/app/services/exports.py:204:    if detail_level == "riggable-base-only":
/opt/MediaCreator/apps/api/app/services/exports.py:213:        "current capture set for a detail-prep artifact. No refined mesh is claimed yet."
/opt/MediaCreator/apps/api/app/services/reconstruction.py:115:            "riggable-base-plus-detail-prep" if qualifies_for_detail_prep else "riggable-base-only"
/opt/MediaCreator/apps/api/app/services/reconstruction.py:234:            "refined_detail_mesh_generated": False,
/opt/MediaCreator/apps/api/app/services/reconstruction.py:351:    if payload.detail_level_target == "riggable-base-plus-detail-prep":
```

## API artifact proof

Command:

```bash
cd /opt/MediaCreator/apps/api && .venv/bin/pytest -q \
  tests/test_saved_3d_output_contract.py \
  tests/test_blender_export_api.py \
  tests/test_reconstruction_api.py
```

Result:

```text
....                                                                     [100%]
4 passed in 27.34s
```

Artifact-backed coverage:

- [test_saved_3d_output_contract.py](/opt/MediaCreator/apps/api/tests/test_saved_3d_output_contract.py#L39) proves preview/base GLB stays `not-ready` before queue, becomes `available` only after the worker writes the real artifact, and is retrievable at `/preview.glb`
- [test_saved_3d_output_contract.py](/opt/MediaCreator/apps/api/tests/test_saved_3d_output_contract.py#L154) proves the detail threshold path only reports detail-prep when the body-qualified threshold is met
- [test_reconstruction_api.py](/opt/MediaCreator/apps/api/tests/test_reconstruction_api.py#L42) proves the high-detail path writes a base/proxy GLB plus detail-prep manifest and keeps the job payload truthful
- [test_blender_export_api.py](/opt/MediaCreator/apps/api/tests/test_blender_export_api.py#L44) proves the preview export route writes and serves a real GLB artifact with job metadata

## UI truth proof

Commands:

```bash
cd /opt/MediaCreator/apps/web && ../../infra/bin/pnpm exec vitest run \
  tests/unit/reconstruction-status.test.tsx

cd /opt/MediaCreator/apps/web && ../../infra/bin/pnpm exec vitest run \
  tests/unit/character-import.test.tsx
```

Results:

- `tests/unit/reconstruction-status.test.tsx`: `1 passed`
- `tests/unit/character-import.test.tsx`: `3 passed`

UI-backed coverage:

- [reconstruction-status.test.tsx](/opt/MediaCreator/apps/web/tests/unit/reconstruction-status.test.tsx#L29) proves the high-detail status control keeps the queued job state explicit
- [character-import.test.tsx](/opt/MediaCreator/apps/web/tests/unit/character-import.test.tsx#L74) proves character creation still posts to `/api/v1/exports/characters/{id}/preview`, keeping preview export explicit instead of pretending the artifact already exists

## Repo safety checks

Commands:

```bash
make -C /opt/MediaCreator lint
make -C /opt/MediaCreator typecheck
```

Results:

- `make lint`: passed
- `make typecheck`: passed

## Conclusion

Phase 04 passes. The saved 3D contract is truthful: the repo exposes a real base/proxy GLB, keeps detail-prep separate, does not claim a refined mesh, and keeps preview export tied to an explicit artifact-backed action.
