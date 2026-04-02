
# STACK_DECISIONS.md

This document records the exact stack decisions for the MediaCreator rebuild. Codex must follow these decisions unless a blocker is written and approved.

## Runtime baselines

- **Node.js**: 22 LTS
- **Python**: 3.12
- **Database**: PostgreSQL 16
- **3D runtime / DCC**: Blender 4.5 LTS
- **OS assumption**: Linux host with NVIDIA GPU, local NVMe plus 10G NAS access

The chosen Node line is 22 LTS, which is in the production-ready LTS line according to the Node release policy and current release listings. Python 3.12 is chosen for stable ecosystem support. Blender 4.5 LTS is chosen for a stable long-lived Blender API and bugfix window through 2027. See S25, S26, S44, S45, and S20.

## Frontend

Chosen path:
- Next.js App Router
- TypeScript
- React server/client components as appropriate
- CSS Modules or scoped CSS next to components
- Radix Slider + Radix Tooltip
- react-dropzone
- Playwright
- Vitest for unit tests

Rejected for this rebuild:
- Pages Router
- Remix
- raw three.js rewrite
- a second web framework
- replacing the existing fetch pattern with Axios/TanStack Query during the rebuild

Reason:
The App Router route model and dynamic segments fit the required `/studio/.../[publicId]` structure, while Radix and react-dropzone solve the exact UI primitives we need with accessible, maintained components. See S01–S07.

## Backend

Chosen path:
- FastAPI
- Pydantic v2
- SQLAlchemy 2
- Alembic
- psycopg v3
- database-backed jobs with a dedicated worker
- pytest + FastAPI TestClient

Rejected:
- Django
- Flask + ad-hoc extensions
- Celery as the first job system
- browser-only state for character edits

Reason:
FastAPI’s modular routing model matches the domain-based service layout we want, and the database-backed job queue keeps the source of truth in PostgreSQL while avoiding Celery complexity for a single-user first build. See S08–S20.

## Storage

Chosen path:
- NAS-backed canonical storage for models, checkpoints, LoRAs, long-lived assets, and exports
- local NVMe scratch for temp files, active job working sets, and short-lived staging
- every file gets DB metadata, ownership-ready lineage, and history records

Rejected:
- storing large binaries in the database
- local-only storage for canonical assets

## 3D and character modeling

Chosen path:
- Blender 4.5 LTS as the authoritative DCC/runtime
- Rigify for rig generation
- glTF/GLB as the web export format
- `<model-viewer>` for web preview
- numeric body parameters and numeric pose parameters designed to map to Blender shape keys and pose bones
- detailed reconstruction path built in stages:
  1. guided capture + QC
  2. base parametric body fit
  3. rig attachment
  4. detail refinement
  5. texture/material projection

Reason:
Blender already gives us rigging, rig generation, numeric shape/pose hooks, and glTF export with animation, skinning, textures, and shape keys. `<model-viewer>` already solves web preview needs. See S25–S31.

## High-detail reconstruction

Chosen path:
- use a two-layer strategy
  1. parametric human model fitting with SMPL-X family for a riggable base
  2. high-detail refinement path driven by capture quality plus COLMAP-backed reconstruction/material projection in later phases

Reason:
A riggable character must exist before high-detail reconstruction becomes useful in the app. SMPL-X/SMPLify-X/SMPLest-X provide an expressive body representation and fitting ecosystem, while COLMAP provides a well-documented SfM/MVS path for geometric detail from multi-view capture. See S32–S36.

## Generation and LoRA

Chosen path:
- ComfyUI for image-generation orchestration
- AI Toolkit for local LoRA training
- Civitai public REST integration for discovery/import later in the rebuild
- all heavy models and checkpoints on NAS-backed storage

Reason:
ComfyUI is the practical local workflow engine for generation, and AI Toolkit explicitly supports consumer-grade GPU LoRA training workflows, including 24 GB class cards. See S37–S42.

## Motion

Chosen path:
- Blender actions are the canonical motion asset type
- the app stores motion clips and retargetable action metadata
- the first motion library is locally authored / imported and rig-attached
- Mixamo is treated as an optional external source for humanoid motion clips, not as an automated dependency

Reason:
The app requirement is to control the character rig, not to fake motion with one-shot AI video generation. Blender actions align with that goal. Mixamo is useful, free, and humanoid-focused, but it requires Adobe login and is not the core dependency path. See S43.

## Verification

Chosen path:
- unit tests for components and services
- API integration tests for domain routes
- Playwright for end-to-end user-visible behavior
- screenshot and file-output checks where useful
- phase reports and verify reports after every phase

This pack is build-first but verify-gated. No phase is complete until its verify document passes.
