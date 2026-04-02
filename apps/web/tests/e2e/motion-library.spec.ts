import fs from "node:fs";

import { expect, test } from "@playwright/test";

const SAMPLE_PHOTO = "/opt/MediaCreator/docs/capture_guides/assets/male_body_front.png";
const API_BASE_URL = "http://10.0.0.102:8010";

test("motion library assigns a local clip to a character and survives reload", async ({
  page,
  request
}) => {
  const photosetResponse = await request.post(`${API_BASE_URL}/api/v1/photosets`, {
    multipart: {
      character_label: "Browser motion character",
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

  await page.goto("/studio/motion");

  await expect(page.getByRole("heading", { name: "Motion library" })).toBeVisible();
  await page.getByLabel("Character").selectOption({ label: "Browser motion character" });
  await page.getByLabel("Motion clip").selectOption({ label: "Walk" });
  await page.getByRole("button", { name: "Assign motion" }).click();

  await expect(page.getByText("Motion assigned to character.")).toBeVisible();
  await expect(page.getByText("Current motion: Walk")).toBeVisible();
  await expect(page.getByText("Selected clip: Walk")).toBeVisible();
  await expect(page.locator(".promptAuditBlock").filter({ hasText: "walk.json" }).first()).toBeVisible();

  await page.reload();

  await page.getByLabel("Character").selectOption({ label: "Browser motion character" });
  await expect(page.getByText("Current motion: Walk")).toBeVisible();
});
