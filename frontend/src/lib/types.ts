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

export interface Technologies {
  server: string | null;
  frameworks: string[];
  cookies: CookieInfo[];
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
