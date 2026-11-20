"use client";

import { useCrawlStore } from "@/store/crawl-store";

export function useCrawlState() {
  return useCrawlStore();
}
