"use client";

import { useEffect } from "react";

import { streamUrl } from "@/lib/api";
import type { StreamEvent } from "@/lib/types";
import { useCrawlStore } from "@/store/crawl-store";

const EVENT_TYPES = ["status", "node", "table", "summary", "error", "done"] as const;

export function useCrawlStream(): void {
  const crawlId = useCrawlStore((state) => state.crawlId);
  const applyEvent = useCrawlStore((state) => state.applyEvent);

  useEffect(() => {
    if (!crawlId) {
      return;
    }

    const source = new EventSource(streamUrl(crawlId));

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
  }, [crawlId, applyEvent]);
}
