# Motion Contract

Phase 23 introduces the first reusable rig-driven motion library.

## Motion assets

- Each motion clip is stored as a reusable `motion-clip` asset.
- The clip metadata includes:
  - `name`
  - `duration_seconds`
  - `source`
  - `compatible_rig_class`
  - `action_payload_path`
- The first local library is seeded from tracked action payload references for:
  - idle
  - walk
  - jump
  - sit
  - turn

## Assignment rules

- Motion is assigned to a character through `character.motion_assigned` history events.
- The character keeps the latest assigned motion as the current motion reference.
- Motion assignment is rig-driven and explicit; the app does not substitute AI-only video generation for animation control.

## Preview contract

- The Blender preview job payload now carries the selected motion reference through:
  - `motion_clip_name`
  - `motion_duration_seconds`
  - `motion_payload_path`
- Phase 23 does not claim the preview GLB is animated yet. It only guarantees that the chosen motion reference reaches the preview job payload truthfully.

## External imports

- External humanoid animation imports remain optional.
- Mixamo is documented as the recommended future import source, but Adobe login is not a hard dependency for the app to function.
