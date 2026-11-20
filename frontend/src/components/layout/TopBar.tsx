"use client";

import { Badge } from "@/components/ui/Badge";
import { useCrawlStore } from "@/store/crawl-store";

export function TopBar() {
  const status = useCrawlStore((state) => state.status);

  return (
    <header className="flex items-center justify-between border-b border-terminal-border bg-terminal-panel/60 px-4 py-3">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded border border-terminal-accent/40 bg-terminal-accent/10 text-sm text-terminal-accent">
          NS
        </div>
        <div>
          <p className="text-sm font-bold tracking-[0.3em] text-terminal-text">NEUROSPIDER</p>
          <p className="text-[10px] tracking-widest text-terminal-muted">
            VISUAL CRAWLER / AI EXTRACTION
          </p>
        </div>
      </div>
      <Badge tone={status === "completed" ? "signal" : status === "failed" ? "alert" : "accent"}>
        {status}
      </Badge>
    </header>
  );
}
