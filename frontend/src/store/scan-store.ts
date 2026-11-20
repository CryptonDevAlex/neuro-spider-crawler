"use client";

import { create } from "zustand";

import type {
  Finding,
  PageNode,
  ScanStatus,
  SecurityHeader,
  ScanResult,
  SecuritySummary,
  StreamEvent,
  Technologies,
  WafDetection,
} from "@/lib/types";

interface ScanState {
  scanId: string | null;
  target: string;
  status: ScanStatus;
  phase: string;
  pagesDone: number;
  pagesTotal: number;
  nodes: PageNode[];
  findings: Finding[];
  headers: SecurityHeader[];
  technologies: Technologies;
  summary: SecuritySummary | null;
  subdomains: string[];
  wafDetections: WafDetection[];
  error: string | null;
  done: boolean;
  findingsTotal: number;
  setAccepted: (scanId: string, target: string) => void;
  applyEvent: (event: StreamEvent) => void;
  loadResult: (result: ScanResult) => void;
  reset: () => void;
}

const initialState = {
  scanId: null,
  target: "",
  status: "queued" as ScanStatus,
  phase: "idle",
  pagesDone: 0,
  pagesTotal: 0,
  nodes: [] as PageNode[],
  findings: [] as Finding[],
  headers: [] as SecurityHeader[],
  technologies: { server: null, frameworks: [], cookies: [], waf: [] } as Technologies,
  summary: null as SecuritySummary | null,
  subdomains: [] as string[],
  wafDetections: [] as WafDetection[],
  error: null as string | null,
  done: false,
  findingsTotal: 0,
};

export const useScanStore = create<ScanState>((set) => ({
  ...initialState,

  setAccepted: (scanId, target) =>
    set({ ...initialState, scanId, target, status: "queued", phase: "queued" }),

  applyEvent: (event) =>
    set((state) => {
      switch (event.type) {
        case "status":
          return {
            status: "running",
            phase: event.phase,
            pagesDone: event.pages_done,
            pagesTotal: event.pages_total,
          };
        case "node":
          if (state.nodes.some((node) => node.id === event.id)) {
            return {};
          }
          return {
            nodes: [
              ...state.nodes,
              {
                id: event.id,
                url: event.url,
                title: event.title,
                depth: event.depth,
                links: event.links,
                forms: event.forms,
                scripts: event.scripts,
                word_count: event.word_count,
              },
            ],
            pagesDone: state.nodes.length + 1,
          };
        case "finding":
          if (state.findings.some((finding) => finding.id === event.finding.id)) {
            return {};
          }
          return { findings: [...state.findings, event.finding] };
        case "summary":
          return {
            summary: {
              executive_diagnosis: event.executive_diagnosis,
              severity_counts: event.severity_counts,
              remediation_priorities: event.remediation_priorities,
              scope: event.scope,
              engine: event.engine,
            },
            technologies: event.technologies,
            headers: Array.from(
              new Map(event.headers.map((header) => [header.name, header])).values(),
            ),
            subdomains: event.subdomains ?? [],
            wafDetections: event.waf_detections ?? [],
          };
        case "error":
          return { error: `${event.code}: ${event.message}` };
        case "done":
          return {
            done: true,
            status: state.error ? "failed" : "completed",
            phase: "finished",
            pagesDone: event.pages_scanned,
            findingsTotal: event.findings_total,
          };
      }
    }),

  loadResult: (result) =>
    set({
      ...initialState,
      scanId: result.scan_id,
      target: result.target,
      status: result.status,
      done: result.status === "completed",
      phase: result.status,
      nodes: result.pages,
      findings: result.findings,
      headers: result.headers,
      technologies: result.technologies,
      summary: result.summary,
      subdomains: result.subdomains,
      wafDetections: result.waf_detections,
      findingsTotal: result.findings.length,
      pagesDone: result.pages.length,
      pagesTotal: result.pages.length,
    }),

  reset: () => set(initialState),
}));
