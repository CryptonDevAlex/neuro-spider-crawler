"use client";

import { formatNumber } from "@/lib/utils";
import { useCrawlStore } from "@/store/crawl-store";

export function MetricsGrid() {
  const nodes = useCrawlStore((state) => state.nodes);
  const tables = useCrawlStore((state) => state.tables);

  const links = nodes.reduce((total, node) => total + node.links, 0);
  const words = nodes.reduce((total, node) => total + node.word_count, 0);

  const metrics = [
    { label: "páginas", value: nodes.length },
    { label: "enlaces", value: links },
    { label: "tablas", value: tables.length },
    { label: "palabras", value: words },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className="rounded border border-terminal-border bg-terminal-bg/60 p-3"
        >
          <p className="text-[10px] uppercase tracking-widest text-terminal-muted">
            {metric.label}
          </p>
          <p className="mt-1 text-xl text-terminal-accent">{formatNumber(metric.value)}</p>
        </div>
      ))}
    </div>
  );
}
