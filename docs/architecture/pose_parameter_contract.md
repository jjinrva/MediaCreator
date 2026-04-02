# Pose Parameter Contract

Phase 15 freezes the canonical numeric pose catalog for limb posing. These values are the source of truth for later Blender pose-bone mapping, preview refresh, and natural-language pose translation.

## Rules

- Pose values are stored numerically.
- Natural-language phrases are never the canonical stored value.
- Each pose parameter has a stable key, bone name, and axis.
- The UI reads parameter metadata from the backend instead of hard-coding ranges.
- Phase 15 covers left arm, right arm, left leg, and right leg only.

## Catalog

| Key | Label | Group | Bone | Axis | Min | Max | Step | Unit | Default |
|---|---|---|---|---|---:|---:|---:|---|---:|
| `upper_arm_l_pitch_deg` | Left arm raise | `arms` | `upper_arm.L` | `x` | -45 | 90 | 1 | `deg` | 0 |
| `upper_arm_r_pitch_deg` | Right arm raise | `arms` | `upper_arm.R` | `x` | -45 | 90 | 1 | `deg` | 0 |
| `thigh_l_pitch_deg` | Left leg raise | `legs` | `thigh.L` | `x` | -35 | 75 | 1 | `deg` | 0 |
| `thigh_r_pitch_deg` | Right leg raise | `legs` | `thigh.R` | `x` | -35 | 75 | 1 | `deg` | 0 |

## Mapping intent

- `upper_arm_l_pitch_deg` and `upper_arm_r_pitch_deg` map to later Blender upper-arm pose-bone pitch controls.
- `thigh_l_pitch_deg` and `thigh_r_pitch_deg` map to later Blender thigh pose-bone pitch controls.
- Later natural-language edit phases may interpret instructions such as "raise the left arm by 15 degrees", but the persisted truth must still resolve back to these numeric keys.
