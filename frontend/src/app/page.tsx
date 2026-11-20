"use client";

import { SpiderGraph } from "@/components/crawler/SpiderGraph";
import { UrlInput } from "@/components/crawler/UrlInput";
import { AppShell } from "@/components/layout/AppShell";
import { ResultsPanel } from "@/components/results/ResultsPanel";
import { HistoryPanel } from "@/components/suite/HistoryPanel";
import { MonitoringPanel } from "@/components/suite/MonitoringPanel";
import { useScanStream } from "@/hooks/useScanStream";
import { useUiStore } from "@/store/ui-store";

export default function Home() {
  useScanStream();
  const view = useUiStore((state) => state.view);

  return (
    <AppShell>
      {view === "recon" ? (
        <div className="grid min-h-0 flex-1 gap-4 p-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
          <section className="flex min-h-0 flex-col gap-4">
            <UrlInput />
            <SpiderGraph />
          </section>
          <ResultsPanel />
        </div>
      ) : null}
      {view === "history" ? <HistoryPanel /> : null}
      {view === "monitoring" ? <MonitoringPanel /> : null}
    </AppShell>
  );
}
