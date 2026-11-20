"use client";

import { DataTable } from "./DataTable";
import { ExportBar } from "./ExportBar";
import { MetricsGrid } from "./MetricsGrid";
import { SummaryCard } from "./SummaryCard";
import { Panel } from "@/components/ui/Panel";

export function ResultsPanel() {
  return (
    <Panel
      title="Datos extraídos"
      subtitle="Métricas, resumen por IA y tablas del sitio"
      className="h-full"
      actions={<ExportBar />}
    >
      <div className="space-y-4">
        <MetricsGrid />
        <SummaryCard />
        <DataTable />
      </div>
    </Panel>
  );
}
