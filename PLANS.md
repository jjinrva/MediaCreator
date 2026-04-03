# PLANS.md

## MediaCreator rebuild roadmap

This rebuild is intentionally sequential. Do not collapse phases.

| Phase | Title | Status |
|---|---|---|
| 01 | Workspace bootstrap and monorepo foundation | PASS |
| 02 | Local infrastructure, containers, and developer entrypoints | PASS |
| 03 | Storage layout, NAS paths, environment contracts | PASS |
| 04 | Database foundation, IDs, lineage, and migrations | PASS |
| 05 | Job orchestration and background worker foundation | PARTIAL |
| 06 | ComfyUI service, model storage, and generation capability checks | PASS |
| 07 | UI shell, design system, tooltips, and accessibility baseline | PASS |
| 08 | Guided capture assets and onboarding instructions | PASS |
| 09 | Photoset ingest screen with drag/drop and thumbnail grid | PASS |
| 10 | Photo QC and preparation pipeline | PASS |
| 11 | Character asset registry, history, and base-character creation | PASS |
| 12 | Character detail route, GLB preview, and export scaffold | PASS |
| 13 | Numeric body parameter model and backend contracts | PASS |
| 14 | Numeric body editing UI and persistence loop | PASS |
| 15 | Numeric limb posing and persistent pose state | PASS |
| 16 | Face/expression parameter foundation | PASS |
| 17 | Blender runtime, Rigify rig generation, and model attachment | PASS |
| 18 | High-detail 3D reconstruction/refinement path | PARTIAL |
| 19 | Skin, color, texture, and material fidelity path | PASS |
| 20 | LoRA dataset curation, prompt tagging, and training inputs | PASS |
| 21 | Real local LoRA training, model registry, and activation | PASS |
| 22 | Wardrobe ingestion from photo, AI wardrobe generation, closet catalog | PASS |
| 23 | Motion/action library, retargeting, and controlled animation inputs | PASS |
| 24 | Controlled video rendering from rigged characters | PASS |
| 25 | Tagged image/video generation workspace and external LoRA use | PARTIAL |
| 26 | Diagnostics, settings, final verification, polish, and handoff | PARTIAL |

Audit note as of 2026-04-03:

- Phase 05 is still partial because the worker does not yet execute every queued job type used by the operator flow, including proof-image generation work.
- Phase 18 is still partial because the saved 3D result is currently a riggable base/proxy GLB plus an optional detail-prep artifact, not a refined photo-derived mesh.
- Phase 25 is still partial because generation requests are stored, but proof-image generation is not implemented end-to-end.
- Phase 26 is still partial because the repo truth-reset and follow-on repair pack work are still in progress.

## Definition of completion

The pack is complete only when all 26 phases have passed their paired verify steps and the overnight acceptance test passes.
