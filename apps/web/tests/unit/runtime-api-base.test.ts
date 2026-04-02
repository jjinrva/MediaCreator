import { afterEach, describe, expect, it, vi } from "vitest";

import { getApiBase } from "../../lib/runtimeApiBase";

const originalInternalApiBase = process.env.MEDIACREATOR_INTERNAL_API_BASE_URL;
const originalPublicApiBase = process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL;

describe("runtime API base helper", () => {
  afterEach(() => {
    if (originalInternalApiBase === undefined) {
      delete process.env.MEDIACREATOR_INTERNAL_API_BASE_URL;
    } else {
      process.env.MEDIACREATOR_INTERNAL_API_BASE_URL = originalInternalApiBase;
    }

    if (originalPublicApiBase === undefined) {
      delete process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL;
    } else {
      process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL = originalPublicApiBase;
    }

    vi.unstubAllGlobals();
  });

  it("prefers the explicit public API base when configured", () => {
    process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL = "http://lan-box:8010";

    expect(getApiBase()).toBe("http://lan-box:8010");
  });

  it("derives the browser API base from the current hostname by default", () => {
    delete process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL;

    expect(getApiBase()).toBe("http://localhost:8010");
  });

  it("uses the active browser hostname instead of a fixed LAN IP", () => {
    delete process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL;

    Object.defineProperty(window, "location", {
      configurable: true,
      value: {
        hostname: "media-box.local",
        protocol: "http:"
      }
    });

    expect(getApiBase()).toBe("http://media-box.local:8010");
  });

  it("uses the internal server API base when window is unavailable", () => {
    delete process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL;
    process.env.MEDIACREATOR_INTERNAL_API_BASE_URL = "http://127.0.0.1:8011";
    vi.stubGlobal("window", undefined);

    expect(getApiBase()).toBe("http://127.0.0.1:8011");
  });

  it("falls back to the internal localhost default on the server", () => {
    delete process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL;
    delete process.env.MEDIACREATOR_INTERNAL_API_BASE_URL;
    vi.stubGlobal("window", undefined);

    expect(getApiBase()).toBe("http://127.0.0.1:8010");
  });
});
