# Phase 01 build — truth reset and status alignment

## Goal

Remove false confidence from repo status and output messaging.

## Scope

Repair only truth and status alignment in this phase.

## Required changes

1. Update `PLANS.md`
   - do not leave all 26 phases marked PASS if major gaps remain
   - mark unresolved areas in a way that matches the actual code state
   - do not invent new roadmap structure

2. Update `README.md`
   - remove or correct the claims that photoset upload/QC return immediately
   - remove or correct the blanket claim that all long-running POST routes return `202`
   - distinguish implemented capabilities from future or conditional capabilities

3. Update 3D/export messaging
   - in `apps/api/app/services/exports.py` and any relevant UI text, make the stage wording explicit:
     - proxy/base GLB
     - detail-prep artifact
     - refined mesh only if it exists

4. Update any other obviously false completion language found in the audited file map

## Do not do in this phase

- do not change ingest execution yet
- do not change QC thresholds yet
- do not add new features

## Required outputs

- truthful `PLANS.md`
- truthful `README.md`
- truthful export/status language
- phase report using the verification template

## Failure rules

If you cannot make the wording truthful without understanding the current code path, stop and inspect the file map again.
