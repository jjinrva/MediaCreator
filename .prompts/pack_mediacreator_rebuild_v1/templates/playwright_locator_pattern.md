
# Playwright locator pattern

Use user-facing locators first.

```ts
await page.getByRole('button', { name: 'Create character' }).click();
await page.getByLabel('Character height').fill('170');
await page.getByRole('tab', { name: 'Body' }).click();
await expect(page.getByText('No characters yet')).toBeVisible();
```
