export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthUser {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

export type ScanStatus = "queued" | "running" | "completed" | "failed";
export type EventType = "status" | "node" | "finding" | "summary" | "error" | "done";
export type Severity = "CRITICO" | "ALTO" | "MEDIO" | "BAJO" | "INFO";

export interface ScanRequest {
  url: string;
  max_depth: number;
  max_pages: number;
  audit_mode: boolean;
}

export interface ScanAccepted {
  scan_id: string;
  status: ScanStatus;
}

export interface PageNode {
  id: string;
  url: string;
  title: string;
  depth: number;
  links: number;
  forms: number;
  scripts: number;
  word_count: number;
}

export interface SecurityHeader {
  name: string;
  present: boolean;
  value: string | null;
  severity: Severity;
}

export interface FormInput {
  name: string;
  type: string;
}

export interface FormDetail {
  action: string;
  method: string;
  inputs: FormInput[];
}

export interface CookieInfo {
  name: string;
  http_only: boolean;
  secure: boolean;
  same_site: string | null;
}

export interface WafDetection {
  name: string;
  evidence: string;
  category: string;
}

export interface Technologies {
  server: string | null;
  frameworks: string[];
  cookies: CookieInfo[];
  waf: WafDetection[];
}

export interface Finding {
  id: string;
  severity: Severity;
  category: string;
  title: string;
  description: string;
  evidence: string;
  remediation: string;
  target: string;
  source: string | null;
}

export interface SecuritySummary {
  executive_diagnosis: string;
  severity_counts: Record<string, number>;
  remediation_priorities: string[];
  scope: Record<string, number>;
  engine: string;
}

export interface ScanResult {
  scan_id: string;
  status: ScanStatus;
  target: string;
  pages: PageNode[];
  headers: SecurityHeader[];
  forms: FormDetail[];
  js_files: string[];
  technologies: Technologies;
  findings: Finding[];
  robots_paths: string[];
  sitemap_paths: string[];
  subdomains: string[];
  waf_detections: WafDetection[];
  summary: SecuritySummary | null;
}

export interface EventBase {
  type: EventType;
  scan_id: string;
  timestamp: string;
}

export interface StatusEvent extends EventBase {
  type: "status";
  phase: string;
  pages_done: number;
  pages_total: number;
}

export interface NodeEvent extends EventBase {
  type: "node";
  id: string;
  url: string;
  title: string;
  depth: number;
  links: number;
  forms: number;
  scripts: number;
  word_count: number;
}

export interface FindingEvent extends EventBase {
  type: "finding";
  finding: Finding;
}

export interface SummaryEvent extends EventBase {
  type: "summary";
  executive_diagnosis: string;
  severity_counts: Record<string, number>;
  remediation_priorities: string[];
  scope: Record<string, number>;
  engine: string;
  technologies: Technologies;
  headers: SecurityHeader[];
  subdomains: string[];
  waf_detections: WafDetection[];
}

export interface ErrorEvent extends EventBase {
  type: "error";
  code: string;
  message: string;
  page_id?: string | null;
}

export interface DoneEvent extends EventBase {
  type: "done";
  pages_scanned: number;
  findings_total: number;
  duration_ms: number;
  export_ready: boolean;
}

export type StreamEvent =
  | StatusEvent
  | NodeEvent
  | FindingEvent
  | SummaryEvent
  | ErrorEvent
  | DoneEvent;

export interface ScanHistoryItem {
  scan_id: string;
  domain: string;
  created_at: string;
  finished_at: string | null;
  status: ScanStatus;
  engine_ia: string;
  severity_counts: Record<string, number>;
  findings_total: number;
  subdomains_total: number;
}

export interface ScanComparisonFinding {
  id: string;
  title: string;
  severity: Severity;
  category: string;
  remediation: string;
}

export interface ScanComparison {
  base_id: string;
  target_id: string;
  domain: string;
  resolved: ScanComparisonFinding[];
  new: ScanComparisonFinding[];
  persistent: ScanComparisonFinding[];
  counts: Record<string, number>;
}

export type MonitoringFrequency = "daily" | "weekly";

export interface MonitoredTarget {
  id: number;
  domain: string;
  frequency: MonitoringFrequency;
  active: boolean;
  webhook_url: string | null;
  last_run_at: string | null;
  created_at: string;
}
