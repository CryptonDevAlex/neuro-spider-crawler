"use client";

import { formatNumber } from "@/lib/utils";
import { useScanStore } from "@/store/scan-store";

export function StatusBar() {
  const phase = useScanStore((state) => state.phase);
  const pagesDone = useScanStore((state) => state.pagesDone);
  const pagesTotal = useScanStore((state) => state.pagesTotal);
  const findingsTotal = useScanStore((state) => state.findingsTotal);
  const error = useScanStore((state) => state.error);

  return (
    <footer className="flex items-center justify-between gap-4 border-t border-terminal-border bg-terminal-panel/60 px-4 py-2 text-[10px] uppercase tracking-widest text-terminal-muted">
      <span className="truncate">{error ?? `fase: ${phase}`}</span>
      <span>
        páginas {pagesDone}/{pagesTotal} · hallazgos {formatNumber(findingsTotal)} · backend :8000
      </span>
    </footer>
  );
}
