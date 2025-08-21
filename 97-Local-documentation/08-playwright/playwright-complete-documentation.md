# Playwright Complete Documentation

## Table of Contents

1. [Getting Started & Installation](#getting-started--installation)
2. [Configuration & Setup](#configuration--setup)
3. [Web Automation & Locators](#web-automation--locators)
4. [Test Actions & Assertions](#test-actions--assertions)
5. [Debugging & Tracing](#debugging--tracing)
6. [Network Mocking & API Testing](#network-mocking--api-testing)
7. [Mobile Testing & Device Emulation](#mobile-testing--device-emulation)
8. [Cross-Browser Testing](#cross-browser-testing)
9. [Advanced Features](#advanced-features)
10. [Best Practices & Patterns](#best-practices--patterns)

---

## Getting Started & Installation

### Installation Methods

#### Node.js Installation
```bash
# Install Playwright Test
npm i -D @playwright/test

# Install browser binaries
npx playwright install

# Alternative installation methods
yarn add -D @playwright/test
pnpm add -D @playwright/test
```

#### Initialize New Project
```bash
# Create new Playwright project with configuration
npm init playwright@latest

# Or create in specific directory
npm init playwright@latest new-project
```

#### Python Installation
```bash
# Install via pip
pip install --upgrade pip
pip install playwright
playwright install

# Install via conda
conda config --add channels conda-forge
conda config --add channels microsoft
conda install playwright
playwright install
```

#### .NET Installation
```bash
# Create project
dotnet new console -n PlaywrightDemo
cd PlaywrightDemo

# Add Playwright package
dotnet add package Microsoft.Playwright

# Build and install browsers
dotnet build
pwsh bin/Debug/netX/playwright.ps1 install
```

#### Java Installation
```xml
<!-- Add to pom.xml -->
<dependency>
  <groupId>com.microsoft.playwright</groupId>
  <artifactId>playwright</artifactId>
  <version>1.XX.0</version>
</dependency>
```

### Browser Installation Options

```bash
# Install all browsers
npx playwright install

# Install specific browsers
npx playwright install chromium
npx playwright install chromium webkit

# Install with system dependencies
npx playwright install --with-deps
```

---

## Configuration & Setup

### Basic Configuration (`playwright.config.ts`)

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // Test directory
  testDir: 'tests',
  
  // Parallel execution
  fullyParallel: true,
  
  // Fail build if test.only found in CI
  forbidOnly: !!process.env.CI,
  
  // Retry configuration
  retries: process.env.CI ? 2 : 0,
  
  // Workers configuration
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter
  reporter: 'html',
  
  // Global timeout
  timeout: 30000,
  globalTimeout: 600000,
  
  // Global settings
  use: {
    // Base URL for navigation
    baseURL: 'http://localhost:3000',
    
    // Trace settings
    trace: 'on-first-retry',
    
    // Screenshot settings
    screenshot: 'only-on-failure',
    
    // Video settings
    video: 'on-first-retry',
    
    // Browser context settings
    ignoreHTTPSErrors: true,
    
    // Emulation settings
    viewport: { width: 1280, height: 720 },
    locale: 'en-US',
    timezoneId: 'America/New_York',
    colorScheme: 'light',
  },
  
  // Projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  
  // Web server configuration
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

### Multiple Web Servers

```typescript
export default defineConfig({
  webServer: [
    {
      command: 'npm run start',
      url: 'http://localhost:3000',
      name: 'Frontend',
      timeout: 120 * 1000,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'npm run backend',
      url: 'http://localhost:3333',
      name: 'Backend',
      timeout: 120 * 1000,
      reuseExistingServer: !process.env.CI,
    }
  ],
  use: {
    baseURL: 'http://localhost:3000',
  },
});
```

### Global Setup and Teardown

```typescript
// global-setup.ts
import { chromium, type FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const { baseURL, storageState } = config.projects[0].use;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // Perform authentication
  await page.goto(baseURL!);
  await page.getByLabel('User Name').fill('user');
  await page.getByLabel('Password').fill('password');
  await page.getByText('Sign in').click();
  
  // Save authentication state
  await page.context().storageState({ path: storageState as string });
  await browser.close();
}

export default globalSetup;
```

---

## Web Automation & Locators

### Locator Strategies

#### Recommended Locators

```javascript
// By role (most resilient)
await page.getByRole('button', { name: 'Sign in' }).click();
await page.getByRole('link', { name: 'Get started' }).click();

// By label (form elements)
await page.getByLabel('User Name').fill('john');
await page.getByLabel('Password').fill('secret');

// By test ID (explicit testing attributes)
await page.getByTestId('submit-button').click();

// By text content
await page.getByText('Welcome, John!').isVisible();
await page.getByText('Submit', { exact: true }).click();

// By placeholder
await page.getByPlaceholder('Enter your email').fill('user@example.com');

// By alt text (images)
await page.getByAltText('Company logo').click();

// By title attribute
await page.getByTitle('Close dialog').click();
```

#### CSS and XPath Selectors

```javascript
// CSS selectors
await page.locator('css=button').click();
await page.locator('.submit-btn').click();
await page.locator('#login-form').isVisible();

// XPath selectors
await page.locator('xpath=//button').click();
await page.locator('//div[@class="content"]').isVisible();

// Auto-detection (no prefix needed)
await page.locator('button').click();
await page.locator('//button').click();
```

#### Locator Filtering

```javascript
// Filter by text
const product = page.getByRole('listitem').filter({ hasText: 'Product 2' });
await product.getByRole('button', { name: 'Add to cart' }).click();

// Filter by nested locator
const articleWithHeading = page.locator('article').filter({
  has: page.getByRole('heading', { name: 'Breaking News' })
});

// Chain multiple filters
const button = page.getByRole('button')
  .filter({ hasText: 'Submit' })
  .filter({ has: page.locator('.icon') });
```

#### Locator Position

```javascript
// First and last
await page.getByRole('button').first().click();
await page.getByRole('button').last().click();

// By index (use sparingly)
await page.getByRole('button').nth(2).click();

// All matching elements
const buttons = await page.getByRole('button').all();
for (const button of buttons) {
  await button.click();
}
```

### Basic Actions

```javascript
// Click actions
await page.getByRole('button').click();
await page.getByText('Item').click({ button: 'right' });
await page.getByText('Item').dblclick();

// Text input
await page.getByLabel('Email').fill('user@example.com');
await page.getByLabel('Email').clear();
await page.getByLabel('Email').type('user@example.com');

// Keyboard actions
await page.getByLabel('Search').press('Enter');
await page.getByLabel('Search').press('Control+A');

// Checkboxes and radio buttons
await page.getByRole('checkbox', { name: 'Accept terms' }).check();
await page.getByRole('checkbox', { name: 'Subscribe' }).uncheck();
await page.getByRole('radio', { name: 'Option 1' }).check();

// Select dropdowns
await page.getByRole('combobox').selectOption('option-value');
await page.getByRole('combobox').selectOption({ label: 'Option Name' });

// File uploads
await page.getByLabel('Upload').setInputFiles('path/to/file.pdf');
await page.getByLabel('Upload').setInputFiles(['file1.pdf', 'file2.pdf']);

// Hover and focus
await page.getByText('Menu').hover();
await page.getByLabel('Username').focus();
```

---

## Test Actions & Assertions

### Web-First Assertions

```javascript
import { test, expect } from '@playwright/test';

// Visibility assertions
await expect(page.getByText('Welcome')).toBeVisible();
await expect(page.getByText('Loading')).toBeHidden();
await expect(page.getByRole('button')).toBeAttached();

// Text content assertions
await expect(page.getByTestId('status')).toHaveText('Success');
await expect(page.getByRole('heading')).toContainText('Dashboard');
await expect(page.getByRole('listitem')).toHaveText(['Apple', 'Banana', 'Orange']);

// Value assertions
await expect(page.getByLabel('Email')).toHaveValue('user@example.com');
await expect(page.getByRole('textbox')).toBeEmpty();

// Attribute assertions
await expect(page.getByRole('link')).toHaveAttribute('href', '/dashboard');
await expect(page.getByRole('button')).toHaveClass('btn-primary');
await expect(page.getByTestId('element')).toHaveId('unique-id');

// State assertions
await expect(page.getByRole('button')).toBeEnabled();
await expect(page.getByRole('button')).toBeDisabled();
await expect(page.getByRole('checkbox')).toBeChecked();
await expect(page.getByLabel('Password')).toBeFocused();

// Count assertions
await expect(page.getByRole('listitem')).toHaveCount(5);

// CSS assertions
await expect(page.getByTestId('element')).toHaveCSS('color', 'rgb(255, 0, 0)');

// Page assertions
await expect(page).toHaveTitle('My App');
await expect(page).toHaveURL('https://example.com/dashboard');

// Screenshot assertions
await expect(page.getByTestId('chart')).toHaveScreenshot('chart.png');
await expect(page).toHaveScreenshot('full-page.png');
```

### Auto-Waiting and Retry

```javascript
// All locator actions automatically wait
await page.getByRole('button').click(); // Waits for button to be actionable

// Assertions auto-retry until condition is met
await expect(page.getByText('Loading')).toBeHidden(); // Retries until hidden

// Custom waiting
await page.waitForSelector('.dynamic-content');
await page.waitForFunction(() => window.dataLoaded === true);
await page.waitForLoadState('networkidle');
```

### Test Structure

```javascript
import { test, expect } from '@playwright/test';

test.describe('User Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.getByLabel('Username').fill('testuser');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Login' }).click();
    
    await expect(page.getByText('Welcome, testuser')).toBeVisible();
    await expect(page).toHaveURL('/dashboard');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.getByLabel('Username').fill('invalid');
    await page.getByLabel('Password').fill('wrong');
    await page.getByRole('button', { name: 'Login' }).click();
    
    await expect(page.getByText('Invalid credentials')).toBeVisible();
    await expect(page).toHaveURL('/login');
  });
});
```

---

## Debugging & Tracing

### Running Tests in Debug Mode

```bash
# Debug all tests
npx playwright test --debug

# Debug specific test
npx playwright test example.spec.ts --debug

# Debug with UI mode
npx playwright test --ui

# Debug with headed browser
npx playwright test --headed

# Debug specific project
npx playwright test --project=chromium --debug
```

### Environment Variables for Debugging

```bash
# Enable Playwright Inspector
PWDEBUG=1 npx playwright test

# Enable console debugging
PWDEBUG=console npx playwright test

# For Python
PWDEBUG=1 pytest -s

# For .NET
PWDEBUG=1 dotnet test

# For Java
PWDEBUG=1 mvn test
```

### Tracing Configuration

```typescript
// In playwright.config.ts
export default defineConfig({
  use: {
    // Trace on first retry
    trace: 'on-first-retry',
    
    // Always trace
    trace: 'on',
    
    // Only on failure
    trace: 'retain-on-failure',
    
    // Advanced trace options
    trace: {
      mode: 'on',
      screenshots: true,
      snapshots: true,
      sources: true,
    },
  },
});
```

### Programmatic Tracing

```javascript
// Start tracing
await context.tracing.start({
  screenshots: true,
  snapshots: true,
  sources: true,
  title: 'My Test Trace'
});

// Perform test actions
await page.goto('https://example.com');
await page.getByRole('button').click();

// Stop tracing and save
await context.tracing.stop({ path: 'trace.zip' });
```

### Trace Viewer

```bash
# View trace files
npx playwright show-trace trace.zip
npx playwright show-trace trace/

# Online trace viewer (drag and drop)
# Visit: https://trace.playwright.dev
```

### Screenshots and Videos

```typescript
// Screenshot configuration
export default defineConfig({
  use: {
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
});
```

```javascript
// Manual screenshots
await page.screenshot({ path: 'screenshot.png' });
await page.getByTestId('chart').screenshot({ path: 'chart.png' });

// Full page screenshot
await page.screenshot({ path: 'fullpage.png', fullPage: true });
```

### Pause for Debugging

```javascript
// Pause test execution
await page.pause();

// The Playwright Inspector will open
// allowing you to step through the test
```

---

## Network Mocking & API Testing

### Request Interception

```javascript
// Mock API responses
await page.route('**/api/users', async route => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([
      { id: 1, name: 'John Doe' },
      { id: 2, name: 'Jane Smith' }
    ])
  });
});

// Block specific requests
await page.route('**/*.{png,jpg,jpeg}', route => route.abort());

// Modify requests
await page.route('**/api/**', async route => {
  const headers = route.request().headers();
  headers['authorization'] = 'Bearer token123';
  await route.continue({ headers });
});
```

### Advanced Network Interception

```javascript
// Fetch and modify responses
await page.route('**/api/settings', async route => {
  const response = await route.fetch();
  const json = await response.json();
  
  // Modify response data
  json.theme = 'dark';
  json.features = [...json.features, 'newFeature'];
  
  await route.fulfill({ response, json });
});

// Conditional mocking
await page.route('/api/**', async route => {
  if (route.request().postData()?.includes('test-data')) {
    await route.fulfill({ body: 'mocked-response' });
  } else {
    await route.continue();
  }
});
```

### HAR File Mocking

```javascript
// Record HAR file
const context = await browser.newContext({
  recordHar: { path: 'requests.har' }
});

// Replay from HAR file
await page.routeFromHAR('requests.har', {
  url: '**/api/**',
  update: false
});

// Update HAR file with new requests
await page.routeFromHAR('requests.har', {
  url: '**/api/**',
  update: true
});
```

### WebSocket Mocking

```javascript
// Mock WebSocket connections
await page.routeWebSocket('wss://example.com/ws', ws => {
  ws.onMessage(message => {
    if (message === 'ping') {
      ws.send('pong');
    }
  });
});

// Forward to real server with modifications
await page.routeWebSocket('wss://example.com/ws', ws => {
  const server = ws.connectToServer();
  ws.onMessage(message => {
    // Modify message before forwarding
    const modifiedMessage = message.toUpperCase();
    server.send(modifiedMessage);
  });
});
```

### API Testing with Request Context

```javascript
import { test, expect } from '@playwright/test';

test('API testing', async ({ request }) => {
  // POST request
  const response = await request.post('/api/users', {
    data: {
      name: 'John Doe',
      email: 'john@example.com'
    }
  });
  
  expect(response.ok()).toBeTruthy();
  const user = await response.json();
  expect(user.name).toBe('John Doe');
  
  // GET request with headers
  const getResponse = await request.get('/api/users/1', {
    headers: {
      'Authorization': 'Bearer token123'
    }
  });
  
  expect(getResponse.status()).toBe(200);
});
```

---

## Mobile Testing & Device Emulation

### Device Configuration

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  projects: [
    // Mobile devices
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
    {
      name: 'Tablet',
      use: { ...devices['iPad Pro'] },
    },
    
    // Custom mobile configuration
    {
      name: 'Custom Mobile',
      use: {
        ...devices['iPhone 13'],
        viewport: { width: 390, height: 844 },
        deviceScaleFactor: 3,
        isMobile: true,
        hasTouch: true,
        userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)',
      },
    },
  ],
});
```

### Geolocation and Permissions

```javascript
// Set geolocation
test.use({
  geolocation: { longitude: 12.492507, latitude: 41.889938 },
  permissions: ['geolocation'],
});

test('location test', async ({ page, context }) => {
  await page.goto('https://maps.google.com');
  
  // Change location during test
  await context.setGeolocation({ 
    longitude: 48.858455, 
    latitude: 2.294474 
  });
  
  await page.getByText('Your location').click();
});

// Grant permissions
test.use({
  permissions: ['camera', 'microphone', 'notifications'],
});
```

### Touch Events and Gestures

```javascript
// Basic touch events
await page.getByRole('button').tap();

// Custom touch gestures
async function pan(locator, deltaX = 0, deltaY = 0, steps = 5) {
  const { centerX, centerY } = await locator.evaluate(target => {
    const bounds = target.getBoundingClientRect();
    return {
      centerX: bounds.left + bounds.width / 2,
      centerY: bounds.top + bounds.height / 2
    };
  });

  const touches = [{
    identifier: 0,
    clientX: centerX,
    clientY: centerY,
  }];
  
  await locator.dispatchEvent('touchstart', {
    touches,
    changedTouches: touches,
    targetTouches: touches
  });

  for (let i = 1; i <= steps; i++) {
    const touches = [{
      identifier: 0,
      clientX: centerX + deltaX * i / steps,
      clientY: centerY + deltaY * i / steps,
    }];
    
    await locator.dispatchEvent('touchmove', {
      touches,
      changedTouches: touches,
      targetTouches: touches
    });
  }

  await locator.dispatchEvent('touchend');
}

// Pinch gesture
async function pinch(locator, { direction = 'in', deltaX = 50, steps = 5 }) {
  const { centerX, centerY } = await locator.evaluate(target => {
    const bounds = target.getBoundingClientRect();
    return {
      centerX: bounds.left + bounds.width / 2,
      centerY: bounds.top + bounds.height / 2
    };
  });

  const stepDeltaX = deltaX / (steps + 1);
  
  // Initial touch points
  const touches = [
    {
      identifier: 0,
      clientX: centerX - (direction === 'in' ? deltaX : stepDeltaX),
      clientY: centerY,
    },
    {
      identifier: 1,
      clientX: centerX + (direction === 'in' ? deltaX : stepDeltaX),
      clientY: centerY,
    },
  ];
  
  await locator.dispatchEvent('touchstart', {
    touches,
    changedTouches: touches,
    targetTouches: touches
  });

  // Move touch points
  for (let i = 1; i <= steps; i++) {
    const offset = direction === 'in' 
      ? (deltaX - i * stepDeltaX) 
      : (stepDeltaX * (i + 1));
      
    const touches = [
      {
        identifier: 0,
        clientX: centerX - offset,
        clientY: centerY,
      },
      {
        identifier: 1,
        clientX: centerX + offset,
        clientY: centerY,
      },
    ];
    
    await locator.dispatchEvent('touchmove', {
      touches,
      changedTouches: touches,
      targetTouches: touches
    });
  }

  await locator.dispatchEvent('touchend', {
    touches: [],
    changedTouches: [],
    targetTouches: []
  });
}
```

### Viewport and Media Queries

```javascript
// Custom viewport
await page.setViewportSize({ width: 375, height: 667 });

// Test responsive design
test.describe('Responsive Design', () => {
  test('mobile layout', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await expect(page.getByTestId('mobile-menu')).toBeVisible();
  });

  test('desktop layout', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');
    await expect(page.getByTestId('desktop-nav')).toBeVisible();
  });
});

// Color scheme testing
test.use({ colorScheme: 'dark' });

test('dark mode', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('body')).toHaveClass(/dark-theme/);
});
```

---

## Cross-Browser Testing

### Browser Configuration

```typescript
export default defineConfig({
  projects: [
    // Desktop browsers
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    
    // Branded browsers
    {
      name: 'Google Chrome',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome'
      },
    },
    {
      name: 'Microsoft Edge',
      use: {
        ...devices['Desktop Edge'],
        channel: 'msedge'
      },
    },
    
    // Browser with custom settings
    {
      name: 'Chrome Incognito',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: ['--incognito']
        }
      },
    },
  ],
});
```

### Running Specific Browsers

```bash
# Run all projects
npx playwright test

