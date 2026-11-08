import { defineConfig } from "@playwright/test";
import { fileURLToPath } from "node:url";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30000,
  expect: { timeout: 10000 },
  use: {
    baseURL: "http://127.0.0.1:8000",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium", use: { browserName: "chromium", viewport: { width: 1366, height: 900 } } },
    { name: "webkit-ipad", use: {
      browserName: "webkit",
      viewport: { width: 820, height: 1180 },
      isMobile: true,
      hasTouch: true,
      deviceScaleFactor: 2,
    } },
  ],
  webServer: {
    command: "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000",
    cwd: fileURLToPath(new URL("../", import.meta.url)),
    url: "http://127.0.0.1:8000/api/health",
    timeout: 30000,
    reuseExistingServer: !process.env.CI,
    env: { SIMCOTER_AI_ENABLED: "false" },
  },
});
