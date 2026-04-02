"use client";

import { useRouter } from "next/navigation";
import React from "react";

type GenerationWorkspaceProps = {
  characters: Array<{
    label: string;
    promptExpansion: string;
    promptHandle: string;
    publicId: string;
    status: string;
    trainingPromptStatus: string;
    visibleTags: string[];
  }>;
  civitaiImport: {
    baseUrl: string;
    detail: string;
    missingRequirements: string[];
    status: string;
  };
  externalLoras: Array<{
    characterPublicId: string | null;
    modelName: string;
    ownerLabel: string;
    promptHandle: string;
    registryPublicId: string;
    source: string;
    status: string;
    storagePath: string | null;
    toolkitName: string | null;
  }>;
  generationCapability: {
    detail: string;
    missingRequirements: string[];
    status: string;
  };
  localLoras: Array<{
    characterPublicId: string | null;
    modelName: string;
    ownerLabel: string;
    promptHandle: string;
    registryPublicId: string;
    source: string;
    status: string;
    storagePath: string | null;
    toolkitName: string | null;
  }>;
  recentRequests: Array<{
    createdAt: string;
    expandedPrompt: string;
    externalLora:
      | {
          modelName: string;
          registryPublicId: string;
        }
      | null;
    localLora:
      | {
          modelName: string;
          registryPublicId: string;
        }
      | null;
    matchedHandles: string[];
    providerStatus: string;
    publicId: string;
    rawPrompt: string;
    status: string;
    targetKind: string;
    workflowId: string;
    workflowPath: string;
  }>;
  workflowContracts: Array<{
    path: string;
    targetKind: string;
    workflowId: string;
  }>;
};

