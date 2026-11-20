"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/Button";
import { startScan } from "@/lib/api";
import type { ScanRequest } from "@/lib/types";
import { useScanStore } from "@/store/scan-store";

export function UrlInput() {
  const [url, setUrl] = useState("http://127.0.0.1:8080/index.html");
  const [maxDepth, setMaxDepth] = useState(2);
  const [maxPages, setMaxPages] = useState(20);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const setAccepted = useScanStore((state) => state.setAccepted);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const payload: ScanRequest = {
      url,
      max_depth: maxDepth,
      max_pages: maxPages,
      audit_mode: true,
    };

    try {
      const response = await startScan(payload);
      setAccepted(response.scan_id, url);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 rounded-lg border border-terminal-border bg-terminal-panel/80 p-4"
    >
      <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.25em] text-terminal-muted">
        <span className="h-2 w-2 rounded-full bg-terminal-signal" />
        nuevo reconocimiento autorizado
      </div>
      <div className="flex flex-col gap-2 sm:flex-row">
        <input
          type="url"
          required
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="https://ejemplo.com"
          aria-label="URL objetivo autorizada"
          className="min-w-0 flex-1 rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm text-terminal-text outline-none placeholder:text-terminal-muted focus:border-terminal-accent"
        />
        <Button type="submit" disabled={loading}>
          {loading ? " analizando..." : "reconocer"}
        </Button>
      </div>
      <div className="flex flex-wrap gap-4 text-[10px] uppercase tracking-widest text-terminal-muted">
        <label className="flex items-center gap-2">
          profundidad
          <input
            type="number"
            min={1}
            max={4}
            value={maxDepth}
            onChange={(event) => setMaxDepth(Number(event.target.value))}
            className="w-14 rounded border border-terminal-border bg-terminal-bg px-2 py-1 text-terminal-text"
          />
        </label>
        <label className="flex items-center gap-2">
          páginas
          <input
            type="number"
            min={1}
            max={100}
            value={maxPages}
            onChange={(event) => setMaxPages(Number(event.target.value))}
            className="w-16 rounded border border-terminal-border bg-terminal-bg px-2 py-1 text-terminal-text"
          />
        </label>
        <span className="flex items-center gap-2 text-terminal-signal">
          <span className="h-1.5 w-1.5 rounded-full bg-terminal-signal" />
          modo auditoría
        </span>
      </div>
      {error ? <p className="text-[10px] text-terminal-alert">{error}</p> : null}
    </form>
  );
}
