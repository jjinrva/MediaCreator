const { defineConfig } = require("@playwright/test");

const PLAYWRIGHT_HOST = process.env.MEDIACREATOR_PLAYWRIGHT_HOST ?? "localhost";
const PLAYWRIGHT_WEB_PORT = process.env.MEDIACREATOR_PLAYWRIGHT_WEB_PORT ?? "3100";
const PLAYWRIGHT_API_PORT = process.env.MEDIACREATOR_PLAYWRIGHT_API_PORT ?? "8110";
const WEB_BASE_URL =
  process.env.MEDIACREATOR_PLAYWRIGHT_WEB_BASE_URL ??
  `http://${PLAYWRIGHT_HOST}:${PLAYWRIGHT_WEB_PORT}`;
const API_BASE_URL =
  process.env.MEDIACREATOR_PLAYWRIGHT_API_BASE_URL ??
  `http://${PLAYWRIGHT_HOST}:${PLAYWRIGHT_API_PORT}`;

process.env.MEDIACREATOR_PLAYWRIGHT_WEB_BASE_URL = WEB_BASE_URL;
process.env.MEDIACREATOR_PLAYWRIGHT_API_BASE_URL = API_BASE_URL;

module.exports = defineConfig({
  testDir: "./tests/e2e",
  timeout: 30000,
  workers: 1,
  use: {
    baseURL: WEB_BASE_URL
  },
  webServer: [
    {
      command:
        "bash -lc 'mkdir -p /opt/MediaCreator/storage/playwright-nas/models/loras && " +
        "MEDIACREATOR_STORAGE_NAS_ROOT=/opt/MediaCreator/storage/playwright-nas " +
        "MEDIACREATOR_STORAGE_LORAS_ROOT=/opt/MediaCreator/storage/playwright-nas/models/loras " +
        "../api/.venv/bin/alembic -c ../api/alembic.ini upgrade head && " +
        "MEDIACREATOR_STORAGE_NAS_ROOT=/opt/MediaCreator/storage/playwright-nas " +
        "MEDIACREATOR_STORAGE_LORAS_ROOT=/opt/MediaCreator/storage/playwright-nas/models/loras " +
        `../api/.venv/bin/uvicorn app.main:app --app-dir ../api --host 0.0.0.0 --port ${PLAYWRIGHT_API_PORT}'`,
      cwd: __dirname,
      url: `${API_BASE_URL}/health`,
      timeout: 120000,
      reuseExistingServer: false
    },
    {
      command:
        `NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL=${API_BASE_URL} ` +
        `MEDIACREATOR_INTERNAL_API_BASE_URL=${API_BASE_URL} ` +
        `MEDIACREATOR_ALLOWED_DEV_ORIGINS=${PLAYWRIGHT_HOST} ` +
        `../../infra/bin/pnpm dev --hostname 0.0.0.0 --port ${PLAYWRIGHT_WEB_PORT}`,
      cwd: __dirname,
      url: WEB_BASE_URL,
      timeout: 120000,
      reuseExistingServer: false
    }
  ]
});
