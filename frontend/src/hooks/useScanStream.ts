"use client";

import { useEffect } from "react";

import { streamUrl } from "@/lib/api";
import type { StreamEvent } from "@/lib/types";
import { useScanStore } from "@/store/scan-store";

const EVENT_TYPES = ["status", "node", "finding", "summary", "error", "done"] as const;

export function useScanStream(): void {
  const scanId = useScanStore((state) => state.scanId);
  const applyEvent = useScanStore((state) => state.applyEvent);

  useEffect(() => {
    if (!scanId) {
      return;
    }

    const source = new EventSource(streamUrl(scanId));

    const handler = (event: Event) => {
      const message = event as MessageEvent<string>;

      try {
        applyEvent(JSON.parse(message.data) as StreamEvent);
      } catch {
        return;
      }
    };

    EVENT_TYPES.forEach((type) => source.addEventListener(type, handler));

    return () => {
      EVENT_TYPES.forEach((type) => source.removeEventListener(type, handler));
      source.close();
    };
  }, [scanId, applyEvent]);
}