# Run specific browser
npx playwright test --project=firefox
npx playwright test --project="Mobile Safari"

# Run multiple browsers
npx playwright test --project=chromium --project=firefox
```

### Browser-Specific Configurations

```javascript
// Browser launch options
export default defineConfig({
  use: {
    launchOptions: {
      // Slow motion for debugging
      slowMo: 50,
      
      // Additional Chrome arguments
      args: ['--disable-web-security', '--disable-features=VizDisplayCompositor'],
      
      // Custom executable path
      executablePath: '/path/to/browser',
    },
  },
});
```

### Conditional Browser Logic

```javascript
test('browser-specific behavior', async ({ page, browserName }) => {
  await page.goto('/');
  
  if (browserName === 'webkit') {
    // Safari-specific behavior
    await page.waitForLoadState('networkidle');
  }
  
  if (browserName === 'firefox') {
    // Firefox-specific behavior
    await page.addInitScript(() => {
      window.firefoxSpecificSetup = true;
    });
  }
  
  // Common test logic
  await page.getByRole('button').click();
});
```

---

## Advanced Features

### Page Object Model

```typescript
// page-objects/LoginPage.ts
import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.usernameInput = page.getByLabel('Username');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Login' });
    this.errorMessage = page.getByTestId('error-message');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toHaveText(message);
  }
}

