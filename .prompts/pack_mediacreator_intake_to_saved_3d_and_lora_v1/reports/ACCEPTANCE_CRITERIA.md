# Acceptance criteria

The pack is PASS only if every item below is true.

## Intake and labeling

1. The intake screen requires a non-empty character label before upload can start.
2. The label may duplicate an existing label. No uniqueness error may block the operator.
3. The label is trimmed and stored consistently in the photoset and character records.

## Progress truth

4. The UI shows upload transfer progress before the network request completes.
5. After transfer finishes, the UI shows server-side ingest/QC stage progress with a live stage name.
6. The UI shows processed count versus total count during scan/classification.
7. The UI never stays on a generic permanent “uploading photoset” message without further state detail.

## Thumbnail review UX

8. Every thumbnail is clickable.
9. Clicking a thumbnail opens a larger preview dialog or lightbox.
10. The enlarged preview shows the image bucket, QC reasons, and key signals.

## Classification and acceptance

11. Every image is first evaluated for human presence.
12. If no person is detected, the image is rejected with an explicit reason.
13. If a person is detected and the image passes LoRA-specific checks, it is eligible for LoRA.
14. If a person is detected and the image passes body-specific checks, it is eligible for body modeling.
15. If both sets of checks pass, the image is tagged `both`.
16. A body shot without a visible face may still be accepted into `body_only` if body evidence is sufficient.
17. A face-centric or portrait image may be `lora_only` if body evidence is insufficient.
18. Rejected images remain visible with reasons.
19. Accepted counts must be visible for:
    - LoRA
    - body
    - both
    - rejected

## Preprocessing

20. Original files are preserved.
21. Normalized derivatives are written for downstream use.
22. Body-qualified inputs get a background-removed derivative or alpha-masked derivative.
23. LoRA-qualified inputs get conservative normalization only. The system does not aggressively “rescue” bad images with heavy edits.

## Saved character and outputs

24. Character creation uses accepted assets only.
25. A saved character record is created with lineage to the source photoset.
26. If the body bucket has enough accepted inputs, a saved 3D output file is written and registered.
27. The character detail page shows a real GLB preview backed by a real artifact.
28. The detail page keeps full-body framing.

## LoRA and proof image

29. The LoRA dataset is built only from `lora_only` and `both` images.
30. AI Toolkit capability is reported truthfully.
31. If AI Toolkit is operational, a real LoRA artifact is trained or updated and registered.
32. If AI Toolkit is operational, at least one proof image is generated from the resulting LoRA and saved.

## Anti-misleading rules

33. No route or screen may show `complete`, `generated`, or `ready` unless:
    - the artifact file exists, and
    - the corresponding registry/output/database record exists.
34. Verification reports must list exact commands and exact results.
35. Any failed verification must leave the phase in FAIL or BLOCKED, not PASS.
