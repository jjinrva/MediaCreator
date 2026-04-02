import React from "react";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { WardrobeCatalog } from "../../components/wardrobe-catalog/WardrobeCatalog";

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

const baseProps = {
  generationCapability: {
    detail:
      "ComfyUI is not ready, so AI wardrobe items are stored as prompt-backed catalog records without claiming a generated garment image.",
    missingRequirements: ["comfyui_base_url_missing"],
    status: "unavailable"
  },
  items: []
};

describe("Phase 22 wardrobe catalog", () => {
  it("posts the photo-ingest form to the wardrobe API", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      json: async () => ({ items: [{}] }),
      ok: true
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<WardrobeCatalog {...baseProps} />);

    const file = new File(["shirt"], "shirt.png", { type: "image/png" });
    fireEvent.change(screen.getByLabelText("Source photo"), {
      target: { files: [file] }
    });
    fireEvent.change(document.getElementById("wardrobe-photo-label") as HTMLInputElement, {
      target: { value: "Photo shirt" }
    });
    fireEvent.change(document.getElementById("wardrobe-photo-type") as HTMLInputElement, {
      target: { value: "shirt" }
    });
    fireEvent.change(document.getElementById("wardrobe-photo-material") as HTMLInputElement, {
      target: { value: "cotton" }
    });
    fireEvent.change(document.getElementById("wardrobe-photo-color") as HTMLInputElement, {
      target: { value: "navy" }
    });
    fireEvent.submit(
      screen.getByRole("button", { name: "Create wardrobe from photo" }).closest("form")!
    );

    await waitFor(() => {
      expect(String(fetchMock.mock.calls[0]?.[0])).toBe(
        "http://10.0.0.102:8010/api/v1/wardrobe/from-photo"
      );
      expect((fetchMock.mock.calls[0]?.[1] as { method: string }).method).toBe("POST");
      expect(refresh).toHaveBeenCalled();
    });
  });

  it("posts the prompt form to the wardrobe API", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      json: async () => ({ items: [{ creation_path: "ai-prompt" }] }),
      ok: true
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<WardrobeCatalog {...baseProps} />);

    fireEvent.change(document.getElementById("wardrobe-prompt-label") as HTMLInputElement, {
      target: { value: "Prompt jacket" }
    });
    fireEvent.change(document.getElementById("wardrobe-prompt-type") as HTMLInputElement, {
      target: { value: "jacket" }
    });
    fireEvent.change(
      document.getElementById("wardrobe-prompt-material") as HTMLInputElement,
      {
        target: { value: "leather" }
      }
    );
    fireEvent.change(document.getElementById("wardrobe-prompt-color") as HTMLInputElement, {
      target: { value: "brown" }
    });
    fireEvent.change(screen.getByLabelText("Prompt text"), {
      target: { value: "brown leather jacket" }
    });
    fireEvent.submit(
      screen.getByRole("button", { name: "Create wardrobe from prompt" }).closest("form")!
    );

    await waitFor(() => {
      expect(String(fetchMock.mock.calls[0]?.[0])).toBe(
        "http://10.0.0.102:8010/api/v1/wardrobe/from-prompt"
      );
      const init = fetchMock.mock.calls[0]?.[1] as {
        body: string;
        headers: { "content-type": string };
        method: string;
      };
      expect(init.method).toBe("POST");
      expect(init.headers["content-type"]).toBe("application/json");
      expect(init.body).toContain("brown leather jacket");
      expect(refresh).toHaveBeenCalled();
    });
  });
});
