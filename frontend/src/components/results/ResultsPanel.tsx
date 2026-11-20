"use client";

import { ExportBar } from "./ExportBar";
import { FindingsReport } from "./FindingsReport";
import { MetricsGrid } from "./MetricsGrid";
import { SummaryCard } from "./SummaryCard";
import { TechPanel } from "./TechPanel";
import { Panel } from "@/components/ui/Panel";

export function ResultsPanel() {
  return (
    <Panel
      title="Reporte de seguridad"
      subtitle="Reconocimiento pasivo, superficie expuesta y remediación priorizada"
      className="h-full"
      actions={<ExportBar />}
    >
      <div className="space-y-4">
        <MetricsGrid />
        <SummaryCard />
        <TechPanel />
        <FindingsReport />
      </div>
    </Panel>
  );
}
