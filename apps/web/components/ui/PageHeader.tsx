import React from "react";

type PageHeaderProps = {
  eyebrow: string;
  title: string;
  summary: string;
  actions?: React.ReactNode;
};

export function PageHeader({ eyebrow, title, summary, actions }: PageHeaderProps) {
  return (
    <header className="pageHeader">
      <div>
        <span className="pageHeaderEyebrow">{eyebrow}</span>
        <h1 className="pageHeaderTitle">{title}</h1>
        <p className="pageHeaderSummary">{summary}</p>
      </div>
      {actions ? <div className="pageHeaderActions">{actions}</div> : null}
    </header>
  );
}
