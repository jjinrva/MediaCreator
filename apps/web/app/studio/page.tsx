"use client";

import Link from "next/link";
import React from "react";

import { EmptyState } from "../../components/ui/EmptyState";
import { FileTile } from "../../components/ui/FileTile";
import { HistoryList } from "../../components/ui/HistoryList";
import { InfoTooltip } from "../../components/ui/InfoTooltip";
import { KeyValueList } from "../../components/ui/KeyValueList";
import { NumericSliderField } from "../../components/ui/NumericSliderField";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionCard } from "../../components/ui/SectionCard";
import { StudioFrame } from "../../components/ui/StudioFrame";
import type { FieldMetadata } from "../../components/ui/field-metadata";

type ThemeName = "dawn" | "midnight";
type StudioTab = "controls" | "contracts" | "history";

const TABS: Array<{ id: StudioTab; label: string }> = [
  { id: "controls", label: "Shell controls" },
  { id: "contracts", label: "Contracts" },
  { id: "history", label: "Verified milestones" }
];

const LAYOUT_FOCUS_FIELD: FieldMetadata & {
  min: number;
  max: number;
  step: number;
  suffix: string;
} = {
  id: "layout-focus",
  label: "Layout focus",
  helpText:
    "Adjusts the navigation column width for this Phase 07 shell only. It is not saved to production data.",
  min: 24,
  max: 34,
  step: 1,
  suffix: "%"
};

const WORKSPACE_LABEL_FIELD: FieldMetadata = {
  id: "workspace-label",
  label: "Workspace label",
  helpText:
    "A local shell label for the page header. It exists only in this browser session and is not persisted."
};

const CONTRACT_ITEMS = [
  { label: "Mode", value: "Single-user rebuild" },
  { label: "Queue", value: "PostgreSQL-backed jobs active" },
  { label: "Generation", value: "Capability gated by /api/v1/system/status" },
  { label: "Storage", value: "NAS-backed canonical roots with degraded local-only fallback" }
];

const HISTORY_ITEMS = [
  {
    label: "Phase 04",
    detail: "Migration-backed schema verified with the seeded god actor and UUID contracts."
  },
  {
    label: "Phase 05",
    detail: "Durable PostgreSQL dequeue and job history verification passed."
  },
  {
    label: "Phase 06",
    detail: "ComfyUI capability reporting, workflow contracts, and NAS model-root checks passed."
  }
];

const WORKFLOW_FILES = [
  {
    fileName: "text_to_image_v1.json",
    filePath: "workflows/comfyui/text_to_image_v1.json",
    description: "Baseline text-to-image capability contract placeholder."
  },
  {
    fileName: "character_refine_img2img_v1.json",
    filePath: "workflows/comfyui/character_refine_img2img_v1.json",
    description: "Character refinement placeholder reserved for later phases."
  }
];

function MetadataTextField({
  field,
  value,
  onChange
}: {
  field: FieldMetadata;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="fieldStack">
      <div className="fieldHeader">
        <label htmlFor={field.id} className="fieldLabel">
          {field.label}
        </label>
        <InfoTooltip content={field.helpText} label={field.label} />
      </div>
      <input
        id={field.id}
        className="textInput"
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Phase 07 shell label"
      />
    </div>
  );
}

