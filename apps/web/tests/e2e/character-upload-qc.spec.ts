import { expect, test } from "@playwright/test";

const SAMPLE_FILES = [
  "/opt/MediaCreator/docs/capture_guides/assets/male_body_front.png",
  "/opt/MediaCreator/docs/capture_guides/assets/female_head_front.png"
];

test("character ingest uploads to the API and reloads stable QC results", async ({ page }) => {
  await page.goto("/studio/characters/new");

  await page.getByTestId("photoset-input").setInputFiles(SAMPLE_FILES);
  await expect(page.getByRole("img", { name: "Preview of male_body_front.png" })).toBeVisible();
  await expect(page.getByRole("img", { name: "Preview of female_head_front.png" })).toBeVisible();

  await page.getByRole("button", { name: "Upload photoset" }).click();

  await expect(page).toHaveURL(/photoset=/);
  await expect(page.getByText(/QC (pass|warn|fail)/)).toHaveCount(2);
  await expect(page.getByRole("img", { name: "Prepared thumbnail of male_body_front.png" })).toBeVisible();

  await page.reload();

  await expect(page).toHaveURL(/photoset=/);
  await expect(page.getByText(/QC (pass|warn|fail)/)).toHaveCount(2);
  await expect(page.getByRole("img", { name: "Prepared thumbnail of male_body_front.png" })).toBeVisible();
});
