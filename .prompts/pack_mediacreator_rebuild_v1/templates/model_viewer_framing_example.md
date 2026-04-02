
# `<model-viewer>` framing example

Use the existing viewer stack and recompute framing after load and after transform-changing updates.

```tsx
'use client';

import { useEffect, useRef } from 'react';

type ModelViewerElement = HTMLElement & {
  updateFraming?: () => void;
  dismissPoster?: () => void;
};

export function GlbPreview({ src, refreshKey }: { src: string; refreshKey: string }) {
  const ref = useRef<ModelViewerElement | null>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const handleLoad = () => {
      el.dismissPoster?.();
      el.updateFraming?.();
    };

    el.addEventListener('load', handleLoad);
    return () => el.removeEventListener('load', handleLoad);
  }, [src]);

  useEffect(() => {
    ref.current?.updateFraming?.();
  }, [refreshKey]);

  return (
    <model-viewer
      ref={ref as any}
      src={src}
      camera-controls
      ar={false}
      exposure="1"
      shadow-intensity="1"
      style={{ width: '100%', height: '100%', minHeight: 480 }}
    />
  );
}
```
