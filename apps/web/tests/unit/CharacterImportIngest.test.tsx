import React from "react";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { CharacterImportIngest } from "../../components/character-import/CharacterImportIngest";

const createObjectURL = vi.fn((file: File) => `blob:${file.name}`);
const fetchMock = vi.fn();
const push = vi.fn();
const revokeObjectURL = vi.fn();

type UploadResponse = {
  accepted_entry_count: number;
  bucket_counts: {
    body_only: number;
    both: number;
    lora_only: number;
    rejected: number;
  };
  character_label: string;
  entries: Array<{
    accepted_for_character_use: boolean;
    artifact_urls: {
      normalized: string;
      original: string;
      thumbnail: string;
    };
    bucket: "both";
    original_filename: string;
    photo_asset_public_id: string;
    public_id: string;
    qc_metrics: {
      blur_score: number;
      body_detected: boolean;
      body_landmarks_detected: boolean;
      exposure_score: number;
      face_detected: boolean;
      framing_label: string;
      has_person: boolean;
      occlusion_label: string;
      resolution_ok: boolean;
    };
    qc_reasons: string[];
    qc_status: "pass";
    reason_codes: string[];
    reason_messages: string[];
    usable_for_body: boolean;
    usable_for_lora: boolean;
  }>;
  entry_count: number;
  ingest_job: {
    bucket_counts: {
      body_only: number;
      both: number;
      lora_only: number;
      rejected: number;
    };
    job_public_id: string;
    processed_files: number;
    progress_percent: number;
    status: string;
    step_name: string;
    total_files: number;
  };
  public_id: string;
  rejected_entry_count: number;
  status: string;
};

class MockXMLHttpRequest {
  static nextResponse: UploadResponse | null = null;

  onerror: (() => void) | null = null;
  onload: (() => void) | null = null;
  responseText = "";
  status = 0;
  upload: {
    onload: ((event?: ProgressEvent) => void) | null;
    onprogress: ((event: ProgressEvent) => void) | null;
  } = {
    onload: null,
    onprogress: null
  };

  open(_method: string, _url: string) {}

  send(_body: FormData) {
    window.setTimeout(() => {
      this.upload.onprogress?.({
        lengthComputable: true,
        loaded: 512,
        total: 1024
      } as ProgressEvent);
    }, 0);

    window.setTimeout(() => {
      this.upload.onload?.(new ProgressEvent("load"));
      this.status = 201;
      this.responseText = JSON.stringify(MockXMLHttpRequest.nextResponse);
      this.onload?.();
    }, 10);
  }
}

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push
  })
}));

