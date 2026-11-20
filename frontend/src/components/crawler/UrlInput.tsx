"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/Button";
import { startCrawl } from "@/lib/api";
import type { CrawlRequest } from "@/lib/types";
import { useCrawlStore } from "@/store/crawl-store";

export function UrlInput() {
  const [url, setUrl] = useState("");
  const [maxDepth, setMaxDepth] = useState(2);
  const [maxPages, setMaxPages] = useState(30);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const setAccepted = useCrawlStore((state) => state.setAccepted);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const payload: CrawlRequest = {
      url,
      max_depth: maxDepth,
      max_pages: maxPages,
      respect_robots: true,
    };

    try {
      const response = await startCrawl(payload);
      setAccepted(response.crawl_id);
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
        nuevo rastreo
      </div>
      <div className="flex flex-col gap-2 sm:flex-row">
        <input
          type="url"
          required
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="https://ejemplo.com"
          aria-label="URL a rastrear"
          className="min-w-0 flex-1 rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm text-terminal-text outline-none placeholder:text-terminal-muted focus:border-terminal-accent"
        />
        <Button type="submit" disabled={loading}>
          {loading ? " iniciando..." : "rastrear"}
        </Button>
      </div>
      <div className="flex gap-4 text-[10px] uppercase tracking-widest text-terminal-muted">
        <label className="flex items-center gap-2">
          profundidad
          <input
            type="number"
            min={1}
            max={5}
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
            max={200}
            value={maxPages}
            onChange={(event) => setMaxPages(Number(event.target.value))}
            className="w-16 rounded border border-terminal-border bg-terminal-bg px-2 py-1 text-terminal-text"
          />
        </label>
      </div>
      {error ? <p className="text-[10px] text-terminal-alert">{error}</p> : null}
    </form>
  );
}