// Using the Page Object
test('login flow', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('testuser', 'password123');
  await expect(page).toHaveURL('/dashboard');
});
```

### Custom Fixtures

```typescript
// fixtures.ts
import { test as base } from '@playwright/test';
import { LoginPage } from './page-objects/LoginPage';

type MyFixtures = {
  loginPage: LoginPage;
  authenticatedPage: Page;
};

export const test = base.extend<MyFixtures>({
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await use(loginPage);
  },

  authenticatedPage: async ({ page }, use) => {
    // Automatically login before each test
    await page.goto('/login');
    await page.getByLabel('Username').fill('testuser');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Login' }).click();
    await page.waitForURL('/dashboard');
    await use(page);
  },
});

export { expect } from '@playwright/test';
```

### Component Testing

```typescript
// component.spec.tsx
import { test, expect } from '@playwright/experimental-ct-react';
import { Button } from './Button';

test('button click', async ({ mount }) => {
  let clicked = false;
  
  const component = await mount(
    <Button onClick={() => { clicked = true; }}>
      Click me
    </Button>
  );
  
  await component.click();
  expect(clicked).toBe(true);
});
```

### Parallel Testing and Sharding

```bash
# Run tests in parallel (default)
npx playwright test

# Shard tests across multiple machines
npx playwright test --shard=1/3  # Machine 1 of 3
npx playwright test --shard=2/3  # Machine 2 of 3
npx playwright test --shard=3/3  # Machine 3 of 3

