# E2E automation (Playwright) — bootstrap

Feature contract: `../FEATURE_MATRIX.md`  
Agent login notes: `../AUTOMATION_AGENT.md`

## Install (local)

```bash
cd /path/to/baratx
npm init -y
npm i -D @playwright/test
npx playwright install chromium
```

Suggested `e2e/playwright.config.ts`:

```ts
import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e/tests",
  timeout: 60_000,
  use: {
    baseURL: process.env.QA_BASE_URL || "https://barathx.com",
    trace: "on-first-retry",
  },
});
```

## First smoke test sketch

```ts
// e2e/tests/smoke.spec.ts
import { test, expect } from "@playwright/test";

test("login → square suggestions → alerts nav", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel(/email|username/i).fill(process.env.QA_USER_A_EMAIL!);
  await page.getByLabel(/password/i).fill(process.env.QA_USER_A_PASSWORD!);
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/feed/);
  await expect(page.getByText(/Top questions in the Square/i)).toBeVisible();
  await page.locator("[data-coach='nav-alerts']").click();
  await expect(page).toHaveURL(/notifications/);
});
```

Coach selectors for onboarding tips: `[data-coach='compose']`, `nav-square`, `nav-alerts`, `nav-arenas`.

Do not commit real passwords — use CI secrets.
