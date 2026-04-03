# Phase 04 build — saved 3D output truth and contract repairs

## Goal

Make the saved 3D path truthful.

## Required repairs

1. Distinguish output stages explicitly
   - proxy/base GLB available
   - detail-prep available
   - refined mesh available only if a real refined mesh exists

2. Do not let the UI/API present proxy/base GLB as refined 3D

3. Preserve the existing preview export path
   - keep it working
   - keep artifact checks
   - do not regress the saved base GLB contract

4. If refined mesh is not implemented, say so plainly
   - do not fake a refined stage
   - do not mark the roadmap or output payload as if that stage is complete

5. Verify whether character creation should auto-queue preview export
   - if kept, make it truthful and test-backed
   - if not kept, make the required operator action explicit

## Required tests

- saved character can still reach proxy/base GLB available state
- detail-prep is separate from refined mesh
- refined mesh stays absent until actually implemented
