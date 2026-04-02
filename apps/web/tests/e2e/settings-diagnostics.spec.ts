import fs from "node:fs";

import { expect, test } from "@playwright/test";

const SAMPLE_PHOTO = "/opt/MediaCreator/docs/capture_guides/assets/male_body_front.png";
const API_BASE_URL = "http://10.0.0.102:8010";

test("settings and diagnostics pages expose truthful runtime state", async ({ page, request }) => {
  const photosetResponse = await request.post(`${API_BASE_URL}/api/v1/photosets`, {
    multipart: {
      character_label: "Browser diagnostics character",
      photos: {
        buffer: fs.readFileSync(SAMPLE_PHOTO),
        mimeType: "image/png",
        name: "male_body_front.png"
      }
    }
  });
  expect(photosetResponse.ok()).toBeTruthy();
  const photoset = await photosetResponse.json();

  const characterResponse = await request.post(`${API_BASE_URL}/api/v1/characters`, {
    data: { photoset_public_id: photoset.public_id },
    headers: { "content-type": "application/json" }
  });
  expect(characterResponse.ok()).toBeTruthy();

  const settingsResponse = await request.get(`${API_BASE_URL}/api/v1/system/status`);
  expect(settingsResponse.ok()).toBeTruthy();
  const settingsPayload = await settingsResponse.json();

  await page.goto("/studio/settings");

  await expect(page.getByRole("heading", { name: "Runtime settings" })).toBeVisible();
  await expect(
    page.getByText(settingsPayload.storage_paths.nas_root, { exact: true })
  ).toBeVisible();
  await expect(
    page.locator(".runtimePanel").filter({ hasText: "ComfyUI generation" })
  ).toContainText(settingsPayload.generation.status);
  await expect(page.locator(".runtimePanel").filter({ hasText: "Blender runtime" })).toContainText(
    settingsPayload.blender.status
  );

  const diagnosticsResponse = await request.get(`${API_BASE_URL}/api/v1/system/diagnostics`);
  expect(diagnosticsResponse.ok()).toBeTruthy();
  const diagnosticsPayload = await diagnosticsResponse.json();
  const checks = new Map(
    diagnosticsPayload.checks.map((check: { check_id: string; status: string }) => [
      check.check_id,
      check.status
    ])
  );
  const ingestStatus = String(checks.get("ingest_pipeline") ?? "");
  const previewStatus = String(checks.get("glb_preview") ?? "");
  const generationStatus = String(checks.get("generation_workflow_availability") ?? "");

  await page.goto("/studio/diagnostics");

  await expect(page.getByRole("heading", { name: "Diagnostics" })).toBeVisible();
  await expect(
    page.locator(".diagnosticItem").filter({ hasText: "Ingest pipeline" })
  ).toContainText(ingestStatus);
  await expect(page.locator(".diagnosticItem").filter({ hasText: "GLB preview" })).toContainText(
    previewStatus
  );

  await page.getByRole("button", { name: "Run diagnostics again" }).click();

  await expect(
    page.locator(".diagnosticItem").filter({ hasText: "Generation workflow availability" })
  ).toContainText(generationStatus);
});
