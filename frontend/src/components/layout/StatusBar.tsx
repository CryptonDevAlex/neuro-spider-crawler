"use client";

import { useCrawlStore } from "@/store/crawl-store";

export function StatusBar() {
  const phase = useCrawlStore((state) => state.phase);
  const pagesDone = useCrawlStore((state) => state.pagesDone);
  const pagesTotal = useCrawlStore((state) => state.pagesTotal);
  const error = useCrawlStore((state) => state.error);

  return (
    <footer className="flex items-center justify-between gap-4 border-t border-terminal-border bg-terminal-panel/60 px-4 py-2 text-[10px] uppercase tracking-widest text-terminal-muted">
      <span className="truncate">{error ?? `fase: ${phase}`}</span>
      <span>
        páginas {pagesDone}/{pagesTotal} · backend :8000
      </span>
    </footer>
  );
}
