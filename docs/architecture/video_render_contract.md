# Controlled Video Render Contract

Phase 24 adds one truthful controlled-video path:

- `GET /api/v1/video` returns the current render policy, every known character, the assigned motion clip, the latest render job state, the latest persisted MP4 asset, and the character-scoped video history trail.
- `POST /api/v1/video/characters/{character_public_id}/render` queues exactly one `character-motion-video-render` job, runs the worker path, and refreshes the same screen contract.
- `GET /api/v1/video/assets/{video_asset_public_id}.mp4` serves the persisted MP4 if the output file exists.

## Lineage

- Each render creates one `character-motion-video` asset.
- The video asset uses `parent_asset_id = <character asset id>` so the clip stays attached to the character.
- The video asset uses `source_asset_id = <motion asset id>` so the clip stays attached to the selected action asset.
- The MP4 storage object uses `source_asset_id = <video asset id>`.

## History

The character history records:

- `video.render_requested`
- `video.render_completed`
- `video.output_registered`

The video asset records:

- `video.asset_created`
- `video.output_registered`
- `video.render_failed` if Blender does not produce the output

## Runtime

- Blender 4.5 LTS runs in background mode.
- The render script is `workflows/blender/render_actions.py`.
- The first scene is intentionally simple: one rigged proxy character, one camera, one floor plane, basic lighting, and MP4 output.
- No AI text-to-video path is used in this phase.