export default function StudioPage() {
  const [theme, setTheme] = React.useState<ThemeName>("dawn");
  const [activeTab, setActiveTab] = React.useState<StudioTab>("controls");
  const [layoutFocus, setLayoutFocus] = React.useState<number>(28);
  const [workspaceLabel, setWorkspaceLabel] = React.useState<string>("Studio shell");

  React.useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  const activeTabIndex = TABS.findIndex((tab) => tab.id === activeTab);

  function handleTabKeyDown(
    event: React.KeyboardEvent<HTMLButtonElement>,
    currentIndex: number
  ) {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft" && event.key !== "Home" && event.key !== "End") {
      return;
    }

    event.preventDefault();

    if (event.key === "Home") {
      setActiveTab(TABS[0].id);
      return;
    }

    if (event.key === "End") {
      setActiveTab(TABS[TABS.length - 1].id);
      return;
    }

    const direction = event.key === "ArrowRight" ? 1 : -1;
    const nextIndex = (currentIndex + direction + TABS.length) % TABS.length;
    setActiveTab(TABS[nextIndex].id);
  }

  return (
    <StudioFrame
      currentPath="/studio"
      phaseLabel="Phase 07"
      shellStyle={{ ["--studio-nav-width" as string]: `${layoutFocus}%` }}
    >
      <div className="statusStrip" role="status" aria-live="polite">
        <span className="statusBadge">single-user</span>
        <span className="statusBadge">jobs verified</span>
        <span className="statusBadge">generation gated</span>
        <button
          type="button"
          className="themeToggle"
          onClick={() => setTheme(theme === "dawn" ? "midnight" : "dawn")}
        >
          {theme === "dawn" ? "Switch to midnight" : "Switch to dawn"}
        </button>
      </div>

      <PageHeader
        eyebrow={workspaceLabel}
        title="Studio shell"
        summary="This route establishes the permanent MediaCreator shell: navigation, status strip, reusable cards, tabs, and the info-tooltip rule for every visible input."
        actions={<span className="headerCallout">No runtime demo data is seeded here.</span>}
      />

      <div className="tabList" role="tablist" aria-label="Studio sections">
        {TABS.map((tab, index) => (
          <button
            key={tab.id}
            id={`${tab.id}-tab`}
            type="button"
            role="tab"
            className={tab.id === activeTab ? "tabButton tabButtonActive" : "tabButton"}
            aria-selected={tab.id === activeTab}
            aria-controls={`${tab.id}-panel`}
            tabIndex={tab.id === activeTab ? 0 : -1}
            onClick={() => setActiveTab(tab.id)}
            onKeyDown={(event) => handleTabKeyDown(event, index)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <section
        id="controls-panel"
        role="tabpanel"
        aria-labelledby="controls-tab"
        hidden={activeTab !== "controls"}
        className="studioPanelGrid"
      >
        <SectionCard
          title="Shell controls"
          description="Phase 07 keeps the visible controls local to the shell and labels each control with a permanent info icon."
        >
          <NumericSliderField
            field={LAYOUT_FOCUS_FIELD}
            value={layoutFocus}
            onChange={setLayoutFocus}
          />
          <MetadataTextField
            field={WORKSPACE_LABEL_FIELD}
            value={workspaceLabel}
            onChange={setWorkspaceLabel}
          />
        </SectionCard>

        <SectionCard
          title="Current state"
          description="Truthful shell status only, without fabricated counts."
        >
          <KeyValueList items={CONTRACT_ITEMS} />
          <EmptyState
            title="No character selected yet"
            description="Character creation, editing, and generation surfaces arrive in later verified phases."
          />
        </SectionCard>
      </section>

      <section
        id="contracts-panel"
        role="tabpanel"
        aria-labelledby="contracts-tab"
        hidden={activeTab !== "contracts"}
        className="studioPanelGrid"
      >
        <SectionCard
          title="Workflow contracts"
          description="These tracked workflow files are real repository contracts, not generated samples."
        >
          <div className="fileTileGrid">
            {WORKFLOW_FILES.map((file) => (
              <FileTile
                key={file.fileName}
                fileName={file.fileName}
                filePath={file.filePath}
                description={file.description}
              />
            ))}
          </div>
        </SectionCard>

        <SectionCard
          title="Capability notes"
          description="The shell reflects the backend contract instead of guessing generation readiness."
        >
          <KeyValueList
            items={[
              { label: "System route", value: "GET /api/v1/system/status" },
              { label: "Tooltip rule", value: "Every visible slider and textbox has an info icon" },
              { label: "Accessibility", value: "Tabs, nav links, and buttons expose user-facing names" }
            ]}
          />
        </SectionCard>
      </section>

      <section
        id="history-panel"
        role="tabpanel"
        aria-labelledby="history-tab"
        hidden={activeTab !== "history"}
        className="studioPanelGrid"
      >
        <SectionCard
          title="Verified milestones"
          description="These are truthful project milestones already verified in earlier phases."
        >
          <HistoryList items={HISTORY_ITEMS} />
        </SectionCard>
      </section>

      <footer className="studioFooter">
        <span>Active tab {activeTabIndex + 1} of {TABS.length}</span>
        <Link href="/" className="inlineLink">
          Return to front door
        </Link>
      </footer>
    </StudioFrame>
  );
}
