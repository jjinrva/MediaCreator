
# Numeric slider field example

Use this pattern for every numeric body/pose field.

```tsx
'use client';

import * as Slider from '@radix-ui/react-slider';
import * as Tooltip from '@radix-ui/react-tooltip';

type NumericSliderFieldProps = {
  id: string;
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  help: string;
  unit?: string;
  onChange: (value: number) => void;
  onCommit: (value: number) => void;
};

export function NumericSliderField(props: NumericSliderFieldProps) {
  const { id, label, value, min, max, step, help, unit, onChange, onCommit } = props;

  return (
    <div className="field">
      <div className="fieldHeader">
        <label htmlFor={id}>{label}</label>
        <Tooltip.Provider delayDuration={150}>
          <Tooltip.Root>
            <Tooltip.Trigger asChild>
              <button type="button" aria-label={`${label} help`} className="infoButton">i</button>
            </Tooltip.Trigger>
            <Tooltip.Portal>
              <Tooltip.Content side="top" sideOffset={6}>
                {help}
                <Tooltip.Arrow />
              </Tooltip.Content>
            </Tooltip.Portal>
          </Tooltip.Root>
        </Tooltip.Provider>
      </div>

      <div className="fieldValue">
        <output aria-live="polite">{value}{unit ? ` ${unit}` : ''}</output>
      </div>

      <Slider.Root
        id={id}
        min={min}
        max={max}
        step={step}
        value={[value]}
        onValueChange={(values) => onChange(values[0])}
        onValueCommit={(values) => onCommit(values[0])}
      >
        <Slider.Track>
          <Slider.Range />
        </Slider.Track>
        <Slider.Thumb aria-label={label} />
      </Slider.Root>
    </div>
  );
}
```
