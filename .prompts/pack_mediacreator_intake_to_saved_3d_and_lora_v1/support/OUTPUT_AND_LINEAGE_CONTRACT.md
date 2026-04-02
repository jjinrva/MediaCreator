# Output and lineage contract

Every downstream artifact must be traceable to a source image set and an execution event.

## Required asset lineage

For each uploaded image, preserve and link:

1. original asset
2. normalized derivative
3. thumbnail derivative
4. background-removed body derivative if body-qualified
5. LoRA-normalized derivative if LoRA-qualified

## Required records for photoset entries

Each photoset entry must persist:

- source file path
- normalized path
- thumbnail path
- body-derivative path if present
- lora-derivative path if present
- classification bucket
- QC metrics
- reason codes
- reason messages

## Required records for saved character creation

A saved character record must persist:

- human-facing label
- stable public ID
- source photoset public ID
- accepted source asset IDs
- separated body asset IDs
- separated LoRA asset IDs
- history event for creation

## Required records for saved 3D output

A saved 3D output must persist:

- character public ID
- output type
- file path
- artifact existence check result
- generating job public ID
- completion timestamp
- history event

## Required records for LoRA artifact and proof image

A saved LoRA path must persist:

- dataset version ID
- trainer capability check result
- model artifact path
- active/current/failed status
- generating job public ID
- proof-image output ID(s)

A proof image must persist:

- prompt used
- prompt expansion result
- active LoRA artifact ID
- image output path
- history event