# Control worker count
npx playwright test --workers=4
```

### Test Dependencies

```typescript
export default defineConfig({
  projects: [
    {
      name: 'setup',
      testMatch: /global\.setup\.ts/,
    },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },
  ],
});
```

### Visual Comparisons

```javascript
// Screenshot testing
await expect(page).toHaveScreenshot('landing-page.png');
await expect(page.getByTestId('chart')).toHaveScreenshot('chart.png');

// Custom screenshot options
await expect(page).toHaveScreenshot('page.png', {
  fullPage: true,
  threshold: 0.2,
  maxDiffPixels: 100,
});

// Update screenshots
// npx playwright test --update-snapshots
```

---

## Best Practices & Patterns

### Locator Best Practices

```javascript
// ✅ Good - Use role-based locators
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

// ✅ Good - Use test IDs for complex cases
await page.getByTestId('user-profile-dropdown').click();

// ✅ Good - Use label association
await page.getByLabel('Password').fill('secret123');

// ❌ Avoid - Fragile CSS selectors
await page.locator('.btn.btn-primary.submit-button').click();

// ❌ Avoid - XPath with positions
await page.locator('//div[3]/span[2]/button').click();
```

### Test Organization

```javascript
// Group related tests
test.describe('User Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('valid login', async ({ page }) => {
    // Test implementation
  });

  test('invalid credentials', async ({ page }) => {
    // Test implementation
  });
});

