# Patch matrix

| Problem | Evidence basis | Required repair | Phase |
|---|---|---|---|
| Character label must be required but duplicates allowed | user report | require non-empty label; remove duplicate-label blocking | 01, 02, 04 |
| Upload hangs on generic “uploading photoset” | user report + static audit basis | add transfer progress + server scan/classification progress | 01, 02 |
| Clear images are mislabeled blurry | user report | separate LoRA thresholds from body thresholds; reduce false rejects | 01 |
| Body shots with no face are rejected | user report | decouple body eligibility from face visibility | 01 |
| Operator cannot tell whether image is for LoRA or 3D | user report | add explicit buckets and reasons | 01, 02 |
| Thumbnail click does not enlarge image | user report | add preview dialog/lightbox | 02 |
| 3D inputs need cleanup | user question + current stack | write background-removed body derivatives | 03 |
| LoRA inputs may benefit from consistency normalization | user question | add bounded normalization derivative only, no heavy rescue | 03 |
| App must end with saved 3D characters | user requirement | create saved character + saved GLB flow and verify real artifact exists | 04, 06 |
| App must end with LoRA-generated photos | user requirement | train/register LoRA when capability is real and save proof image | 05, 06 |
| Codex must not mislead about completion | user requirement | add hard truth gates and fail/blocker policy | all phases, especially 06 |
