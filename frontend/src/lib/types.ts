export type CrawlStatus = "queued" | "running" | "completed" | "failed";
export type EventType = "status" | "node" | "table" | "summary" | "error" | "done";
export type ExportFormat = "json" | "markdown";

export interface CrawlRequest {
  url: string;
  max_depth: number;
  max_pages: number;
  respect_robots: boolean;
}

export interface CrawlAccepted {
  crawl_id: string;
  status: CrawlStatus;
}

export interface PageNode {
  id: string;
  url: string;
  title: string;
  depth: number;
  links: number;
  word_count: number;
  text?: string;
}

export interface TableData {
  node_id: string;
  headers: string[];
  rows: string[][];
}

export interface KeyPoint {
  text: string;
  weight: number;
}

export interface ExecutiveSummary {
  executive_summary: string;
  key_points: KeyPoint[];
  entities: string[];
}

export interface CrawlResult {
  crawl_id: string;
  status: CrawlStatus;
  nodes: PageNode[];
  tables: TableData[];
  summary: ExecutiveSummary | null;
}

export interface EventBase {
  type: EventType;
  crawl_id: string;
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
  word_count: number;
}

export interface TableEvent extends EventBase {
  type: "table";
  node_id: string;
  headers: string[];
  rows: string[][];
}

export interface SummaryEvent extends EventBase {
  type: "summary";
  executive_summary: string;
  key_points: string[];
  entities: string[];
}

export interface ErrorEvent extends EventBase {
  type: "error";
  code: string;
  message: string;
  node_id?: string | null;
}

export interface DoneEvent extends EventBase {
  type: "done";
  pages_crawled: number;
  duration_ms: number;
  export_ready: boolean;
}

export type StreamEvent =
  | StatusEvent
  | NodeEvent
  | TableEvent
  | SummaryEvent
  | ErrorEvent
  | DoneEvent;
