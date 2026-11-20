"use client";

import { Badge } from "@/components/ui/Badge";
import { useScanStore } from "@/store/scan-store";
import { useUiStore, type SuiteView } from "@/store/ui-store";

const views: { id: SuiteView; label: string }[] = [
  { id: "recon", label: "RECONOCIMIENTO" },
  { id: "history", label: "HISTORIAL & DIFF" },
  { id: "monitoring", label: "VIGILANCIA 24/7" },
];

export function TopBar() {
  const status = useScanStore((state) => state.status);
  const view = useUiStore((state) => state.view);
  const setView = useUiStore((state) => state.setView);

  return (
    <header className="flex flex-wrap items-center justify-between gap-3 border-b border-terminal-border bg-terminal-panel/60 px-4 py-3">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded border border-terminal-accent/40 bg-terminal-accent/10 text-sm text-terminal-accent">
          NS
        </div>
        <div>
          <p className="text-sm font-bold tracking-[0.3em] text-terminal-text">NEUROSPIDER</p>
          <p className="text-[10px] tracking-widest text-terminal-muted">
            PASSIVE RECON / OSINT AUTHORIZED
          </p>
        </div>
      </div>
      <nav className="flex flex-wrap gap-2">
        {views.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setView(item.id)}
            className={`rounded border px-3 py-1.5 text-[10px] font-semibold uppercase tracking-widest transition-colors ${
              view === item.id
                ? "border-terminal-accent bg-terminal-accent/10 text-terminal-accent"
                : "border-terminal-border text-terminal-muted hover:text-terminal-text"
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>
      <Badge tone={status === "completed" ? "signal" : status === "failed" ? "alert" : "accent"}>
        {status}
      </Badge>
    </header>
  );
}
