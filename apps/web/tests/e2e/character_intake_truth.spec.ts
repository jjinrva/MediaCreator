import { expect, test } from "@playwright/test";

const SAMPLE_FILES = [
  "/opt/MediaCreator/docs/capture_guides/assets/male_head_front.png",
  "/opt/MediaCreator/docs/capture_guides/assets/female_head_front.png"
];

function preparedPhotosetPayload() {
  return {
    accepted_entry_count: 2,
    bucket_counts: {
      body_only: 1,
      both: 1,
      lora_only: 0,
      rejected: 0
    },
    character_label: "Repeat Label",
    entries: [
      {
        accepted_for_character_use: true,
        artifact_urls: {
          normalized: "http://localhost:8010/api/v1/photosets/phase-02/normalized-a",
          original: "http://localhost:8010/api/v1/photosets/phase-02/original-a",
          thumbnail: "http://localhost:8010/api/v1/photosets/phase-02/thumbnail-a"
        },
        bucket: "body_only",
        original_filename: "male_head_front.png",
        photo_asset_public_id: "photo-a",
        public_id: "entry-a",
        qc_metrics: {
          blur_score: 102,
          body_detected: true,
          body_landmarks_detected: true,
          exposure_score: 99,
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
          blur_score: 148,
          body_detected: true,
          body_landmarks_detected: true,
          exposure_score: 104,
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
    entry_count: 2,
    ingest_job: {
      bucket_counts: {
        body_only: 1,
        both: 1,
        lora_only: 0,
        rejected: 0
      },
      job_public_id: "job-phase-02",
      processed_files: 2,
      progress_percent: 100,
      status: "completed",
      step_name: "completed",
      total_files: 2
    },
    public_id: "photoset-phase-02",
    rejected_entry_count: 0,
    status: "prepared"
  };
}

test("character intake requires a label, shows stage-aware progress, and gates character creation", async ({
  page
}) => {
  let jobPollCount = 0;

  await page.route("**/api/v1/photosets", async (route) => {
    await route.fulfill({
      body: JSON.stringify({
        accepted_entry_count: 0,
        bucket_counts: {
          body_only: 0,
          both: 0,
          lora_only: 0,
          rejected: 0
        },
        character_label: "Repeat Label",
        entries: [],
        entry_count: 2,
        ingest_job: {
          bucket_counts: {
            body_only: 0,
            both: 0,
            lora_only: 0,
            rejected: 0
          },
          job_public_id: "job-phase-02",
          processed_files: 0,
          progress_percent: 5,
          status: "running",
          step_name: "upload_received",
          total_files: 2
        },
        public_id: "photoset-phase-02",
        rejected_entry_count: 0,
        status: "ingesting"
      }),
      contentType: "application/json",
      status: 201
    });
  });

  await page.route("**/api/v1/jobs/job-phase-02", async (route) => {
    jobPollCount += 1;
    if (jobPollCount === 1) {
      await route.fulfill({
        body: JSON.stringify({
          error_summary: null,
          finished_at: null,
          job_type: "photoset-ingest",
          output_asset_id: "asset-phase-02",
          output_storage_object_id: null,
          progress: {
            bucket_counts: {
              body_only: 1,
              both: 0,
              lora_only: 0,
              rejected: 0
            },
            processed_files: 1,
            total_files: 2
          },
          progress_percent: 60,
          public_id: "job-phase-02",
          stage_history: [
            {
              bucket_counts: {
                body_only: 0,
                both: 0,
                lora_only: 0,
                rejected: 0
              },
              created_at: "2026-04-02T00:00:00Z",
              event_type: "job.running",
              processed_files: 0,
              progress_percent: 1,
              status: "running",
              step_name: "upload_received",
              total_files: 2
            },
            {
              bucket_counts: {
                body_only: 1,
                both: 0,
                lora_only: 0,
                rejected: 0
              },
              created_at: "2026-04-02T00:00:01Z",
              event_type: "job.progressed",
              processed_files: 1,
              progress_percent: 60,
              status: "running",
              step_name: "classification",
              total_files: 2
            }
          ],
          started_at: "2026-04-02T00:00:00Z",
          status: "running",
          step_name: "classification"
        }),
        contentType: "application/json",
        status: 200
      });
      return;
    }

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
            rejected: 0
          },
          processed_files: 2,
          total_files: 2
        },
        progress_percent: 100,
        public_id: "job-phase-02",
        stage_history: [
          {
            bucket_counts: {
              body_only: 1,
              both: 1,
              lora_only: 0,
              rejected: 0
            },
            created_at: "2026-04-02T00:00:03Z",
            event_type: "job.completed",
            processed_files: 2,
            progress_percent: 100,
            status: "completed",
            step_name: "completed",
            total_files: 2
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

  await page.route("**/api/v1/photosets/photoset-phase-02", async (route) => {
    await route.fulfill({
      body: JSON.stringify(preparedPhotosetPayload()),
      contentType: "application/json",
      status: 200
    });
  });

  await page.goto("/studio/characters/new");

  await page.getByTestId("photoset-input").setInputFiles(SAMPLE_FILES);
  await expect(page.getByRole("button", { name: "Upload photoset" })).toBeDisabled();

  await page.getByRole("textbox", { name: "Character label" }).fill("Repeat Label");
  await expect(page.getByRole("button", { name: "Upload photoset" })).toBeEnabled();

  await page.getByRole("button", { name: "Upload photoset" }).click();

  const buildButton = page.getByRole("button", { name: "Build base character" });
  const bucketSummary = page.locator("[data-testid='bucket-summary']");
  await expect(buildButton).toBeDisabled();
  await expect(page.getByText("classification", { exact: true })).toBeVisible();
  await expect(page.getByText("1 / 2 processed")).toBeVisible();
  await expect(bucketSummary).toContainText("body only");

  await expect(buildButton).toBeEnabled();
  await expect(page.getByText("2 accepted", { exact: true })).toBeVisible();
  await expect(page.getByText("0 rejected", { exact: true })).toBeVisible();
  await expect(page.getByText("pass and warn can build")).toBeVisible();
  await expect(bucketSummary).toContainText("body only");
  await expect(bucketSummary).toContainText("both");
  await expect(bucketSummary).toContainText("lora only");
  await expect(bucketSummary).toContainText("rejected");
});
