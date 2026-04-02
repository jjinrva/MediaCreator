# MediaCreator repository contract

## Purpose

This contract freezes the Phase 01 folder layout so later phases extend one implementation instead of creating parallel trees.

## Allowed top-level directories

- `.prompts` — rebuild pack instructions and per-phase source files
- `apps` — runtime applications only
- `packages` — shared TypeScript workspace packages only
- `docs` — architecture notes, capture guides, phase reports, and verification reports
- `experts` — pack expert guidance
- `infra` — local toolchain bootstrap and future infrastructure support files
- `scripts` — canonical shell entrypoints used by `make`
- `storage` — tracked storage placeholder only
- `workflows` — reserved for future workflow definitions

## Root applications

- `apps/web` is the only frontend app
- `apps/api` is the only HTTP API app
- `apps/worker` is the only worker app

No duplicate app roots may be created elsewhere in the repository.

## Documentation contract

- `docs/phase_reports` holds one phase report per phase
- `docs/verification` holds one verify report per phase
- `docs/architecture` holds durable architecture documents
- `docs/capture_guides` is reserved for capture guidance assets from later phases

## Storage contract

- `storage/.gitkeep` is the only tracked file under `storage` in Phase 01
- runtime assets, exports, and heavy binaries must not be committed into the repo

## Runtime truthfulness

- the web home page may describe only bootstrap-ready behavior
- the API may expose only truthful health/bootstrap endpoints
- the worker may report bootstrap-only status until the jobs phase lands

## Naming contract

Use `MediaCreator` everywhere. Do not introduce `AutoCharacter` names in root files, app code, routes, scripts, or docs.
