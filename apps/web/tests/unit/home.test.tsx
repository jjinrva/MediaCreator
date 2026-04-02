import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HomePage from "../../app/page";

describe("HomePage", () => {
  it("renders a truthful MediaCreator bootstrap placeholder", () => {
    render(<HomePage />);

    expect(screen.getByRole("heading", { name: "MediaCreator" })).toBeTruthy();
    expect(screen.getByRole("link", { name: "Open studio shell" })).toBeTruthy();
    expect(screen.getByText(/single-user mode/i)).toBeTruthy();
    expect(screen.getByText(/accessible tabs, shared UI primitives/i)).toBeTruthy();
    expect(screen.getByText(/Generation stays unavailable until ComfyUI/i)).toBeTruthy();
    expect(screen.getByText(/mounted NAS root/i)).toBeTruthy();
    expect(screen.getByText(/claims PostgreSQL-backed jobs/i)).toBeTruthy();
  });
});
