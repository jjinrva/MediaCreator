# Output truth contract

## Required status vocabulary

Use explicit stage language. Do not collapse these into a generic “ready” state.

### Intake
- `uploading`
- `queued`
- `ingesting`
- `classifying`
- `completed`
- `failed`
- `canceled`

### 3D
- `not-started`
- `proxy-glb-available`
- `detail-prep-available`
- `refined-mesh-available`

### LoRA
- `unavailable`
- `staged`
- `queued`
- `training`
- `current`
- `failed`

### Proof image
- `not-requested`
- `blocked`
- `queued`
- `generated`
- `failed`

## Forbidden shortcuts

Do not present these as equivalent:

- proxy GLB == refined mesh
- detail-prep == reconstructed mesh
- stored generation-request == generated proof image
- runtime capability check == produced artifact

## Required evidence for success labels

### “saved 3D character”
Only allowed if:
- character record exists
- preview/base GLB exists on disk
- storage object exists
- exported status payload resolves it

### “refined 3D character”
Only allowed if:
- refined mesh artifact exists on disk
- storage object exists
- exported status payload resolves it
- the artifact is not just the proxy/base GLB

### “saved proof image”
Only allowed if:
- image file exists on disk
- storage object exists
- generation request lineage points to it
- the file was produced by a real generation execution path
