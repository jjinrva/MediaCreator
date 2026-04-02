import React from "react";

type HistoryItem = {
  label: string;
  detail: string;
};

type HistoryListProps = {
  items: HistoryItem[];
};

export function HistoryList({ items }: HistoryListProps) {
  return (
    <ol className="historyList">
      {items.map((item) => (
        <li key={item.label} className="historyItem">
          <strong>{item.label}</strong>
          <span>{item.detail}</span>
        </li>
      ))}
    </ol>
  );
}
