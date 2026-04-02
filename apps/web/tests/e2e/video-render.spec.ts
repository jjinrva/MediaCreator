import fs from "node:fs";

import { expect, test } from "@playwright/test";

const SAMPLE_PHOTO = "/opt/MediaCreator/docs/capture_guides/assets/male_body_front.png";
const API_BASE_URL = "http://10.0.0.102:8010";

test.setTimeout(120000);

test("controlled video rendering creates a replayable jump clip with history", async ({
  page,
  request
}) => {
  const photosetResponse = await request.post(`${API_BASE_URL}/api/v1/photosets`, {
    multipart: {
      character_label: "Browser video character",
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

  const motionResponse = await request.get(`${API_BASE_URL}/api/v1/motion`);
  expect(motionResponse.ok()).toBeTruthy();
  const motionPayload = await motionResponse.json();
  const jumpClip = motionPayload.motion_library.find((clip: { slug: string }) => clip.slug === "jump");
  expect(jumpClip).toBeTruthy();

  const assignResponse = await request.put(
    `${API_BASE_URL}/api/v1/motion/characters/${character.public_id}`,
    {
      data: { motion_public_id: jumpClip.public_id },
      headers: { "content-type": "application/json" }
    }
  );
  expect(assignResponse.ok()).toBeTruthy();

  await page.goto("/studio/video");

  await expect(page.getByRole("heading", { name: "Controlled video rendering" })).toBeVisible();
  await page.getByLabel("Character").selectOption({ label: "Browser video character" });
  await expect(page.getByText("Current motion: Jump")).toBeVisible();

  await page.getByLabel("Width").fill("320");
  await page.getByLabel("Height").fill("320");
  await page.getByLabel("Duration (seconds)").fill("1.1");
  await page.getByRole("button", { name: "Render video" }).click();

  await expect(page.getByText("Controlled video render completed.")).toBeVisible();
  await expect(page.getByTestId("rendered-video")).toBeVisible();
  await expect(
    page.locator(".historyItem strong").filter({ hasText: "video.output_registered" }).first()
  ).toBeVisible();

  await page.reload();
  await page.getByLabel("Character").selectOption({ label: "Browser video character" });

  const renderedVideo = page.getByTestId("rendered-video");
  await expect(renderedVideo).toBeVisible();

  const replayWorked = await renderedVideo.evaluate(async (node) => {
    const video = node as HTMLVideoElement;
    video.muted = true;
    await new Promise<void>((resolve, reject) => {
      if (video.readyState >= 2) {
        resolve();
        return;
      }

      video.addEventListener("loadeddata", () => resolve(), { once: true });
      video.addEventListener("error", () => reject(new Error("video failed to load")), {
        once: true
      });
    });
    const firstPlayWorked = await video.play().then(
      () => true,
      () => false
    );
    if (!firstPlayWorked) {
      return false;
    }
    await new Promise((resolve) => setTimeout(resolve, 300));
    const advancedTime = video.currentTime;
    video.pause();
    video.currentTime = 0;
    await new Promise((resolve) => setTimeout(resolve, 100));
    const secondPlayWorked = await video.play().then(
      () => true,
      () => false
    );
    await new Promise((resolve) => setTimeout(resolve, 150));
    video.pause();
    return advancedTime > 0 && secondPlayWorked && video.readyState >= 2;
  });

  expect(replayWorked).toBeTruthy();
});
