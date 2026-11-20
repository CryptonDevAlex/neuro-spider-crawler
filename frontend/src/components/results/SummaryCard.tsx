"use client";

import { useCrawlStore } from "@/store/crawl-store";

export function SummaryCard() {
  const summary = useCrawlStore((state) => state.summary);

  if (!summary) {
    return (
      <div className="rounded border border-dashed border-terminal-border p-4 text-xs text-terminal-muted">
        El resumen ejecutivo aparecerá cuando el análisis de IA finalice.
      </div>
    );
  }

  return (
    <div className="space-y-4 rounded border border-terminal-border bg-terminal-bg/60 p-4">
      <div>
        <p className="text-[10px] uppercase tracking-[0.2em] text-terminal-signal">
          resumen ejecutivo
        </p>
        <p className="mt-2 text-sm leading-relaxed text-terminal-text">
          {summary.executive_summary}
        </p>
      </div>
      <div>
        <p className="text-[10px] uppercase tracking-[0.2em] text-terminal-muted">puntos clave</p>
        <ul className="mt-2 space-y-1 text-xs text-terminal-text">
          {summary.key_points.map((point, index) => (
            <li key={index} className="flex gap-2">
              <span className="text-terminal-accent">›</span>
              {point.text}
            </li>
          ))}
        </ul>
      </div>
      {summary.entities.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {summary.entities.map((entity, index) => (
            <span
              key={index}
              className="rounded-full border border-terminal-border px-2 py-0.5 text-[10px] text-terminal-muted"
            >
              {entity}
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}
