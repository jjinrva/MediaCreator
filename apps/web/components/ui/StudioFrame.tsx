import Link from "next/link";
import React from "react";

const NAV_ITEMS = [
  { href: "/", label: "Front door" },
  { href: "/studio", label: "Studio shell" },
  { href: "/studio/capture-guide", label: "Capture guide" },
  { href: "/studio/characters/new", label: "New character" }
];

type StudioFrameProps = {
  children: React.ReactNode;
  currentPath: string;
  phaseLabel: string;
  shellStyle?: React.CSSProperties;
};

export function StudioFrame({ children, currentPath, phaseLabel, shellStyle }: StudioFrameProps) {
  return (
    <main className="studioShell" style={shellStyle}>
      <aside className="studioNav" aria-label="Studio navigation">
        <div className="studioNavBrand">
          <span className="studioNavEyebrow">{phaseLabel}</span>
          <strong>MediaCreator Studio</strong>
        </div>
        <nav className="studioNavLinks" aria-label="Studio navigation">
          {NAV_ITEMS.map((item) => {
            const isActive = currentPath === item.href;
            const className = isActive ? "navLink navLinkActive" : "navLink";

            return (
              <Link
                key={item.href}
                href={item.href}
                className={className}
                aria-current={isActive ? "page" : undefined}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <p className="studioNavNote">
          This shell is truthful scaffolding only. No fake assets, counts, or jobs are shown here.
        </p>
      </aside>

      <div className="studioContent">{children}</div>
    </main>
  );
}
