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

    expect(screen.getAllByText("Pending backend classification")).toHaveLength(2);

    fireEvent.click(screen.getByRole("button", { name: "Remove photo-a.png" }));

    await waitFor(() => {
      expect(screen.queryByRole("img", { name: "Preview of photo-a.png" })).toBeNull();
    });

    expect(screen.getByRole("img", { name: "Preview of photo-b.png" })).toBeTruthy();
    expect(screen.getAllByText("Pending backend classification")).toHaveLength(1);
  });

  it("creates the base character from a persisted photoset and redirects to the public route", async () => {
    window.history.replaceState({}, "", "/studio/characters/new?photoset=phase-11-photoset");
    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          accepted_entry_count: 1,
          entry_count: 1,
          entries: [
            {
              accepted_for_character_use: true,
              artifact_urls: {
                normalized: "http://localhost:8010/api/v1/photosets/phase-11/normalized",
                original: "http://localhost:8010/api/v1/photosets/phase-11/original",
                thumbnail: "http://localhost:8010/api/v1/photosets/phase-11/thumbnail"
              },
              bucket: "both",
              original_filename: "male_body_front.png",
              photo_asset_public_id: "phase-11-photo",
              public_id: "phase-11-entry",
              qc_metrics: {
                body_landmarks_detected: true,
                blur_score: 120,
                blur_ok_for_body: true,
                blur_ok_for_lora: true,
                body_detected: true,
                exposure_score: 96,
                exposure_ok_for_body: true,
                exposure_ok_for_lora: true,
                face_detected: true,
                framing_label: "full-body",
                has_person: true,
                occlusion_label: "clear",
                person_detected: true,
                resolution_ok: true
              },
              qc_reasons: [],
              qc_status: "pass",
              reason_codes: [],
              reason_messages: [],
              usable_for_body: true,
              usable_for_lora: true
            }
          ],
          public_id: "phase-11-photoset",
          rejected_entry_count: 0,
          status: "prepared"
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          public_id: "phase-11-character"
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          detail: "Preview export queued. Follow the job until it reaches a terminal state.",
          job_public_id: "phase-11-job",
          progress_percent: 0,
          status: "queued",
          step_name: "queued"
        })
      });

    render(<CharacterImportIngest />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Build base character" })).toBeTruthy();
    });

    expect(screen.getByText("1 accepted")).toBeTruthy();
    expect(screen.getByText("0 rejected")).toBeTruthy();
    expect(screen.getByText("pass and warn can build")).toBeTruthy();
    expect(screen.getByText("Accepted for character use")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Build base character" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenNthCalledWith(
        2,
        "http://localhost:8010/api/v1/characters",
        expect.objectContaining({
          method: "POST"
        })
      );
      expect(fetchMock).toHaveBeenNthCalledWith(
        3,
        "http://localhost:8010/api/v1/exports/characters/phase-11-character/preview",
        { method: "POST" }
      );
      expect(push).toHaveBeenCalledWith("/studio/characters/phase-11-character");
    });
  });

  it("blocks character creation when the persisted photoset has zero accepted entries", async () => {
    window.history.replaceState({}, "", "/studio/characters/new?photoset=phase-11-photoset");
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        accepted_entry_count: 0,
        entry_count: 1,
        entries: [
          {
            accepted_for_character_use: false,
            artifact_urls: {
              normalized: "http://localhost:8010/api/v1/photosets/phase-11/normalized",
              original: "http://localhost:8010/api/v1/photosets/phase-11/original",
              thumbnail: "http://localhost:8010/api/v1/photosets/phase-11/thumbnail"
            },
            bucket: "rejected",
            original_filename: "female_head_front.png",
            photo_asset_public_id: "phase-11-photo",
            public_id: "phase-11-entry",
            qc_metrics: {
              body_landmarks_detected: false,
              blur_score: 55,
              blur_ok_for_body: true,
              blur_ok_for_lora: false,
              body_detected: false,
              exposure_score: 96,
              exposure_ok_for_body: true,
              exposure_ok_for_lora: true,
              face_detected: true,
              framing_label: "head-closeup",
              has_person: true,
              occlusion_label: "body_not_visible",
              person_detected: true,
              resolution_ok: true
            },
            qc_reasons: ["Image appears too blurry."],
            qc_status: "fail",
            reason_codes: ["blur_below_lora_threshold"],
            reason_messages: ["Image appears too blurry."],
            usable_for_body: false,
            usable_for_lora: false
          }
        ],
        public_id: "phase-11-photoset",
        rejected_entry_count: 1,
        status: "prepared"
      })
    });

    render(<CharacterImportIngest />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Build base character" })).toBeTruthy();
    });

    expect(screen.getByText("Rejected from character use")).toBeTruthy();
    expect(
      screen.getAllByText(
        /Create saved character stays disabled until ingest completes and at least one accepted image exists\./i
      ).length
    ).toBeGreaterThan(0);
    expect(
      (screen.getByRole("button", { name: "Build base character" }) as HTMLButtonElement).disabled
    ).toBe(true);
  });
});
