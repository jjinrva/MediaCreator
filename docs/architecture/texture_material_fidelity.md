# Texture and Material Fidelity

Phase 19 adds the first truthful texture/material path for MediaCreator.

## Current fidelity levels

The app reports one of these states:

- `untextured` — no persisted texture artifact exists yet
- `base-textured` — a base-color texture derived from prepared capture photos exists and is carried into preview GLB export
- `refined-textured` — reserved for later phases that produce a higher-fidelity texture set

Phase 19 guarantees only the `base-textured` path.

## Current texture pipeline

The texture pipeline starts from prepared photos, not raw uploads.

Current behavior:

- read the normalized prepared images for the character source photoset
- synthesize a base-color texture atlas from those prepared images
- persist the atlas as a separate storage object from the GLB geometry
- write `texture.generated` on first creation or `texture.updated` on regeneration
- pass the atlas path into the Blender GLB export so the preview carries embedded texture data

This is a truthful full-color output path, not a cinema-grade skin/material solver.

## Geometry versus texture separation

Geometry and texture artifacts stay separate on purpose:

- riggable base GLB remains a geometry/export artifact
- detail-prep manifests remain reconstruction artifacts
- base-color and future refined texture sets remain texture artifacts

That separation is required for later wardrobe, material overrides, and higher-end render packaging.

## Material truthfulness

Phase 19 does not claim subsurface skin shading, advanced displacement, or a refined texture solve.

It does claim:

- a persisted base-color texture artifact
- a GLB export that includes texture data when generated after the texture pipeline runs
- UI/API metadata that states whether the current output is untextured, base-textured, or refined-textured
