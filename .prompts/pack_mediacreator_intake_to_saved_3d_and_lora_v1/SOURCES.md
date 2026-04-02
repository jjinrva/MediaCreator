# SOURCES.md

This pack uses the following primary references. Use these source IDs inside the phase files.

## Frontend and testing

- **S01** — Next.js App Router docs: https://nextjs.org/docs/app
- **S02** — react-dropzone docs/project: https://github.com/react-dropzone/react-dropzone
- **S03** — Playwright locator best practices: https://playwright.dev/docs/locators
- **S04** — `<model-viewer>` staging/cameras/updateFraming docs: https://modelviewer.dev/examples/stagingandcameras/

## Backend and data

- **S05** — FastAPI request files / `UploadFile`: https://fastapi.tiangolo.com/tutorial/request-files/
- **S06** — FastAPI testing / `TestClient`: https://fastapi.tiangolo.com/tutorial/testing/
- **S07** — SQLAlchemy ORM declarative mapping: https://docs.sqlalchemy.org/en/20/orm/declarative_mapping.html

## QC and preprocessing

- **S08** — MediaPipe Face Landmarker for Python: https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker/python
- **S09** — MediaPipe Pose Landmarker for Python: https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker/python
- **S10** — Pillow docs: https://pillow.readthedocs.io/
- **S11** — OpenCV official docs: https://docs.opencv.org/

## 3D and generation

- **S12** — Blender glTF 2.0 exporter manual: https://docs.blender.org/manual/en/4.1/addons/import_export/scene_gltf2.html
- **S13** — InstantMesh official README / background-removal note: https://github.com/TencentARC/InstantMesh
- **S14** — AI Toolkit by Ostris: https://github.com/ostris/ai-toolkit

## Source-use decisions for this pack

- Use `S08` and `S09` for person, face, and body evidence rules.
- Use `S10` and `S11` for derivative generation and conservative image normalization.
- Use `S13` to justify writing background-removed body derivatives for image-to-3D inputs.
- Use `S14` for the LoRA dataset/training format and truthful capability reporting.
- Do not invent alternate tools if the existing repo stack already covers the requirement.
