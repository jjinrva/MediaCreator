import React from "react";

type EmptyStateProps = {
  title: string;
  description: string;
};

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="emptyState" role="status" aria-live="polite">
      <strong className="emptyStateTitle">{title}</strong>
      <p className="emptyStateDescription">{description}</p>
    </div>
  );
}
