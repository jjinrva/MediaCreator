import { expect, test } from "@playwright/test";

test("home page shows the MediaCreator bootstrap placeholder", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "MediaCreator" })).toBeVisible();
  await expect(page.getByText(/Single-user rebuild/i)).toBeVisible();
  await expect(page.getByRole("link", { name: "Open studio shell" })).toBeVisible();
  await expect(page.getByText(/single-user mode/i)).toBeVisible();
  await expect(page.getByText(/accessible tabs, shared UI primitives/i)).toBeVisible();
  await expect(page.getByText(/Generation stays unavailable until ComfyUI/i)).toBeVisible();
  await expect(page.getByText(/claims PostgreSQL-backed jobs/i)).toBeVisible();
});