function buildUploadResponse(label: string): UploadResponse {
  return {
    accepted_entry_count: 1,
    bucket_counts: {
      body_only: 0,
      both: 1,
      lora_only: 0,
      rejected: 0
    },
    character_label: label,
    entries: [
      {
        accepted_for_character_use: true,
        artifact_urls: {
          normalized: "http://localhost:8010/api/v1/photosets/phase-02/normalized",
          original: "http://localhost:8010/api/v1/photosets/phase-02/original",
          thumbnail: "http://localhost:8010/api/v1/photosets/phase-02/thumbnail"
        },
        bucket: "both",
        original_filename: "subject.png",
        photo_asset_public_id: "photo-1",
        public_id: "entry-1",
        qc_metrics: {
          blur_score: 144,
          body_detected: true,
          body_landmarks_detected: true,
          exposure_score: 100,
          face_detected: true,
          framing_label: "full-body",
          has_person: true,
          occlusion_label: "clear",
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
    entry_count: 1,
    ingest_job: {
      bucket_counts: {
        body_only: 0,
        both: 1,
        lora_only: 0,
        rejected: 0
      },
      job_public_id: "job-phase-02",
      processed_files: 1,
      progress_percent: 100,
      status: "completed",
      step_name: "completed",
      total_files: 1
    },
    public_id: "photoset-phase-02",
    rejected_entry_count: 0,
    status: "prepared"
  };
}

describe("Phase 02 CharacterImportIngest", () => {
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
    vi.stubGlobal(
      "XMLHttpRequest",
      MockXMLHttpRequest as unknown as typeof XMLHttpRequest
    );
    window.history.replaceState({}, "", "/studio/characters/new");
  });

  afterEach(() => {
    cleanup();
    createObjectURL.mockClear();
    fetchMock.mockReset();
    push.mockReset();
    revokeObjectURL.mockClear();
    MockXMLHttpRequest.nextResponse = null;
    vi.unstubAllGlobals();
  });

  it("keeps upload disabled until the label is non-empty after trim", async () => {
    render(<CharacterImportIngest />);

    const input = screen.getByTestId("photoset-input");
    const uploadButton = screen.getByRole("button", { name: "Upload photoset" });
    const file = new File([new Uint8Array(1024)], "photo-a.png", { type: "image/png" });

    fireEvent.change(input, {
      target: {
        files: [file]
      }
    });

    await waitFor(() => {
      expect(screen.getByRole("img", { name: "Preview of photo-a.png" })).toBeTruthy();
    });

    expect((uploadButton as HTMLButtonElement).disabled).toBe(true);

    fireEvent.change(screen.getByRole("textbox", { name: "Character label" }), {
      target: { value: "   " }
    });
    expect((uploadButton as HTMLButtonElement).disabled).toBe(true);

    fireEvent.change(screen.getByRole("textbox", { name: "Character label" }), {
      target: { value: "Repeat Label" }
    });

    expect((uploadButton as HTMLButtonElement).disabled).toBe(false);
  });

  it("accepts a reused label and shows transfer progress during upload", async () => {
    MockXMLHttpRequest.nextResponse = buildUploadResponse("Repeat Label");
    fetchMock.mockImplementation(async (input: string | URL | Request) => {
      const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;

      if (url.endsWith("/api/v1/jobs/job-phase-02")) {
        return {
          ok: true,
          json: async () => ({
            error_summary: null,
            finished_at: "2026-04-02T00:00:00Z",
            job_type: "photoset-ingest",
            output_asset_id: "asset-1",
            output_storage_object_id: null,
            progress: {
              bucket_counts: {
                body_only: 0,
                both: 1,
                lora_only: 0,
                rejected: 0
              },
              processed_files: 1,
              total_files: 1
            },
            progress_percent: 100,
            public_id: "job-phase-02",
            stage_history: [
              {
                bucket_counts: {
                  body_only: 0,
                  both: 1,
                  lora_only: 0,
                  rejected: 0
                },
                created_at: "2026-04-02T00:00:00Z",
                event_type: "job.completed",
                processed_files: 1,
                progress_percent: 100,
                status: "completed",
                step_name: "completed",
                total_files: 1
              }
            ],
            started_at: "2026-04-02T00:00:00Z",
            status: "completed",
            step_name: "completed"
          })
        };
      }

      if (url.endsWith("/api/v1/photosets/photoset-phase-02")) {
        return {
          ok: true,
          json: async () => buildUploadResponse("Repeat Label")
        };
      }

      throw new Error(`Unexpected fetch URL in test: ${url}`);
    });

    render(<CharacterImportIngest />);

    const input = screen.getByTestId("photoset-input");
    const file = new File([new Uint8Array(1024)], "photo-a.png", { type: "image/png" });

    fireEvent.change(input, {
      target: {
        files: [file]
      }
    });

    fireEvent.change(screen.getByRole("textbox", { name: "Character label" }), {
      target: { value: "Repeat Label" }
    });
    fireEvent.submit(screen.getByRole("button", { name: "Upload photoset" }).closest("form")!);

    await waitFor(() => {
      expect(screen.getByText("0.5 KB / 1.0 KB (50%)")).toBeTruthy();
    });

    await waitFor(() => {
      expect(screen.getByText("1 accepted")).toBeTruthy();
      expect(screen.getByText("1 / 1 processed")).toBeTruthy();
    });

    expect(screen.queryByText(/duplicate label/i)).toBeNull();
  });
});
