"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { fetchReport } from "@/lib/api";
import { useScanStore } from "@/store/scan-store";

type ExportFormat = "markdown" | "pdf";

function download(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function ExportBar() {
  const scanId = useScanStore((state) => state.scanId);
  const done = useScanStore((state) => state.done);
  const [loading, setLoading] = useState<ExportFormat | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = async (format: ExportFormat) => {
    if (!scanId) {
      return;
    }

    setLoading(format);
    setError(null);

    try {
      const blob = await fetchReport(scanId, format === "pdf" ? "pdf" : "md");
      const filename =
        format === "pdf"
          ? `neurospider-audit-${scanId}.pdf`
          : `neurospider-${scanId}.md`;
      download(blob, filename);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Error desconocido");
    } finally {
      setLoading(null);
    }
  };

  if (error) {
    return <span className="text-[10px] text-terminal-alert">{error}</span>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      <Button
        variant="primary"
        disabled={!scanId || !done || loading !== null}
        onClick={() => void handleDownload("pdf")}
      >
        {loading === "pdf" ? "generando PDF..." : "DESCARGAR PDF"}
      </Button>
      <Button
        variant="ghost"
        disabled={!scanId || !done || loading !== null}
        onClick={() => void handleDownload("markdown")}
      >
        {loading === "markdown" ? "generando..." : "MARKDOWN"}
      </Button>
    </div>
  );
}
