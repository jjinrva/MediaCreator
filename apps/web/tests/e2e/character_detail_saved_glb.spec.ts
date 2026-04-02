import { expect, test } from "@playwright/test";

import { startWorkerForPlaywright } from "./helpers/worker";

const SAMPLE_FILES = [
  "/opt/MediaCreator/docs/capture_guides/assets/male_body_front.png",
  "/opt/MediaCreator/docs/capture_guides/assets/male_body_left.png",
  "/opt/MediaCreator/docs/capture_guides/assets/male_head_front.png"
];

test.setTimeout(120000);

test("detail route keeps the saved GLB queued until the artifact exists and survives reload", async ({
  page
}) => {
  let stopWorker: (() => Promise<void>) | null = null;

  try {
    await page.goto("/studio/characters/new");

    await page.getByRole("textbox", { name: "Character label" }).fill("Phase 04 saved GLB");
    await page.getByTestId("photoset-input").setInputFiles(SAMPLE_FILES);
    await page.getByRole("button", { name: "Upload photoset" }).click();

    await expect(page.getByRole("button", { name: "Build base character" })).toBeVisible({
      timeout: 60000
    });
    await expect(page).toHaveURL(/photoset=/, { timeout: 60000 });

    await page.getByRole("button", { name: "Build base character" }).click();

    await expect(page).toHaveURL(/\/studio\/characters\/[0-9a-f-]+$/);
    await expect(page.getByText("Saved 3D preview")).toBeVisible();
    await expect(page.getByText("Framing: full-body")).toBeVisible();
    await expect(page.getByText("No GLB preview is available yet.", { exact: true })).toBeVisible();

    const previewJobCard = page
      .locator(".jobProgressCard")
      .filter({ hasText: "Preview generation job" });
    await expect(previewJobCard).toBeVisible();
    await expect(previewJobCard.locator(".jobProgressHeader .thumbnailBadge")).toHaveText(
      /queued|running/
    );
    await expect(
      page.locator(".keyValueRow").filter({ hasText: "Preview GLB" }).getByText("not-ready")
    ).toBeVisible();

    stopWorker = await startWorkerForPlaywright();

    await expect(page.getByTestId("glb-preview-viewer")).toBeVisible({ timeout: 60000 });
    await expect(
      page.locator(".keyValueRow").filter({ hasText: "Preview GLB" }).getByText("available")
    ).toBeVisible();
    await expect(
      page.locator(".keyValueRow").filter({ hasText: "Export job" }).getByText("completed")
    ).toBeVisible();

    await page.reload();

    await expect(page).toHaveURL(/\/studio\/characters\/[0-9a-f-]+$/);
    await expect(page.getByTestId("glb-preview-viewer")).toBeVisible();
    await expect(page.getByText("Framing: full-body")).toBeVisible();
    await expect(
      page.locator(".keyValueRow").filter({ hasText: "Preview GLB" }).getByText("available")
    ).toBeVisible();
    await expect(
      page.locator(".keyValueRow").filter({ hasText: "Export job" }).getByText("completed")
    ).toBeVisible();
  } finally {
    if (stopWorker) {
      await stopWorker();
    }
  }
});
