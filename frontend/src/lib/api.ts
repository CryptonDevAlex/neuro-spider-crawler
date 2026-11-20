import type { CrawlAccepted, CrawlRequest, CrawlResult } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function startCrawl(payload: CrawlRequest): Promise<CrawlAccepted> {
  const response = await fetch(`${API_URL}/crawl`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`No se pudo iniciar el crawl (${response.status})`);
  }

  return (await response.json()) as CrawlAccepted;
}

export async function getCrawl(crawlId: string): Promise<CrawlResult> {
  const response = await fetch(`${API_URL}/crawl/${crawlId}`);

  if (!response.ok) {
    throw new Error(`No se pudo obtener el crawl (${response.status})`);
  }

  return (await response.json()) as CrawlResult;
}

export function streamUrl(crawlId: string): string {
  return `${API_URL}/crawl/${crawlId}/stream`;
}
