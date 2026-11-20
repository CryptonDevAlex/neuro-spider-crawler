"use client";

import { Button } from "@/components/ui/Button";
import type { CrawlResult, ExportFormat } from "@/lib/types";
import { useCrawlStore } from "@/store/crawl-store";

function download(filename: string, content: string, mime: string): void {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function toMarkdown(result: CrawlResult): string {
  const lines = [
    `# NeuroSpider — ${result.crawl_id}`,
    "",
    "## Resumen ejecutivo",
    result.summary?.executive_summary ?? "No disponible",
    "",
    "## Puntos clave",
    ...(result.summary?.key_points.map((point) => `- ${point.text}`) ?? ["- No disponible"]),
    "",
    "## Páginas",
    ...result.nodes.map(
      (node) => `- [${node.title || node.url}](${node.url}) · profundidad ${node.depth} · ${node.links} enlaces`,
    ),
    "",
    "## Entidades",
    ...(result.summary?.entities.map((entity) => `- ${entity}`) ?? ["- No disponible"]),
  ];

  return lines.join("\n");
}

export function ExportBar() {
  const crawlId = useCrawlStore((state) => state.crawlId);
  const nodes = useCrawlStore((state) => state.nodes);
  const tables = useCrawlStore((state) => state.tables);
  const summary = useCrawlStore((state) => state.summary);
  const status = useCrawlStore((state) => state.status);

  const handleExport = (format: ExportFormat) => {
    if (!crawlId) {
      return;
    }

    const result: CrawlResult = { crawl_id: crawlId, status, nodes, tables, summary };
    const content = format === "json" ? JSON.stringify(result, null, 2) : toMarkdown(result);
    download(`neurospider-${crawlId}.${format === "json" ? "json" : "md"}`, content, format === "json" ? "application/json" : "text/markdown");
  };

  const disabled = !crawlId || (nodes.length === 0 && !summary);

  return (
    <div className="flex gap-2">
      <Button variant="ghost" disabled={disabled} onClick={() => handleExport("json")}>
        json
      </Button>
      <Button variant="ghost" disabled={disabled} onClick={() => handleExport("markdown")}>
        markdown
      </Button>
    </div>
  );
}
