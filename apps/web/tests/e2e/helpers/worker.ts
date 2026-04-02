import { once } from "node:events";
import { spawn } from "node:child_process";

const PLAYWRIGHT_HOST = process.env.MEDIACREATOR_PLAYWRIGHT_HOST ?? "localhost";
const API_BASE_URL =
  process.env.MEDIACREATOR_PLAYWRIGHT_API_BASE_URL ?? `http://${PLAYWRIGHT_HOST}:8010`;
const PLAYWRIGHT_NAS_ROOT = "/opt/MediaCreator/storage/playwright-nas";

type SystemStatusPayload = {
  worker: {
    status: string;
  };
};

function sleep(milliseconds: number) {
  return new Promise((resolve) => {
    setTimeout(resolve, milliseconds);
  });
}

async function readWorkerStatus(): Promise<string | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/system/status`, {
      cache: "no-store"
    });
    if (!response.ok) {
      return null;
    }

    const payload = (await response.json()) as SystemStatusPayload;
    return payload.worker.status;
  } catch {
    return null;
  }
}

async function waitForWorkerReady(timeoutMilliseconds: number) {
  const startedAt = Date.now();

  while (Date.now() - startedAt < timeoutMilliseconds) {
    if ((await readWorkerStatus()) === "ready") {
      return;
    }
    await sleep(500);
  }

  throw new Error("Worker heartbeat never reached ready during the Playwright test.");
}

export async function startWorkerForPlaywright(): Promise<() => Promise<void>> {
  const worker = spawn(
    "bash",
    [
      "-lc",
      "cd /opt/MediaCreator && " +
        `MEDIACREATOR_STORAGE_NAS_ROOT=${PLAYWRIGHT_NAS_ROOT} ` +
        `MEDIACREATOR_STORAGE_LORAS_ROOT=${PLAYWRIGHT_NAS_ROOT}/models/loras ` +
        "scripts/run_worker.sh"
    ],
    {
      stdio: "ignore"
    }
  );

  await waitForWorkerReady(30000);

  return async () => {
    if (worker.exitCode !== null || worker.killed) {
      return;
    }

    worker.kill("SIGINT");
    await Promise.race([
      once(worker, "exit"),
      sleep(5000).then(() => {
        if (worker.exitCode === null && !worker.killed) {
          worker.kill("SIGKILL");
        }
      })
    ]);
  };
}
