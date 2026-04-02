import React from "react";

export type RuntimeGenerationCapability = {
  checkpointsRoot: string;
  comfyuiBaseUrl: string | null;
  comfyuiBaseUrlConfigured: boolean;
  comfyuiServiceReachable: boolean;
  discoveredWorkflowFiles: string[];
  embeddingsRoot: string;
  lorasRoot: string;
  missingRequirements: string[];
  modelRootsOnNas: boolean;
  requiredWorkflowFiles: string[];
  status: string;
  vaesRoot: string;
  workflowsRoot: string;
};

export type RuntimeBlenderCapability = {
  blenderBin: string;
  detail: string;
  status: string;
};

export type RuntimeAiToolkitCapability = {
  aiToolkitBin: string | null;
  detail: string;
  lorasRoot: string;
  missingRequirements: string[];
  status: string;
};

export type RuntimeStoragePaths = {
  characterAssetsRoot: string;
  checkpointsRoot: string;
  embeddingsRoot: string;
  exportsRoot: string;
  lorasRoot: string;
  modelsRoot: string;
  nasRoot: string;
  preparedImagesRoot: string;
  rendersRoot: string;
  scratchRoot: string;
  uploadedPhotosRoot: string;
  vaesRoot: string;
  wardrobeRoot: string;
};

type RuntimeSettingsPanelProps = {
  aiToolkit: RuntimeAiToolkitCapability;
  blender: RuntimeBlenderCapability;
  generation: RuntimeGenerationCapability;
  nasAvailable: boolean;
  storageMode: string;
  storagePaths: RuntimeStoragePaths;
};

function statusClassName(status: string): string {
  if (status === "ready") {
    return "runtimeStatusChip runtimeStatusChipReady";
  }
  if (status === "unavailable" || status === "missing" || status === "fail") {
    return "runtimeStatusChip runtimeStatusChipFail";
  }
  return "runtimeStatusChip runtimeStatusChipWarn";
}

function formatList(values: string[]): string {
  if (values.length === 0) {
    return "none";
  }
  return values.join(", ");
}

function RuntimeMetaList({ items }: { items: Array<{ label: string; value: string }> }) {
  return (
    <dl className="runtimeMetaList">
      {items.map((item) => (
        <div key={`${item.label}-${item.value}`} className="runtimeMetaRow">
          <dt>{item.label}</dt>
          <dd>{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}

export function RuntimeSettingsPanel({
  aiToolkit,
  blender,
  generation,
  nasAvailable,
  storageMode,
  storagePaths
}: RuntimeSettingsPanelProps) {
  return (
    <div className="runtimePanelGrid">
      <article className="runtimePanel">
        <div className="runtimePanelHeader">
          <div>
            <h3>ComfyUI generation</h3>
            <p>Single-user runtime only. No fake readiness is shown here.</p>
          </div>
          <span className={statusClassName(generation.status)}>{generation.status}</span>
        </div>
        <RuntimeMetaList
          items={[
            {
              label: "Base URL",
              value: generation.comfyuiBaseUrl ?? "not configured"
            },
            {
              label: "Service reachable",
              value: generation.comfyuiServiceReachable ? "yes" : "no"
            },
            {
              label: "Workflow root",
              value: generation.workflowsRoot
            },
            {
              label: "Required workflows",
              value: formatList(generation.requiredWorkflowFiles)
            },
            {
              label: "Discovered workflows",
              value: formatList(generation.discoveredWorkflowFiles)
            },
            {
              label: "Missing requirements",
              value: formatList(generation.missingRequirements)
            },
            {
              label: "Model roots on NAS",
              value: generation.modelRootsOnNas ? "yes" : "no"
            }
          ]}
        />
      </article>

      <article className="runtimePanel">
        <div className="runtimePanelHeader">
          <div>
            <h3>Blender runtime</h3>
            <p>The 3D runtime stays tied to Blender for preview and video jobs.</p>
          </div>
          <span className={statusClassName(blender.status)}>{blender.status}</span>
        </div>
        <RuntimeMetaList
          items={[
            { label: "Blender binary", value: blender.blenderBin },
            { label: "Detail", value: blender.detail }
          ]}
        />
      </article>

      <article className="runtimePanel">
        <div className="runtimePanelHeader">
          <div>
            <h3>AI Toolkit</h3>
            <p>Local LoRA training is exposed only when the trainer really exists.</p>
          </div>
          <span className={statusClassName(aiToolkit.status)}>{aiToolkit.status}</span>
        </div>
        <RuntimeMetaList
          items={[
            {
              label: "Trainer binary",
              value: aiToolkit.aiToolkitBin ?? "not installed"
            },
            { label: "LoRA root", value: aiToolkit.lorasRoot },
            { label: "Missing requirements", value: formatList(aiToolkit.missingRequirements) },
            { label: "Detail", value: aiToolkit.detail }
          ]}
        />
      </article>

      <article className="runtimePanel runtimePanelWide">
        <div className="runtimePanelHeader">
          <div>
            <h3>Storage paths</h3>
            <p>These are the active runtime roots for this single-user build.</p>
          </div>
          <span className={statusClassName(nasAvailable ? "ready" : "partially-configured")}>
            {nasAvailable ? storageMode : "local-only"}
          </span>
        </div>
        <RuntimeMetaList
          items={[
            { label: "Storage mode", value: storageMode },
            { label: "NAS root", value: storagePaths.nasRoot },
            { label: "Scratch root", value: storagePaths.scratchRoot },
            { label: "Uploads root", value: storagePaths.uploadedPhotosRoot },
            { label: "Prepared images root", value: storagePaths.preparedImagesRoot },
            { label: "Character assets root", value: storagePaths.characterAssetsRoot },
            { label: "Exports root", value: storagePaths.exportsRoot },
            { label: "Renders root", value: storagePaths.rendersRoot },
            { label: "Wardrobe root", value: storagePaths.wardrobeRoot },
            { label: "Models root", value: storagePaths.modelsRoot },
            { label: "Checkpoints root", value: generation.checkpointsRoot },
            { label: "LoRAs root", value: generation.lorasRoot },
            { label: "Embeddings root", value: generation.embeddingsRoot },
            { label: "VAEs root", value: generation.vaesRoot }
          ]}
        />
      </article>
    </div>
  );
}
