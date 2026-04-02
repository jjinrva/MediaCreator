import { expect, test } from "@playwright/test";

test("clicking a persisted thumbnail opens an enlarged preview dialog with bucket details", async ({
  page
}) => {
  await page.route("**/api/v1/photosets/photoset-phase-02", async (route) => {
    await route.fulfill({
      body: JSON.stringify({
        accepted_entry_count: 2,
        bucket_counts: {
          body_only: 1,
          both: 1,
          lora_only: 0,
          rejected: 1
        },
        character_label: "Preview Subject",
        entries: [
          {
            accepted_for_character_use: true,
            artifact_urls: {
              normalized: "http://localhost:8010/api/v1/photosets/phase-02/normalized-a",
              original: "http://localhost:8010/api/v1/photosets/phase-02/original-a",
              thumbnail: "http://localhost:8010/api/v1/photosets/phase-02/thumbnail-a"
            },
            bucket: "body_only",
            original_filename: "male_body_front.png",
            photo_asset_public_id: "photo-a",
            public_id: "entry-a",
            qc_metrics: {
              blur_score: 98,
              body_detected: true,
              body_landmarks_detected: true,
              exposure_score: 92,
              face_detected: false,
              framing_label: "full-body",
              has_person: true,
              occlusion_label: "face_not_visible",
              resolution_ok: true
            },
            qc_reasons: ["Face evidence was not detected for LoRA training."],
            qc_status: "warn",
            reason_codes: ["face_required_for_lora"],
            reason_messages: ["Face evidence was not detected for LoRA training."],
            usable_for_body: true,
            usable_for_lora: false
          },
          {
            accepted_for_character_use: true,
            artifact_urls: {
              normalized: "http://localhost:8010/api/v1/photosets/phase-02/normalized-b",
              original: "http://localhost:8010/api/v1/photosets/phase-02/original-b",
              thumbnail: "http://localhost:8010/api/v1/photosets/phase-02/thumbnail-b"
            },
            bucket: "both",
            original_filename: "female_head_front.png",
            photo_asset_public_id: "photo-b",
            public_id: "entry-b",
            qc_metrics: {
              blur_score: 144,
              body_detected: true,
              body_landmarks_detected: true,
              exposure_score: 101,
              face_detected: true,
              framing_label: "mid-body",
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
        entry_count: 3,
        ingest_job: {
          bucket_counts: {
            body_only: 1,
            both: 1,
            lora_only: 0,
            rejected: 1
          },
          job_public_id: "job-phase-02-preview",
          processed_files: 3,
          progress_percent: 100,
          status: "completed",
          step_name: "completed",
          total_files: 3
        },
        public_id: "photoset-phase-02",
        rejected_entry_count: 1,
        status: "prepared"
      }),
      contentType: "application/json",
      status: 200
    });
  });

  await page.route("**/api/v1/jobs/job-phase-02-preview", async (route) => {
    await route.fulfill({
      body: JSON.stringify({
        error_summary: null,
        finished_at: "2026-04-02T00:00:03Z",
        job_type: "photoset-ingest",
        output_asset_id: "asset-phase-02",
        output_storage_object_id: null,
        progress: {
          bucket_counts: {
            body_only: 1,
            both: 1,
            lora_only: 0,
            rejected: 1
          },
          processed_files: 3,
          total_files: 3
        },
        progress_percent: 100,
        public_id: "job-phase-02-preview",
        stage_history: [
          {
            bucket_counts: {
              body_only: 1,
              both: 1,
              lora_only: 0,
              rejected: 1
            },
            created_at: "2026-04-02T00:00:03Z",
            event_type: "job.completed",
            processed_files: 3,
            progress_percent: 100,
            status: "completed",
            step_name: "completed",
            total_files: 3
          }
        ],
        started_at: "2026-04-02T00:00:00Z",
        status: "completed",
        step_name: "completed"
      }),
      contentType: "application/json",
      status: 200
    });
  });

  await page.goto("/studio/characters/new?photoset=photoset-phase-02");

  await expect(
    page.getByRole("button", { name: "Inspect male_body_front.png" })
  ).toBeVisible();

  await page.getByRole("button", { name: "Inspect male_body_front.png" }).click();

  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole("img", { name: "Large preview of male_body_front.png" })).toBeVisible();
  await expect(dialog.getByText("body only")).toBeVisible();
  await expect(dialog.getByText("Face evidence was not detected for LoRA training.")).toBeVisible();
  await expect(dialog.getByText("Body detected")).toBeVisible();
  await expect(dialog.getByText("yes").first()).toBeVisible();

  await page.keyboard.press("Escape");
  await expect(dialog).toHaveCount(0);
});
