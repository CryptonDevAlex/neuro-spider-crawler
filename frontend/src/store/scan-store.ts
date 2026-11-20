"use client";

import { create } from "zustand";

import type {
  Finding,
  PageNode,
  ScanStatus,
  SecurityHeader,
  SecuritySummary,
  StreamEvent,
  Technologies,
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
  error: string | null;
  done: boolean;
  findingsTotal: number;
  setAccepted: (scanId: string, target: string) => void;
  applyEvent: (event: StreamEvent) => void;
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
  technologies: { server: null, frameworks: [], cookies: [] } as Technologies,
  summary: null as SecuritySummary | null,
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
            },
            technologies: event.technologies,
            headers: Array.from(
              new Map(event.headers.map((header) => [header.name, header])).values(),
            ),
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

  reset: () => set(initialState),
}));
