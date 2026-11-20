"use client";

import { create } from "zustand";

import type {
  CrawlStatus,
  ExecutiveSummary,
  PageNode,
  StreamEvent,
  TableData,
} from "@/lib/types";

interface CrawlState {
  crawlId: string | null;
  status: CrawlStatus;
  phase: string;
  pagesDone: number;
  pagesTotal: number;
  nodes: PageNode[];
  tables: TableData[];
  summary: ExecutiveSummary | null;
  error: string | null;
  done: boolean;
  setAccepted: (crawlId: string) => void;
  applyEvent: (event: StreamEvent) => void;
  reset: () => void;
}

const initialState = {
  crawlId: null,
  status: "queued" as CrawlStatus,
  phase: "idle",
  pagesDone: 0,
  pagesTotal: 0,
  nodes: [] as PageNode[],
  tables: [] as TableData[],
  summary: null as ExecutiveSummary | null,
  error: null as string | null,
  done: false,
};

export const useCrawlStore = create<CrawlState>((set) => ({
  ...initialState,

  setAccepted: (crawlId) =>
    set({ ...initialState, crawlId, status: "queued", phase: "queued" }),

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
          return {
            nodes: [
              ...state.nodes,
              {
                id: event.id,
                url: event.url,
                title: event.title,
                depth: event.depth,
                links: event.links,
                word_count: event.word_count,
              },
            ],
            pagesDone: state.nodes.length + 1,
          };
        case "table":
          return {
            tables: [
              ...state.tables,
              {
                node_id: event.node_id,
                headers: event.headers,
                rows: event.rows,
              },
            ],
          };
        case "summary":
          return {
            summary: {
              executive_summary: event.executive_summary,
              key_points: event.key_points.map((text) => ({ text, weight: 0 })),
              entities: event.entities,
            },
          };
        case "error":
          return { error: `${event.code}: ${event.message}` };
        case "done":
          return {
            done: true,
            status: "completed",
            phase: "finished",
            pagesDone: event.pages_crawled,
          };
      }
    }),

  reset: () => set(initialState),
}));
