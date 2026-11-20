import type {
  MonitoredTarget,
  MonitoringFrequency,
  ScanAccepted,
  ScanComparison,
  ScanHistoryItem,
  ScanRequest,
  ScanResult,
} from "./types";

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

async function parseResponse<T>(response: Response, message: string): Promise<T> {
  if (!response.ok) {
    throw new Error(`${message} (${response.status})`);
  }
  return (await response.json()) as T;
}

export async function fetchScanHistory(): Promise<ScanHistoryItem[]> {
  const response = await fetch(`${API_URL}/scans/history`);
  return parseResponse<ScanHistoryItem[]>(response, "No se pudo cargar el historial");
}

export async function fetchStoredScan(scanId: string): Promise<ScanResult> {
  const response = await fetch(`${API_URL}/scans/${scanId}`);
  return parseResponse<ScanResult>(response, "No se pudo cargar el escaneo");
}

export async function compareStoredScans(
  baseId: string,
  targetId: string,
): Promise<ScanComparison> {
  const query = new URLSearchParams({ base_id: baseId, target_id: targetId });
  const response = await fetch(`${API_URL}/scans/compare?${query.toString()}`);
  return parseResponse<ScanComparison>(response, "No se pudo comparar los escaneos");
}

export async function fetchMonitoredTargets(): Promise<MonitoredTarget[]> {
  const response = await fetch(`${API_URL}/monitoring/targets`);
  return parseResponse<MonitoredTarget[]>(response, "No se pudo cargar la vigilancia");
}

export async function createMonitoredTarget(
  domain: string,
  frequency: MonitoringFrequency,
  webhookUrl: string,
): Promise<MonitoredTarget> {
  const response = await fetch(`${API_URL}/monitoring/targets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      domain,
      frequency,
      webhook_url: webhookUrl.trim() || null,
    }),
  });
  return parseResponse<MonitoredTarget>(response, "No se pudo registrar el dominio");
}

export async function updateMonitoredTarget(
  targetId: number,
  active: boolean,
): Promise<MonitoredTarget> {
  const response = await fetch(`${API_URL}/monitoring/targets/${targetId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ active }),
  });
  return parseResponse<MonitoredTarget>(response, "No se pudo actualizar el dominio");
}

export async function deleteMonitoredTarget(targetId: number): Promise<void> {
  const response = await fetch(`${API_URL}/monitoring/targets/${targetId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(`No se pudo eliminar el dominio (${response.status})`);
  }
}
