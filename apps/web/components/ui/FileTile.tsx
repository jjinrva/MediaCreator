import React from "react";

type FileTileProps = {
  fileName: string;
  filePath: string;
  description: string;
};

export function FileTile({ fileName, filePath, description }: FileTileProps) {
  return (
    <article className="fileTile">
      <div className="fileTileHeader">
        <strong>{fileName}</strong>
        <code>{filePath}</code>
      </div>
      <p>{description}</p>
    </article>
  );
}
