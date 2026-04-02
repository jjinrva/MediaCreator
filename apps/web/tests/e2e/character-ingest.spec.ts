import fs from "node:fs";
import path from "node:path";

import { expect, test, type Page } from "@playwright/test";

type DropFilePayload = {
  bytes: number[];
  mimeType: string;
  name: string;
};

const SAMPLE_FILES = [
  "/opt/MediaCreator/docs/capture_guides/assets/male_body_front.png",
  "/opt/MediaCreator/docs/capture_guides/assets/female_head_front.png"
];

async function createDropDataTransfer(page: Page, filePaths: string[]) {
  const payload = filePaths.map((filePath) => ({
    bytes: Array.from(fs.readFileSync(filePath)),
    mimeType: "image/png",
    name: path.basename(filePath)
  }));

  return page.evaluateHandle((files: DropFilePayload[]) => {
    const dataTransfer = new DataTransfer();

    files.forEach((file: DropFilePayload) => {
      const bytes = Uint8Array.from(file.bytes);
      dataTransfer.items.add(new File([bytes], file.name, { type: file.mimeType }));
    });

    return dataTransfer;
  }, payload);
}

test("character ingest route supports drag-and-drop, thumbnails, removal, and truthful empty state", async ({
  page
}) => {
  await page.goto("/studio/characters/new");

  const dataTransfer = await createDropDataTransfer(page, SAMPLE_FILES);

  await page.getByTestId("ingest-dropzone").dispatchEvent("dragenter", { dataTransfer });
  await page.getByTestId("ingest-dropzone").dispatchEvent("dragover", { dataTransfer });
  await page.getByTestId("ingest-dropzone").dispatchEvent("drop", { dataTransfer });

  await expect(page.getByRole("img", { name: "Preview of male_body_front.png" })).toBeVisible();
  await expect(page.getByRole("img", { name: "Preview of female_head_front.png" })).toBeVisible();
  await expect(page.locator("[data-testid='thumbnail-card'] .thumbnailBadge")).toHaveCount(2);

  await page.getByRole("button", { name: "Remove female_head_front.png" }).click();

  await expect(page.getByRole("img", { name: "Preview of male_body_front.png" })).toBeVisible();
  await expect(page.getByRole("img", { name: "Preview of female_head_front.png" })).toHaveCount(0);
  await expect(page.getByText(/No previously created characters are shown here/i)).toBeVisible();
  await expect(page.getByText("Character 001")).toHaveCount(0);
});
