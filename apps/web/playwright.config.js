const { defineConfig } = require("@playwright/test");

const WEB_BASE_URL = "http://10.0.0.102:3000";
const API_BASE_URL = "http://10.0.0.102:8010";

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
        "../api/.venv/bin/uvicorn app.main:app --app-dir ../api --host 0.0.0.0 --port 8010'",
      cwd: __dirname,
      url: `${API_BASE_URL}/health`,
      timeout: 120000,
      reuseExistingServer: false
    },
    {
      command: "../../infra/bin/pnpm dev --hostname 0.0.0.0 --port 3000",
      cwd: __dirname,
      url: WEB_BASE_URL,
      timeout: 120000,
      reuseExistingServer: false
    }
  ]
});
