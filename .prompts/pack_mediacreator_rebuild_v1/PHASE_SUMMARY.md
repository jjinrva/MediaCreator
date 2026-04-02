# Phase summary

| Phase | Title | Outcome |
|---|---|---|
| 01 | Workspace bootstrap and monorepo foundation | Create a clean MediaCreator monorepo with one frontend app, one backend app, one worker app, shared docs, repeatable commands, and a zero-drift directory contract. |
| 02 | Local infrastructure, containers, and developer entrypoints | Stand up the local runtime foundations for the app: PostgreSQL, a dedicated worker process, the API, the web app, and container/dev scripts that can be run repeatably. |
| 03 | Storage layout, NAS paths, environment contracts | Define the canonical storage layout for models, assets, outputs, exports, and scratch work across NAS and local NVMe without ambiguity. |
| 04 | Database foundation, IDs, lineage, and migrations | Create the base PostgreSQL schema, UUID strategy, Alembic environment, and history/lineage backbone that every later asset type will use. |
| 05 | Job orchestration and background worker foundation | Create the durable job model and worker execution path that later phases will use for photo prep, Blender work, LoRA training, exports, and rendering. |
| 06 | ComfyUI service, model storage, and generation capability checks | Add ComfyUI as the local generation engine and make model storage/versioning live on the NAS with truthful capability reporting. |
| 07 | UI shell, design system, tooltips, and accessibility baseline | Create the MediaCreator shell, navigation, typography, buttons, cards, tabs, tooltips, and the permanent info-icon pattern for every input control. |
| 08 | Guided capture assets and onboarding instructions | Generate and ship the capture guidance that tells the user exactly how to photograph a person for the best LoRA and 3D results, including generic male/female reference assets rendered from Blender. |
| 09 | Photoset ingest screen with drag/drop and thumbnail grid | Create the actual ingest screen where the user drags and drops photos, sees thumbnails, receives guidance, and starts the base-character workflow. |
| 10 | Photo QC and preparation pipeline | Normalize uploaded images, compute objective QC signals, and persist original plus prepared derivatives so later 3D and LoRA phases use the best possible inputs. |
| 11 | Character asset registry, history, and base-character creation | Turn an accepted photoset into a real base character record with asset lineage, a public ID, and a truthful detail page destination. |
| 12 | Character detail route, GLB preview, and export scaffold | Stand up the character detail screen with a truthful section layout and a GLB preview/export scaffold that will be refined in later phases. |
| 13 | Numeric body parameter model and backend contracts | Define the body-parameter system as explicit numeric fields that can later map to natural-language edits and Blender shape keys. |
| 14 | Numeric body editing UI and persistence loop | Make the body parameter model editable in the UI with numeric sliders that persist, reload, and write history correctly. |
| 15 | Numeric limb posing and persistent pose state | Add arm and leg controls as numeric pose parameters that persist, map to the rig later, and survive reloads now. |
| 16 | Face/expression parameter foundation | Lay the numeric groundwork for later facial controls by defining expression parameters and a minimal face-control surface. |
| 17 | Blender runtime, Rigify rig generation, and model attachment | Make Blender the authoritative runtime for rig creation, numeric parameter application, GLB export, and character attachment. |
| 18 | High-detail 3D reconstruction/refinement path | Add the best practical automatic path toward high-detail, full-color, textured human 3D models while keeping the app riggable and controllable. |
| 19 | Skin, color, texture, and material fidelity path | Improve realistic color, skin texture, and material representation so the character model is useful beyond a flat geometry pass. |
| 20 | LoRA dataset curation, prompt tagging, and training inputs | Prepare the best possible training set from the accepted photoset and define exactly how MediaCreator tags and expands character prompts. |
| 21 | Real local LoRA training, model registry, and activation | Train a real local LoRA with AI Toolkit, register the artifact, and make the app able to activate that LoRA for generation. |
| 22 | Wardrobe ingestion from photo, AI wardrobe generation, and closet catalog | Create reusable wardrobe assets from user photos or AI text prompts, preserve materials and color metadata, and expose a closet catalog UI. |
| 23 | Motion/action library, retargeting, and controlled animation inputs | Make MediaCreator control rigged characters with reusable action clips instead of relying on AI video generation to fake motion. |
| 24 | Controlled video rendering from rigged characters | Render simple character-controlled videos such as jumping up and down by applying motion to the rigged model and rendering the result, not by generating AI videos from scratch. |
| 25 | Tagged image/video generation workspace and external LoRA use | Build the standalone generation workspace where users can prompt with `@character`, optionally activate local/external LoRAs, and see the full expanded prompt for now. |
| 26 | Diagnostics, settings, final verification, polish, and handoff | Deliver a polished single-user app with diagnostics, truthful settings, full phase verification, installation docs, and an overnight acceptance report. |
