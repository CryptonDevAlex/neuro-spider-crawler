import type { ScanAccepted, ScanRequest } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function startScan(payload: ScanRequest): Promise<ScanAccepted> {
  const response = await fetch(`${API_URL}/scan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`No se pudo iniciar el reconocimiento (${response.status})`);
  }

  return (await response.json()) as ScanAccepted;
}

export function streamUrl(scanId: string): string {
  return `${API_URL}/scan/${scanId}/stream`;
}

export function reportUrl(scanId: string): string {
  return `${API_URL}/scan/${scanId}/report.md`;
}

export function pdfReportUrl(scanId: string): string {
  return `${API_URL}/scan/${scanId}/report.pdf`;
}
