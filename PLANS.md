# PLANS.md

## MediaCreator rebuild roadmap

This rebuild is intentionally sequential. Do not collapse phases.

| Phase | Title | Status |
|---|---|---|
| 01 | Workspace bootstrap and monorepo foundation | PASS |
| 02 | Local infrastructure, containers, and developer entrypoints | PASS |
| 03 | Storage layout, NAS paths, environment contracts | PASS |
| 04 | Database foundation, IDs, lineage, and migrations | PASS |
| 05 | Job orchestration and background worker foundation | PASS |
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
| 17 | Blender runtime, Rigify rig generation, and model attachment | pending |
| 18 | High-detail 3D reconstruction/refinement path | pending |
| 19 | Skin, color, texture, and material fidelity path | pending |
| 20 | LoRA dataset curation, prompt tagging, and training inputs | pending |
| 21 | Real local LoRA training, model registry, and activation | pending |
| 22 | Wardrobe ingestion from photo, AI wardrobe generation, closet catalog | pending |
| 23 | Motion/action library, retargeting, and controlled animation inputs | pending |
| 24 | Controlled video rendering from rigged characters | pending |
| 25 | Tagged image/video generation workspace and external LoRA use | pending |
| 26 | Diagnostics, settings, final verification, polish, and handoff | pending |

## Definition of completion

The pack is complete only when all 26 phases have passed their paired verify steps and the overnight acceptance test passes.
