import { expect, test } from "@playwright/test";

test("capture guide route shows concrete instructions and serves the rendered PNG assets", async ({
  page,
  request
}) => {
  await page.goto("/studio/capture-guide");

  await expect(page.getByRole("heading", { name: "Capture guide" })).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Studio navigation" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Capture guide" })).toHaveAttribute("aria-current", "page");
  await expect(page.getByText(/20-30 sharp photos/i)).toBeVisible();
  await expect(page.getByText(/60-120\+ sharp photos/i)).toBeVisible();
  await expect(page.getByText(/60-70% overlap/i)).toBeVisible();
  await expect(
    page.getByRole("img", { name: /^Male mannequin full-body front reference$/ })
  ).toBeVisible();

  const assetResponse = await request.get("/studio/capture-guide/assets/male_body_front.png");
  expect(assetResponse.ok()).toBeTruthy();
  expect(assetResponse.headers()["content-type"]).toContain("image/png");
});
