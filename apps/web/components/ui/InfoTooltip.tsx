"use client";

import * as Tooltip from "@radix-ui/react-tooltip";
import React from "react";

type InfoTooltipProps = {
  content: string;
  label: string;
};

export function InfoTooltip({ content, label }: InfoTooltipProps) {
  return (
    <Tooltip.Provider delayDuration={120}>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>
          <button
            type="button"
            className="infoTrigger"
            aria-label={`More info about ${label}`}
          >
            i
          </button>
        </Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content className="tooltipCard" sideOffset={10}>
            <p>{content}</p>
            <Tooltip.Arrow className="tooltipArrow" width={14} height={8} />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
}
