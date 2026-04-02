import { expect, test } from "@playwright/test";

test("studio route exposes the shell, tabs, and labeled tooltip triggers", async ({ page }) => {
  await page.goto("/studio");

  await expect(page.getByRole("heading", { name: "Studio shell" })).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Studio navigation" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Capture guide" })).toBeVisible();
  await expect(page.getByRole("link", { name: "New character" })).toBeVisible();
  await expect(page.getByRole("tab", { name: "Shell controls" })).toBeVisible();
  await expect(page.getByRole("slider", { name: "Layout focus" })).toBeVisible();
  await expect(page.getByRole("textbox", { name: "Workspace label" })).toBeVisible();
  await expect(page.getByRole("button", { name: "More info about Layout focus" })).toBeVisible();
  await expect(page.getByRole("button", { name: "More info about Workspace label" })).toBeVisible();
});
