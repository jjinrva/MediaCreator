import { expect, test } from "@playwright/test";

const SAMPLE_FILES = [
  "/opt/MediaCreator/docs/capture_guides/assets/male_body_front.png",
  "/opt/MediaCreator/docs/capture_guides/assets/female_head_front.png"
];

test("persisted photoset creates one base character and reloads the detail route", async ({
  page
}) => {
  await page.goto("/studio/characters/new");

  await page.getByRole("textbox", { name: "Character label" }).fill("Phase 11 browser character");
  await page.getByTestId("photoset-input").setInputFiles(SAMPLE_FILES);
  await page.getByRole("button", { name: "Upload photoset" }).click();

  await expect(page).toHaveURL(/photoset=/);
  await expect(page.getByRole("button", { name: "Create base character" })).toBeVisible();

  await page.getByRole("button", { name: "Create base character" }).click();

  await expect(page).toHaveURL(/\/studio\/characters\/[0-9a-f-]+$/);
  await expect(page.getByRole("heading", { name: "Phase 11 browser character" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Overview" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Body" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Pose" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Face" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "History" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Outputs" })).toBeVisible();
  await expect(page.getByRole("slider", { name: "Height scale" })).toBeVisible();
  await expect(page.getByRole("slider", { name: "Shoulder width" })).toBeVisible();
  await expect(page.getByRole("button", { name: "More info about Height scale" })).toBeVisible();
  await expect(page.getByRole("button", { name: "More info about Shoulder width" })).toBeVisible();
  await expect(page.getByRole("slider", { name: "Left arm raise" })).toBeVisible();
  await expect(page.getByRole("slider", { name: "Right arm raise" })).toBeVisible();
  await expect(page.getByRole("slider", { name: "Left leg raise" })).toBeVisible();
  await expect(page.getByRole("slider", { name: "Right leg raise" })).toBeVisible();
  await expect(page.getByRole("slider", { name: "Jaw open" })).toBeVisible();
  await expect(page.getByRole("slider", { name: "Smile left" })).toBeVisible();
  await expect(page.getByRole("slider", { name: "Smile right" })).toBeVisible();
  await expect(page.getByRole("slider", { name: "Brow raise" })).toBeVisible();
  await expect(page.getByRole("slider", { name: "Eye openness" })).toBeVisible();
  await expect(page.getByRole("slider", { name: "Neutral blend" })).toBeVisible();

  const shoulderSlider = page.getByRole("slider", { name: "Shoulder width" });
  await shoulderSlider.focus();
  await shoulderSlider.press("ArrowRight");

  await expect(
    page.getByText("Saved Shoulder width at 1.01x. History updated from the API.")
  ).toBeVisible();

  const leftArmSlider = page.getByRole("slider", { name: "Left arm raise" });
  await leftArmSlider.focus();
  await leftArmSlider.press("ArrowRight");
  await expect(
    page.getByText("Saved Left arm raise at 1deg. History updated from the API.")
  ).toBeVisible();

  const rightArmSlider = page.getByRole("slider", { name: "Right arm raise" });
  await rightArmSlider.focus();
  await rightArmSlider.press("ArrowRight");
  await expect(
    page.getByText("Saved Right arm raise at 1deg. History updated from the API.")
  ).toBeVisible();

  const leftLegSlider = page.getByRole("slider", { name: "Left leg raise" });
  await leftLegSlider.focus();
  await leftLegSlider.press("ArrowRight");
  await expect(
    page.getByText("Saved Left leg raise at 1deg. History updated from the API.")
  ).toBeVisible();

  const rightLegSlider = page.getByRole("slider", { name: "Right leg raise" });
  await rightLegSlider.focus();
  await rightLegSlider.press("ArrowRight");
  await expect(
    page.getByText("Saved Right leg raise at 1deg. History updated from the API.")
  ).toBeVisible();

  const jawOpenSlider = page.getByRole("slider", { name: "Jaw open" });
  await jawOpenSlider.focus();
  await jawOpenSlider.press("ArrowRight");
  await expect(
    page.getByText("Saved Jaw open at 0.01x. History updated from the API.")
  ).toBeVisible();

  const smileLeftSlider = page.getByRole("slider", { name: "Smile left" });
  await smileLeftSlider.focus();
  await smileLeftSlider.press("ArrowRight");
  await expect(
    page.getByText("Saved Smile left at 0.01x. History updated from the API.")
  ).toBeVisible();

  await expect(page.getByText("character.created")).toHaveCount(1);
  await expect(page.getByText("body.parameter_updated")).toHaveCount(1);
  await expect(page.getByText("pose.parameter_updated")).toHaveCount(4);
  await expect(page.getByText("face.parameter_updated")).toHaveCount(2);
  await expect(page.getByText("No GLB preview is available yet.", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Generate preview GLB" }).click();
  await expect(page.getByTestId("glb-preview-viewer")).toBeVisible();
  await expect(page.getByText("Texture fidelity: base-textured")).toBeVisible();
  await expect(
    page.locator(".keyValueRow").filter({ hasText: "Preview GLB" }).getByText("available")
  ).toBeVisible();
  await expect(
    page
      .locator(".keyValueRow")
      .filter({ hasText: "Preview texture fidelity" })
      .getByText("base-textured")
  ).toBeVisible();
  await expect(
    page
      .locator(".keyValueRow")
      .filter({ hasText: "Base texture artifact" })
      .getByText("available")
  ).toBeVisible();
  await expect(
    page.locator(".keyValueRow").filter({ hasText: "Export job" }).getByText("completed")
  ).toBeVisible();
  await expect(
    page
      .locator(".keyValueRow")
      .filter({ hasText: "High-detail detail level" })
      .getByText("riggable-base-only")
  ).toBeVisible();
  await expect(
    page
      .locator(".keyValueRow")
      .filter({ hasText: "High-detail strategy" })
      .getByText("smplx-stage1-only")
  ).toBeVisible();
  await expect(
    page
      .locator(".keyValueRow")
      .filter({ hasText: "Detail-prep artifact" })
      .getByText("not-ready")
  ).toBeVisible();
  await page.getByRole("button", { name: "Run high-detail path" }).click();
  await expect(
    page
      .locator(".keyValueRow")
      .filter({ hasText: "Reconstruction job" })
      .getByText("completed")
  ).toBeVisible();
  await expect(page.getByText("job.completed")).toHaveCount(2);
  await expect(page.getByText("export.preview_generated")).toHaveCount(1);
  await expect(page.getByText("reconstruction.completed")).toHaveCount(1);
  await expect(page.getByText("texture.generated")).toHaveCount(1);
  await expect(page.getByRole("heading", { name: "Wardrobe" })).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "Scenes" })).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "Composer" })).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "LoRA Dataset" })).toBeVisible();
  await expect(
    page.locator(".keyValueRow").filter({ hasText: "Prompt handle" }).getByText(/@character_/)
  ).toBeVisible();
  await page.getByRole("button", { name: "Build LoRA dataset" }).click();
  await expect(
    page.locator(".keyValueRow").filter({ hasText: "Dataset status" }).getByText("available")
  ).toBeVisible();
  await expect(page.getByText("lora_dataset.built")).toHaveCount(1);
  await expect(page.getByRole("heading", { name: "LoRA Training" })).toBeVisible();
  await expect(
    page.locator(".keyValueRow").filter({ hasText: "Training capability" }).getByText("unavailable")
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Train LoRA locally" })).toBeDisabled();
  await expect(
    page.getByRole("img", { name: "Accepted reference male_body_front.png" })
  ).toBeVisible();

  await page.reload();

  await expect(page).toHaveURL(/\/studio\/characters\/[0-9a-f-]+$/);
  await expect(page.getByRole("heading", { name: "Phase 11 browser character" })).toBeVisible();
  await expect(page.locator(".fieldStack").filter({ hasText: "Shoulder width" }).getByText("1.01x")).toBeVisible();
  await expect(page.locator(".fieldStack").filter({ hasText: "Left arm raise" }).getByText("1deg")).toBeVisible();
  await expect(page.locator(".fieldStack").filter({ hasText: "Right arm raise" }).getByText("1deg")).toBeVisible();
  await expect(page.locator(".fieldStack").filter({ hasText: "Left leg raise" }).getByText("1deg")).toBeVisible();
  await expect(page.locator(".fieldStack").filter({ hasText: "Right leg raise" }).getByText("1deg")).toBeVisible();
  await expect(page.locator(".fieldStack").filter({ hasText: "Jaw open" }).getByText("0.01x")).toBeVisible();
  await expect(page.locator(".fieldStack").filter({ hasText: "Smile left" }).getByText("0.01x")).toBeVisible();
  await expect(page.getByText("character.created")).toHaveCount(1);
  await expect(page.getByText("body.parameter_updated")).toHaveCount(1);
  await expect(page.getByText("pose.parameter_updated")).toHaveCount(4);
  await expect(page.getByText("face.parameter_updated")).toHaveCount(2);
  await expect(page.getByText("job.completed")).toHaveCount(2);
  await expect(page.getByText("export.preview_generated")).toHaveCount(1);
  await expect(page.getByText("reconstruction.completed")).toHaveCount(1);
  await expect(page.getByText("texture.generated")).toHaveCount(1);
  await expect(page.getByText("lora_dataset.built")).toHaveCount(1);
  await expect(
    page
      .locator(".keyValueRow")
      .filter({ hasText: "High-detail detail level" })
      .getByText("riggable-base-only")
  ).toBeVisible();
  await expect(
    page.locator(".keyValueRow").filter({ hasText: "Dataset status" }).getByText("available")
  ).toBeVisible();
  await expect(
    page.locator(".keyValueRow").filter({ hasText: "Training capability" }).getByText("unavailable")
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Train LoRA locally" })).toBeDisabled();
  await expect(
    page
      .locator(".keyValueRow")
      .filter({ hasText: "Preview texture fidelity" })
      .getByText("base-textured")
  ).toBeVisible();
  await expect(
    page
      .locator(".keyValueRow")
      .filter({ hasText: "Reconstruction job" })
      .getByText("completed")
  ).toBeVisible();
  await expect(page.getByTestId("glb-preview-viewer")).toBeVisible();
});
