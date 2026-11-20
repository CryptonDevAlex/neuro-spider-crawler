"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { reportUrl } from "@/lib/api";
import { useScanStore } from "@/store/scan-store";

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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = async () => {
    if (!scanId) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(reportUrl(scanId));
      if (!response.ok) {
        throw new Error(`No se pudo generar el informe (${response.status})`);
      }
      download(await response.blob(), `neurospider-${scanId}.md`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return <span className="text-[10px] text-terminal-alert">{error}</span>;
  }

  return (
    <Button variant="ghost" disabled={!scanId || !done || loading} onClick={handleDownload}>
      {loading ? "generando..." : "MARKDOWN"}
    </Button>
  );
}
