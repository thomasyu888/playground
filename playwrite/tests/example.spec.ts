import { test, expect } from '@playwright/test';

test.describe('Login with OAuth', () => {
  test("login, save cookies and localStorage", async ({ page, context }) => {
      // Navigate to application login page
      await page.goto('https://dca.app.sagebionetworks.org');
      const username = process.env.SCHEMATIC_USERNAME;
      const password = process.env.SCHEMATIC_PASSWORD;
      // Log in by clicking the OAuth button
      await page.locator('text=Sign In With Your Email').click();

      // Now we are moving to a 3rd party login page....

      // We are at a new page for login, type email address
      await page.fill('#username', username);
      await page.screenshot({ path: 'oauth-login-success.png' });

      // Fill in the password
      await page.fill('#current-password', password);

      // Click the sign-in button
      await page.click('button:has-text("Sign In")');
      await page.click('button:has-text("Allow")');

      // Now we're back to our own app
      // Wait that the main page has loaded
      await page.waitForURL('https://dca.app.sagebionetworks.org', { timeout: 10000 });

      // Wait for network to be idle, if we save storage too early, needed storage values might not yet be available
      await page.waitForLoadState('networkidle');

      // Save cookies and localstorage to a file, which we can use later in the tests to be logged in automatically
      await context.storageState({ path: 'state.json' });
      await page.screenshot({ path: 'oauth-login-success.png' });
      console.log('Cookies and localStorage should now be saved in state.json file for further cache usage...');
  });
  // Test suite ends
});

// test('has title', async ({ page }) => {
//   await page.goto('https://dca.app.sagebionetworks.org/');

//   // Expect a title "to contain" a substring.
//   await expect(page).toHaveTitle(/Data Curator/);
// });

// test('get started link', async ({ page }) => {
//   await page.goto('https://dca.app.sagebionetworks.org/');

//   // Click the get started link.
//   await page.getByRole('link', { name: 'Get started' }).click();

//   // Expects page to have a heading with the name of Installation.
//   await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();
// });
