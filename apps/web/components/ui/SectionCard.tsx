import React from "react";

type SectionCardProps = {
  title: string;
  description?: string;
  children: React.ReactNode;
};

export function SectionCard({ title, description, children }: SectionCardProps) {
  const headingId = `${title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-heading`;

  return (
    <section className="sectionCard" aria-labelledby={headingId}>
      <div className="sectionCardHeader">
        <h2 id={headingId} className="sectionCardTitle">
          {title}
        </h2>
        {description ? <p className="sectionCardDescription">{description}</p> : null}
      </div>
      <div className="sectionCardBody">{children}</div>
    </section>
  );
}
