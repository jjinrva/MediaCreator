# Face Parameter Contract

Phase 16 freezes the canonical numeric facial-parameter catalog for the first truthful face-control surface. These values are the source of truth for later Blender shape-key mapping, corrective-rig refinement, and natural-language facial edits.

## Rules

- Facial values are stored numerically.
- Natural-language phrases are never the canonical stored value.
- Each facial parameter has a stable key and shape-key-compatible mapping target.
- The UI reads facial metadata from the backend instead of hard-coding ranges.
- Phase 16 covers only the minimal expression scaffold: jaw open, smile left/right, brow raise, eye openness, and neutral blend.

## Catalog

| Key | Label | Group | Shape Key | Min | Max | Step | Unit | Default |
|---|---|---|---|---:|---:|---:|---|---:|
| `jaw_open` | Jaw open | `mouth` | `JawOpen` | 0.00 | 1.00 | 0.01 | `x` | 0.00 |
| `smile_left` | Smile left | `mouth` | `SmileLeft` | 0.00 | 1.00 | 0.01 | `x` | 0.00 |
| `smile_right` | Smile right | `mouth` | `SmileRight` | 0.00 | 1.00 | 0.01 | `x` | 0.00 |
| `brow_raise` | Brow raise | `brows` | `BrowRaise` | 0.00 | 1.00 | 0.01 | `x` | 0.00 |
| `eye_openness` | Eye openness | `eyes` | `EyeOpen` | 0.00 | 1.00 | 0.01 | `x` | 1.00 |
| `neutral_expression_blend` | Neutral blend | `base` | `NeutralExpression` | 0.00 | 1.00 | 0.01 | `x` | 1.00 |

## Mapping intent

- `jaw_open`, `smile_left`, and `smile_right` map directly to later Blender mouth-shape keys.
- `brow_raise` maps to a symmetric brow-lift control that may later split into corrective rig channels.
- `eye_openness` maps to a shared eyelid-open target that may later blend shape keys with corrective rig behavior.
- `neutral_expression_blend` preserves a stable neutral baseline that later expressions can blend against without replacing the numeric source of truth.
