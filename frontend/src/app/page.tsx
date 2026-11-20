"use client";

import { AppShell } from "@/components/layout/AppShell";
import { SpiderGraph } from "@/components/crawler/SpiderGraph";
import { UrlInput } from "@/components/crawler/UrlInput";
import { ResultsPanel } from "@/components/results/ResultsPanel";
import { useScanStream } from "@/hooks/useScanStream";

export default function Home() {
  useScanStream();

  return (
    <AppShell>
      <div className="grid min-h-0 flex-1 gap-4 p-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <section className="flex min-h-0 flex-col gap-4">
          <UrlInput />
          <SpiderGraph />
        </section>
        <ResultsPanel />
      </div>
    </AppShell>
  );
}
