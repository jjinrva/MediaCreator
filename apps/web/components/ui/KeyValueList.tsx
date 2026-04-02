import React from "react";

type KeyValueItem = {
  label: string;
  value: string;
};

type KeyValueListProps = {
  items: KeyValueItem[];
};

export function KeyValueList({ items }: KeyValueListProps) {
  return (
    <dl className="keyValueList">
      {items.map((item) => (
        <div key={item.label} className="keyValueRow">
          <dt>{item.label}</dt>
          <dd>{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}
