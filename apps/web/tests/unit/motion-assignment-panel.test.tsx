import React from "react";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { MotionAssignmentPanel } from "../../components/motion-assignment-panel/MotionAssignmentPanel";

const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    refresh
  })
}));

beforeEach(() => {
  refresh.mockReset();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("Phase 23 motion assignment panel", () => {
  it("assigns a selected motion clip to a character", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      json: async () => ({}),
      ok: true
    });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <MotionAssignmentPanel
        characters={[
          {
            currentMotion: null,
            label: "Motion test character",
            publicId: "character-1",
            status: "base-created"
          }
        ]}
        importNote="Mixamo stays optional."
        motionLibrary={[
          {
            actionPayloadPath: "/opt/MediaCreator/motions/library/idle.json",
            compatibleRigClass: "rigify-human-v1",
            durationSeconds: 2,
            externalImportNote: "optional later",
            name: "Idle",
            publicId: "motion-idle",
            recommendedExternalSource: "Mixamo",
            slug: "idle",
            source: "local-seeded"
          },
          {
            actionPayloadPath: "/opt/MediaCreator/motions/library/walk.json",
            compatibleRigClass: "rigify-human-v1",
            durationSeconds: 1.6,
            externalImportNote: "optional later",
            name: "Walk",
            publicId: "motion-walk",
            recommendedExternalSource: "Mixamo",
            slug: "walk",
            source: "local-seeded"
          }
        ]}
      />
    );

    fireEvent.change(screen.getByLabelText("Motion clip"), {
      target: { value: "motion-walk" }
    });
    fireEvent.submit(screen.getByRole("button", { name: "Assign motion" }).closest("form")!);

    await waitFor(() => {
      expect(String(fetchMock.mock.calls[0]?.[0])).toBe(
        "http://localhost:8010/api/v1/motion/characters/character-1"
      );
      expect((fetchMock.mock.calls[0]?.[1] as { method: string }).method).toBe("PUT");
      expect(refresh).toHaveBeenCalled();
    });
  });
});
