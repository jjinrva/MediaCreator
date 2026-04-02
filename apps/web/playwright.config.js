const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests/e2e",
  timeout: 30000,
  use: {
    baseURL: "http://127.0.0.1:3000"
  },
  webServer: [
    {
      command:
        "bash -lc '../api/.venv/bin/alembic -c ../api/alembic.ini upgrade head && " +
        "../api/.venv/bin/uvicorn app.main:app --app-dir ../api --host 127.0.0.1 --port 8010'",
      cwd: __dirname,
      url: "http://127.0.0.1:8010/health",
      timeout: 120000,
      reuseExistingServer: false
    },
    {
      command: "../../infra/bin/pnpm dev --hostname 127.0.0.1 --port 3000",
      cwd: __dirname,
      url: "http://127.0.0.1:3000",
      timeout: 120000,
      reuseExistingServer: false
    }
  ]
});
