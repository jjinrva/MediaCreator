import { expect, test } from "@playwright/test";

const SAMPLE_FILES = [
  "/opt/MediaCreator/docs/capture_guides/assets/male_head_front.png",
  "/opt/MediaCreator/docs/capture_guides/assets/female_head_front.png"
];

test("character ingest uploads to the API and reloads stable QC results", async ({ page }) => {
  await page.goto("/studio/characters/new");

  await page.getByTestId("photoset-input").setInputFiles(SAMPLE_FILES);
  await expect(page.getByRole("img", { name: "Preview of male_head_front.png" })).toBeVisible();
  await expect(page.getByRole("img", { name: "Preview of female_head_front.png" })).toBeVisible();

  await page.getByRole("button", { name: "Upload photoset" }).click();

  await expect(page).toHaveURL(/photoset=/);
  await expect(page.getByText("1. upload photos")).toBeVisible();
  await expect(page.getByText("2. review accepted vs rejected QC")).toBeVisible();
  await expect(page.getByText("3. build base character")).toBeVisible();
  const persistedStatus = page.locator(".statusStrip").filter({ hasText: "pass and warn can build" });
  await expect(persistedStatus.getByText("1 accepted")).toBeVisible();
  await expect(persistedStatus.getByText("1 rejected")).toBeVisible();
  await expect(persistedStatus.getByText("pass and warn can build")).toBeVisible();
  await expect(page.getByRole("button", { name: "Build base character" })).toBeVisible();
  await expect(page.locator(".thumbnailCard").getByText(/QC (pass|warn|fail)/)).toHaveCount(2);
  await expect(page.getByText("Accepted for character use")).toHaveCount(1);
  await expect(page.getByText("Rejected from character use")).toHaveCount(1);
  const rejectedCard = page.locator(".thumbnailCard").filter({
    hasText: "Rejected from character use"
  });
  await expect(rejectedCard.locator("li").first()).toBeVisible();
  await expect(page.getByRole("img", { name: "Prepared thumbnail of male_head_front.png" })).toBeVisible();

  await page.reload();

  await expect(page).toHaveURL(/photoset=/);
  const reloadedPersistedStatus = page.locator(".statusStrip").filter({
    hasText: "pass and warn can build"
  });
  await expect(reloadedPersistedStatus.getByText("1 accepted")).toBeVisible();
  await expect(reloadedPersistedStatus.getByText("1 rejected")).toBeVisible();
  await expect(page.locator(".thumbnailCard").getByText(/QC (pass|warn|fail)/)).toHaveCount(2);
  await expect(page.getByText("Accepted for character use")).toHaveCount(1);
  await expect(page.getByText("Rejected from character use")).toHaveCount(1);
  await expect(
    page.locator(".thumbnailCard").filter({ hasText: "Rejected from character use" }).locator("li").first()
  ).toBeVisible();
  await expect(page.getByRole("img", { name: "Prepared thumbnail of male_head_front.png" })).toBeVisible();
});
