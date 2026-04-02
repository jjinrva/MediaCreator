# Body Parameter Contract

Phase 13 freezes the canonical numeric body parameter catalog. These values are the source of truth for later UI editing, Blender shape-key mapping, and natural-language translation.

## Rules

- Body values are stored numerically.
- Natural-language phrases are never the canonical stored value.
- Each parameter has a stable key that later phases must keep.
- The UI reads parameter metadata from the backend instead of hard-coding ranges.

## Catalog

| Key | Label | Group | Min | Max | Step | Unit | Default |
|---|---|---|---:|---:|---:|---|---:|
| `height_scale` | Height scale | `overall` | 0.85 | 1.15 | 0.01 | `x` | 1.00 |
| `shoulder_width` | Shoulder width | `torso` | 0.80 | 1.20 | 0.01 | `x` | 1.00 |
| `chest_volume` | Chest volume | `torso` | 0.75 | 1.25 | 0.01 | `x` | 1.00 |
| `waist_width` | Waist width | `torso` | 0.75 | 1.25 | 0.01 | `x` | 1.00 |
| `hip_width` | Hip width | `torso` | 0.75 | 1.25 | 0.01 | `x` | 1.00 |
| `upper_arm_volume` | Upper-arm volume | `arms` | 0.75 | 1.25 | 0.01 | `x` | 1.00 |
| `thigh_volume` | Thigh volume | `legs` | 0.75 | 1.25 | 0.01 | `x` | 1.00 |
| `calf_volume` | Calf volume | `legs` | 0.75 | 1.25 | 0.01 | `x` | 1.00 |

## Mapping intent

- `height_scale` maps to the later Blender body-height control.
- `shoulder_width`, `chest_volume`, `waist_width`, and `hip_width` map to torso-oriented shape-key groups.
- `upper_arm_volume`, `thigh_volume`, and `calf_volume` map to limb fullness targets.

Later natural-language edit phases may interpret prompts such as "broader shoulders" or "narrower waist", but the resulting persisted truth must still resolve back to these numeric keys.
