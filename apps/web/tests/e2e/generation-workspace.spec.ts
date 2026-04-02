import fs from "node:fs";

import { expect, test } from "@playwright/test";

const SAMPLE_PHOTO = "/opt/MediaCreator/docs/capture_guides/assets/male_body_front.png";
const API_BASE_URL = "http://10.0.0.102:8010";

test("generation workspace shows visible prompt expansion and persists stored requests", async ({
  page,
  request
}) => {
  const photosetResponse = await request.post(`${API_BASE_URL}/api/v1/photosets`, {
    multipart: {
      character_label: "Browser prompt character",
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
  const character = await characterResponse.json();

  const workspaceResponse = await request.get(`${API_BASE_URL}/api/v1/generation`);
  expect(workspaceResponse.ok()).toBeTruthy();
  const workspace = await workspaceResponse.json();
  const recipe = workspace.characters.find(
    (item: { public_id: string }) => item.public_id === character.public_id
  );
  expect(recipe).toBeTruthy();

  await page.goto("/studio/generate");

  await expect(page.getByRole("heading", { name: "Generation workspace" })).toBeVisible();
  await page
    .getByRole("textbox", { name: "Prompt" })
    .fill(`${recipe.prompt_handle} standing on a bridge`);
  await expect(page.getByTestId("expanded-prompt-preview")).toContainText(
    "Browser prompt character"
  );
  await expect(page.getByTestId("expanded-prompt-preview")).toContainText(
    "standing on a bridge"
  );

  await page.getByRole("button", { name: "Store generation request" }).click();

  await expect(page.getByText("Generation request stored.")).toBeVisible();
  await expect(
    page.locator(".historyItem").filter({
      hasText: `${recipe.prompt_handle} standing on a bridge`
    })
  ).toBeVisible();

  await page.reload();

  await expect(
    page.locator(".historyItem").filter({
      hasText: `${recipe.prompt_handle} standing on a bridge`
    })
  ).toBeVisible();
});
