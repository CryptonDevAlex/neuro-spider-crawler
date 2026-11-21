import type {
  AuthUser,
  LoginRequest,
  MonitoredTarget,
  RegisterRequest,
  MonitoringFrequency,
  ScanAccepted,
  ScanComparison,
  ScanHistoryItem,
  ScanRequest,
  ScanResult,
  TokenResponse,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "/api-backend";

async function errorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string };
    return payload.detail ? `${payload.detail} (${response.status})` : `${fallback} (${response.status})`;
  } catch {
    return `${fallback} (${response.status})`;
  }
}

async function request<T>(
  path: string,
  init: RequestInit,
  fallback: string,
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...init.headers,
    },
  });

  if (!response.ok) {
    throw new Error(await errorMessage(response, fallback));
  }
  return (await response.json()) as T;
}

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  return request<TokenResponse>(
    "/auth/login",
    { method: "POST", body: JSON.stringify(payload) },
    "No se pudo iniciar sesión",
  );
}

export async function register(payload: RegisterRequest): Promise<TokenResponse> {
  return request<TokenResponse>(
    "/auth/register",
    { method: "POST", body: JSON.stringify(payload) },
    "No se pudo crear la cuenta",
  );
}

export function googleLoginUrl(): string {
  return `${API_URL}/auth/google/login`;
}

export type GoogleAvailability =
  | { available: true }
  | { available: false; message: string };

export async function checkGoogleAvailability(): Promise<GoogleAvailability> {
  try {
    const response = await fetch(googleLoginUrl(), {
      method: "GET",
      credentials: "include",
      redirect: "manual",
      headers: { Accept: "application/json" },
    });

    if (
      response.type === "opaqueredirect" ||
      response.status === 0 ||
      (response.status >= 300 && response.status < 400)
    ) {
      return { available: true };
    }

    if (!response.ok) {
      return {
        available: false,
        message:
          "Google OAuth aún no está configurado en el servidor; usa 'Registrarse' para crear tu cuenta local al instante",
      };
    }

    return { available: true };
  } catch {
    return {
      available: false,
      message: "No se pudo verificar Google OAuth en este momento; inténtalo de nuevo.",
    };
  }
}

export async function fetchCurrentUser(): Promise<AuthUser> {
  return request<AuthUser>(
    "/auth/me",
    { method: "GET" },
    "No se pudo verificar la sesión",
  );
}

export async function logout(): Promise<void> {
  await request<{ logged_out: boolean }>(
    "/auth/logout",
    { method: "POST" },
    "No se pudo cerrar la sesión",
  );
}

export async function startScan(payload: ScanRequest): Promise<ScanAccepted> {
  return request<ScanAccepted>(
    "/scan",
    { method: "POST", body: JSON.stringify(payload) },
    "No se pudo iniciar el reconocimiento",
  );
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

export async function fetchReport(scanId: string, format: "md" | "pdf"): Promise<Blob> {
  const url = format === "pdf" ? pdfReportUrl(scanId) : reportUrl(scanId);
  const response = await fetch(url, { credentials: "include" });
  if (!response.ok) {
    throw new Error(await errorMessage(response, "No se pudo descargar el informe"));
  }
  return response.blob();
}

export async function fetchScanHistory(): Promise<ScanHistoryItem[]> {
  return request<ScanHistoryItem[]>(
    "/scans/history",
    { method: "GET" },
    "No se pudo cargar el historial",
  );
}

export async function fetchStoredScan(scanId: string): Promise<ScanResult> {
  return request<ScanResult>(
    `/scans/${scanId}`,
    { method: "GET" },
    "No se pudo cargar el escaneo",
  );
}

export async function deleteStoredScan(scanId: string): Promise<void> {
  await request<{ deleted: boolean }>(
    `/scans/${scanId}`,
    { method: "DELETE" },
    "No se pudo eliminar el escaneo",
  );
}

export async function compareStoredScans(
  baseId: string,
  targetId: string,
): Promise<ScanComparison> {
  const query = new URLSearchParams({ base_id: baseId, target_id: targetId });
  return request<ScanComparison>(
    `/scans/compare?${query.toString()}`,
    { method: "GET" },
    "No se pudo comparar los escaneos",
  );
}

export async function fetchMonitoredTargets(): Promise<MonitoredTarget[]> {
  return request<MonitoredTarget[]>(
    "/monitoring/targets",
    { method: "GET" },
    "No se pudo cargar la vigilancia",
  );
}

export async function createMonitoredTarget(
  domain: string,
  frequency: MonitoringFrequency,
  webhookUrl: string,
): Promise<MonitoredTarget> {
  return request<MonitoredTarget>(
    "/monitoring/targets",
    {
      method: "POST",
      body: JSON.stringify({
        domain,
        frequency,
        webhook_url: webhookUrl.trim() || null,
      }),
    },
    "No se pudo registrar el dominio",
  );
}

export async function updateMonitoredTarget(
  targetId: number,
  active: boolean,
): Promise<MonitoredTarget> {
  return request<MonitoredTarget>(
    `/monitoring/targets/${targetId}`,
    { method: "PATCH", body: JSON.stringify({ active }) },
    "No se pudo actualizar el dominio",
  );
}

export async function deleteMonitoredTarget(targetId: number): Promise<void> {
  await request<{ deleted: boolean }>(
    `/monitoring/targets/${targetId}`,
    { method: "DELETE" },
    "No se pudo eliminar el dominio",
  );
}
