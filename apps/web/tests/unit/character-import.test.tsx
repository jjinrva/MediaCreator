import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { CharacterImportIngest } from "../../components/character-import/CharacterImportIngest";

const createObjectURL = vi.fn((file: File) => `blob:${file.name}`);
const fetchMock = vi.fn();
const push = vi.fn();
const revokeObjectURL = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push
  })
}));

describe("Phase 11 character ingest", () => {
  beforeEach(() => {
    Object.defineProperty(window.URL, "createObjectURL", {
      configurable: true,
      writable: true,
      value: createObjectURL
    });
    Object.defineProperty(window.URL, "revokeObjectURL", {
      configurable: true,
      writable: true,
      value: revokeObjectURL
    });
    vi.stubGlobal("fetch", fetchMock);
    window.history.replaceState({}, "", "/studio/characters/new");
  });

  afterEach(() => {
    createObjectURL.mockClear();
    fetchMock.mockReset();
    push.mockReset();
    revokeObjectURL.mockClear();
    vi.unstubAllGlobals();
  });

  it("renders local thumbnails, neutral QC badges, and supports removal before upload", async () => {
    render(<CharacterImportIngest />);

    const input = screen.getByTestId("photoset-input");
    const fileA = new File(["alpha"], "photo-a.png", { type: "image/png" });
    const fileB = new File(["beta"], "photo-b.png", { type: "image/png" });

    fireEvent.change(input, {
      target: {
        files: [fileA, fileB]
      }
    });

    await waitFor(() => {
      expect(screen.getByRole("img", { name: "Preview of photo-a.png" })).toBeTruthy();
      expect(screen.getByRole("img", { name: "Preview of photo-b.png" })).toBeTruthy();
    });

    expect(screen.getAllByText("QC pending backend upload")).toHaveLength(2);

    fireEvent.click(screen.getByRole("button", { name: "Remove photo-a.png" }));

    await waitFor(() => {
      expect(screen.queryByRole("img", { name: "Preview of photo-a.png" })).toBeNull();
    });

    expect(screen.getByRole("img", { name: "Preview of photo-b.png" })).toBeTruthy();
    expect(
      screen.getByText(/No previously created characters are shown here/i)
    ).toBeTruthy();
  });

  it("creates the base character from a persisted photoset and redirects to the public route", async () => {
    window.history.replaceState({}, "", "/studio/characters/new?photoset=phase-11-photoset");
    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          entry_count: 1,
          entries: [
            {
              artifact_urls: {
                normalized: "http://10.0.0.102:8010/api/v1/photosets/phase-11/normalized",
                original: "http://10.0.0.102:8010/api/v1/photosets/phase-11/original",
                thumbnail: "http://10.0.0.102:8010/api/v1/photosets/phase-11/thumbnail"
              },
              original_filename: "male_body_front.png",
              public_id: "phase-11-entry",
              qc_metrics: {
                body_landmarks_detected: true,
                blur_score: 120,
                exposure_score: 96,
                face_detected: true,
                framing_label: "full-body"
              },
              qc_reasons: [],
              qc_status: "pass"
            }
          ],
          public_id: "phase-11-photoset",
          status: "prepared"
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          public_id: "phase-11-character"
        })
      });

    render(<CharacterImportIngest />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Create base character" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Create base character" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenNthCalledWith(
        2,
        "http://10.0.0.102:8010/api/v1/characters",
        expect.objectContaining({
          method: "POST"
        })
      );
      expect(push).toHaveBeenCalledWith("/studio/characters/phase-11-character");
    });
  });
});