type SearchResult = {
  downloadUrl: string;
  modelName: string;
  promptHandle: string;
  versionName: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL ?? "http://10.0.0.102:8010";

function expandPrompt(
  promptText: string,
  characters: GenerationWorkspaceProps["characters"]
) {
  let expandedPrompt = promptText;
  const matchedHandles: string[] = [];
  const unresolvedHandles = (promptText.match(/@[a-z0-9_][a-z0-9_-]*/gi) ?? []).filter(
    (handle) => !characters.some((character) => character.promptHandle === handle)
  );

  for (const character of [...characters].sort(
    (left, right) => right.promptHandle.length - left.promptHandle.length
  )) {
    const pattern = new RegExp(
      `(?<!\\\\w)${character.promptHandle.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\\\$&")}(?!\\\\w)`,
      "g"
    );
    if (pattern.test(expandedPrompt)) {
      matchedHandles.push(character.promptHandle);
      expandedPrompt = expandedPrompt.replace(pattern, character.promptExpansion);
    }
  }

  return { expandedPrompt, matchedHandles, unresolvedHandles };
}

export function GenerationWorkspace({
  characters,
  civitaiImport,
  externalLoras,
  generationCapability,
  localLoras,
  recentRequests,
  workflowContracts
}: GenerationWorkspaceProps) {
  const router = useRouter();
  const [promptText, setPromptText] = React.useState("");
  const [targetKind, setTargetKind] = React.useState("image");
  const [localLoraId, setLocalLoraId] = React.useState("");
  const [externalLoraId, setExternalLoraId] = React.useState("");
  const [civitaiQuery, setCivitaiQuery] = React.useState("");
  const [searchResults, setSearchResults] = React.useState<SearchResult[]>([]);
  const [actionError, setActionError] = React.useState<string | null>(null);
  const [actionSummary, setActionSummary] = React.useState<string | null>(null);
  const [isSearching, setIsSearching] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [isImporting, setIsImporting] = React.useState(false);

  const promptPreview = expandPrompt(promptText, characters);

  async function handleStoreRequest(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!promptText.trim()) {
      setActionError("Enter a prompt before storing a generation request.");
      return;
    }

    try {
      setIsSubmitting(true);
      setActionError(null);
      setActionSummary(null);

      const response = await fetch(`${API_BASE_URL}/api/v1/generation/requests`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          external_lora_registry_public_id: externalLoraId || null,
          local_lora_registry_public_id: localLoraId || null,
          prompt_text: promptText,
          target_kind: targetKind
        })
      });
      const payload = (await response.json()) as { detail?: string };
      if (!response.ok) {
        throw new Error(payload.detail ?? "Unable to store the generation request.");
      }

      setActionSummary("Generation request stored.");
      router.refresh();
    } catch (error) {
      setActionError(
        error instanceof Error ? error.message : "Unable to store the generation request."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleSearchExternalLoras(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!civitaiQuery.trim()) {
      setActionError("Enter a Civitai search query first.");
      return;
    }

    try {
      setIsSearching(true);
      setActionError(null);
      const response = await fetch(
        `${API_BASE_URL}/api/v1/generation/external-loras/search?q=${encodeURIComponent(civitaiQuery)}`
      );
      const payload = (await response.json()) as { detail?: string; results?: SearchResult[] };
      if (!response.ok) {
        throw new Error(payload.detail ?? "Unable to search Civitai.");
      }

      setSearchResults(payload.results ?? []);
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "Unable to search Civitai.");
    } finally {
      setIsSearching(false);
    }
  }

  async function handleImportExternalLora(result: SearchResult) {
    try {
      setIsImporting(true);
      setActionError(null);
      setActionSummary(null);

      const response = await fetch(`${API_BASE_URL}/api/v1/generation/external-loras/import`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          download_url: result.downloadUrl,
          model_name: result.modelName,
          prompt_handle: result.promptHandle
        })
      });
      const payload = (await response.json()) as { detail?: string };
      if (!response.ok) {
        throw new Error(payload.detail ?? "Unable to import the external LoRA.");
      }

      setActionSummary("External LoRA imported into the internal registry.");
      router.refresh();
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "Unable to import the external LoRA.");
    } finally {
      setIsImporting(false);
    }
  }

  return (
    <div className="sectionCardBody">
      <div className="keyValueRow">
        <dt>Generation capability</dt>
        <dd>{generationCapability.status}</dd>
        <dd>{generationCapability.detail}</dd>
        <dd>
          {generationCapability.missingRequirements.length > 0
            ? `Missing requirements: ${generationCapability.missingRequirements.join(", ")}`
            : "No generation capability blockers detected."}
        </dd>
      </div>
      <div className="keyValueRow">
        <dt>Civitai import</dt>
        <dd>{civitaiImport.status}</dd>
        <dd>{civitaiImport.detail}</dd>
        <dd>{`Base URL: ${civitaiImport.baseUrl}`}</dd>
      </div>

      <div className="thumbnailGrid">
        <form className="thumbnailCard" onSubmit={(event) => void handleStoreRequest(event)}>
          <div className="thumbnailMeta fieldStack">
            <strong>Store generation request</strong>
            <label htmlFor="generation-prompt">Prompt</label>
            <textarea
              id="generation-prompt"
              className="textInput"
              rows={5}
              value={promptText}
              onChange={(event) => setPromptText(event.target.value)}
            />
            <label htmlFor="generation-target-kind">Target</label>
            <select
              id="generation-target-kind"
              className="textInput"
              value={targetKind}
              onChange={(event) => setTargetKind(event.target.value)}
            >
              <option value="image">Image</option>
              <option value="video">Video</option>
            </select>
            <label htmlFor="generation-local-lora">Local LoRA</label>
            <select
              id="generation-local-lora"
              className="textInput"
              value={localLoraId}
              onChange={(event) => setLocalLoraId(event.target.value)}
              disabled={localLoras.length === 0}
            >
              <option value="">No local LoRA</option>
              {localLoras.map((lora) => (
                <option key={lora.registryPublicId} value={lora.registryPublicId}>
                  {`${lora.modelName} (${lora.ownerLabel})`}
                </option>
              ))}
            </select>
            <label htmlFor="generation-external-lora">Imported external LoRA</label>
            <select
              id="generation-external-lora"
              className="textInput"
              value={externalLoraId}
              onChange={(event) => setExternalLoraId(event.target.value)}
              disabled={externalLoras.length === 0}
            >
              <option value="">No external LoRA</option>
              {externalLoras.map((lora) => (
                <option key={lora.registryPublicId} value={lora.registryPublicId}>
                  {lora.modelName}
                </option>
              ))}
            </select>
            <button type="submit" className="previewActionButton" disabled={isSubmitting}>
              {isSubmitting ? "Storing request..." : "Store generation request"}
            </button>
          </div>
        </form>

        <article className="thumbnailCard">
          <div className="thumbnailMeta fieldStack">
            <strong>Expanded prompt preview</strong>
            <span>{`Matched handles: ${promptPreview.matchedHandles.join(", ") || "none"}`}</span>
            <span>
              {`Unresolved handles: ${promptPreview.unresolvedHandles.join(", ") || "none"}`}
            </span>
            <pre className="promptAuditBlock" data-testid="expanded-prompt-preview">
              {promptPreview.expandedPrompt || "Type a prompt to preview the visible expansion."}
            </pre>
            <span>{`Image workflow: ${workflowContracts.find((item) => item.targetKind === "image")?.workflowId ?? "missing"}`}</span>
            <span>{`Video workflow: ${workflowContracts.find((item) => item.targetKind === "video")?.workflowId ?? "missing"}`}</span>
          </div>
        </article>
      </div>

      {actionError ? (
        <span className="previewActionError" role="alert">
          {actionError}
        </span>
      ) : null}
      {actionSummary ? (
        <span className="previewActionSummary" role="status">
          {actionSummary}
        </span>
      ) : null}

      <div className="thumbnailGrid">
        {characters.map((character) => (
          <article key={character.publicId} className="thumbnailCard">
            <div className="thumbnailMeta fieldStack">
              <strong>{character.label}</strong>
              <span>{character.promptHandle}</span>
              <span>{`Prompt contract: ${character.trainingPromptStatus}`}</span>
              <pre className="promptAuditBlock">{character.promptExpansion}</pre>
            </div>
          </article>
        ))}
      </div>

      <div className="thumbnailGrid">
        <article className="thumbnailCard">
          <div className="thumbnailMeta fieldStack">
            <strong>Local LoRA registry</strong>
            {localLoras.length > 0 ? (
              localLoras.map((lora) => (
                <span key={lora.registryPublicId}>{`${lora.modelName} -> ${lora.ownerLabel}`}</span>
              ))
            ) : (
              <span>No local LoRA entries are currently active.</span>
            )}
          </div>
        </article>

        <article className="thumbnailCard">
          <div className="thumbnailMeta fieldStack">
            <strong>External LoRA import</strong>
            {civitaiImport.status === "enabled" ? (
              <>
                <form onSubmit={(event) => void handleSearchExternalLoras(event)} className="fieldStack">
                  <label htmlFor="civitai-search-query">Search external LoRAs</label>
                  <input
                    id="civitai-search-query"
                    className="textInput"
                    value={civitaiQuery}
                    onChange={(event) => setCivitaiQuery(event.target.value)}
                  />
                  <button type="submit" className="previewActionButton" disabled={isSearching}>
                    {isSearching ? "Searching..." : "Search Civitai"}
                  </button>
                </form>
                {searchResults.map((result) => (
                  <div key={`${result.modelName}-${result.versionName}`} className="fieldStack">
                    <span>{`${result.modelName} (${result.versionName})`}</span>
                    <button
                      type="button"
                      className="previewActionButton"
                      disabled={isImporting}
                      onClick={() => void handleImportExternalLora(result)}
                    >
                      {isImporting ? "Importing..." : "Import"}
                    </button>
                  </div>
                ))}
              </>
            ) : (
              <span>{civitaiImport.detail}</span>
            )}
          </div>
        </article>
      </div>

      <div className="sectionCardBody">
        <strong>Recent requests</strong>
        {recentRequests.length > 0 ? (
          <ol className="historyList">
            {recentRequests.map((request) => (
              <li key={request.publicId} className="historyItem">
                <strong>{`${request.targetKind} -> ${request.status}`}</strong>
                <span>{request.rawPrompt}</span>
                <span>{request.expandedPrompt}</span>
                <span>{`Provider: ${request.providerStatus}`}</span>
                <span>
                  {`Local LoRA: ${request.localLora?.modelName ?? "none"} | External LoRA: ${request.externalLora?.modelName ?? "none"}`}
                </span>
              </li>
            ))}
          </ol>
        ) : (
          <p>No generation requests have been stored yet.</p>
        )}
      </div>
    </div>
  );
}
