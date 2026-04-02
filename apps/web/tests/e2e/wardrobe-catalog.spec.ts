import { expect, test } from "@playwright/test";

const SAMPLE_PHOTO = "/opt/MediaCreator/docs/capture_guides/assets/male_body_front.png";

test("wardrobe catalog supports photo and prompt creation with reloadable metadata", async ({
  page
}) => {
  const uniqueToken = `${Date.now()}`;
  const photoLabel = `Browser linen shirt ${uniqueToken}`;
  const promptLabel = `Browser leather jacket ${uniqueToken}`;

  await page.goto("/studio/wardrobe");

  await expect(page.getByRole("heading", { name: "Wardrobe catalog" })).toBeVisible();
  await expect(
    page.locator(".keyValueRow").filter({ hasText: "AI wardrobe capability" }).getByText("unavailable")
  ).toBeVisible();

  await page.getByLabel("Source photo").setInputFiles(SAMPLE_PHOTO);
  await page.locator("#wardrobe-photo-label").fill(photoLabel);
  await page.locator("#wardrobe-photo-type").fill("shirt");
  await page.locator("#wardrobe-photo-material").fill("linen");
  await page.locator("#wardrobe-photo-color").fill("white");
  await page.getByRole("button", { name: "Create wardrobe from photo" }).click();

  await expect(page.getByText("Wardrobe item created from photo.")).toBeVisible();
  const photoCard = page.locator("article.thumbnailCard").filter({ hasText: photoLabel });
  await expect(photoCard).toBeVisible();
  await expect(photoCard).toContainText("Material: linen");
  await expect(photoCard).toContainText("Base color: white");
  await expect(photoCard).toContainText("Created via: photo");

  await page.locator("#wardrobe-prompt-label").fill(promptLabel);
  await page.locator("#wardrobe-prompt-type").fill("jacket");
  await page.locator("#wardrobe-prompt-material").fill("leather");
  await page.locator("#wardrobe-prompt-color").fill("brown");
  await page.getByLabel("Prompt text").fill("brown leather jacket with matte finish");
  await page.getByRole("button", { name: "Create wardrobe from prompt" }).click();

  await expect(page.getByText("Prompt-backed wardrobe item created.")).toBeVisible();
  const promptCard = page.locator("article.thumbnailCard").filter({ hasText: promptLabel });
  await expect(promptCard).toBeVisible();
  await expect(promptCard).toContainText("Material: leather");
  await expect(promptCard).toContainText("Base color: brown");
  await expect(promptCard).toContainText("Created via: ai-prompt");
  await expect(promptCard).toContainText("brown leather jacket with matte finish");

  await page.reload();

  await expect(photoCard).toBeVisible();
  await expect(photoCard).toContainText("Material: linen");
  await expect(photoCard).toContainText("Created via: photo");
  await expect(promptCard).toBeVisible();
  await expect(promptCard).toContainText("Material: leather");
  await expect(promptCard).toContainText("Created via: ai-prompt");
});