// Use descriptive test names
test('should display validation error when email format is invalid', async ({ page }) => {
  // Clear and specific test case
});

// Use tags for test organization
test('critical user flow @smoke @critical', async ({ page }) => {
  // Important test case
});
```

### Error Handling

```javascript
// Handle dynamic content
await page.waitForFunction(() => {
  return document.querySelector('[data-testid="content"]')?.textContent?.length > 0;
});

// Handle network conditions
await page.route('**/api/slow-endpoint', async route => {
  await new Promise(resolve => setTimeout(resolve, 5000));
  await route.continue();
});

// Retry mechanisms
await expect(async () => {
  const response = await page.request.get('/api/status');
  expect(response.status()).toBe(200);
}).toPass({
  timeout: 10000,
  intervals: [1000, 2000, 3000],
});
```

### Performance Testing

```javascript
// Measure page load time
test('page performance', async ({ page }) => {
  const startTime = Date.now();
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  const loadTime = Date.now() - startTime;
  
  expect(loadTime).toBeLessThan(3000);
});

// Network monitoring
test('API performance', async ({ page }) => {
  const responses = [];
  
  page.on('response', response => {
    if (response.url().includes('/api/')) {
      responses.push({
        url: response.url(),
        status: response.status(),
        timing: response.request().timing(),
      });
    }
  });
  
  await page.goto('/dashboard');
  
  // Verify API response times
  const slowResponses = responses.filter(r => 
    r.timing.responseEnd - r.timing.requestStart > 2000
  );
  
  expect(slowResponses).toHaveLength(0);
});
```

### CI/CD Integration

```yaml
# GitHub Actions
name: Playwright Tests
on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: lts/*
    - name: Install dependencies
      run: npm ci
    - name: Install Playwright Browsers
      run: npx playwright install --with-deps
    - name: Run Playwright tests
      run: npx playwright test
    - uses: actions/upload-artifact@v4
      if: always()
      with:
        name: playwright-report
        path: playwright-report/
        retention-days: 30
```

### Environment Management

```typescript
// Environment-specific configuration
export default defineConfig({
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
  },
  
  projects: [
    {
      name: 'staging',
      use: {
        baseURL: 'https://staging.example.com',
      },
    },
    {
      name: 'production',
      use: {
        baseURL: 'https://example.com',
      },
    },
  ],
});

// Environment variables in tests
test('environment-specific test', async ({ page }) => {
  const apiUrl = process.env.API_URL || 'http://localhost:8080';
  
  await page.route(`${apiUrl}/api/**`, route => {
    // Environment-specific mocking
  });
});
```

### Security Testing

```javascript
// Test authentication
test('protected routes require authentication', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page).toHaveURL('/login');
});

// Test authorization
test('admin features hidden from regular users', async ({ page }) => {
  // Login as regular user
  await page.goto('/login');
  await page.getByLabel('Username').fill('user');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Login' }).click();
  
  await page.goto('/dashboard');
  await expect(page.getByTestId('admin-panel')).not.toBeVisible();
});

// Test input validation
test('prevents XSS attacks', async ({ page }) => {
  await page.goto('/contact');
  const maliciousScript = '<script>alert("XSS")</script>';
  
  await page.getByLabel('Message').fill(maliciousScript);
  await page.getByRole('button', { name: 'Submit' }).click();
  
  // Script should be escaped, not executed
  await expect(page.getByText(maliciousScript)).toBeVisible();
});
```

---

## Common Commands Reference

### Test Execution

```bash
# Run all tests
npx playwright test

# Run specific test file
npx playwright test example.spec.ts

# Run tests matching pattern
npx playwright test --grep "login"

# Run in headed mode
npx playwright test --headed

# Run in debug mode
npx playwright test --debug

# Run in UI mode
npx playwright test --ui

# Run with tracing
npx playwright test --trace on

# Run specific project
npx playwright test --project=chromium

# Run with specific reporter
npx playwright test --reporter=json
```

### Code Generation

```bash
# Generate test with codegen
npx playwright codegen https://example.com

# Generate with device emulation
npx playwright codegen --device="iPhone 13" https://example.com

# Generate with custom viewport
npx playwright codegen --viewport-size="800,600" https://example.com

# Generate with geolocation
npx playwright codegen --geolocation="41.890221,12.492348" https://example.com
```

### Reporting and Analysis

```bash
# Show HTML report
npx playwright show-report

# Show trace viewer
npx playwright show-trace trace.zip

# Update screenshots
npx playwright test --update-snapshots

# Install browsers
npx playwright install

# Install specific browser
npx playwright install chromium
```

This comprehensive documentation covers all major aspects of Playwright testing, from basic setup to advanced patterns. Use it as a reference for building robust, maintainable test suites that work across different browsers and devices.