"use client";

import { formatNumber } from "@/lib/utils";
import { useScanStore } from "@/store/scan-store";

const RISK_SEVERITIES = ["CRITICO", "ALTO", "MEDIO"];

export function MetricsGrid() {
  const nodes = useScanStore((state) => state.nodes);
  const findings = useScanStore((state) => state.findings);
  const headers = useScanStore((state) => state.headers);
  const summary = useScanStore((state) => state.summary);

  const endpoints = nodes.reduce((total, node) => total + node.links, 0) + nodes.length;
  const forms = nodes.reduce((total, node) => total + node.forms, 0);
  const missingHeaders = headers.filter((header) => !header.present).length;
  const riskFindings = findings.filter((finding) =>
    RISK_SEVERITIES.includes(finding.severity),
  ).length;

  const metrics = [
    {
      label: "endpoints / formularios",
      value: `${formatNumber(endpoints)} / ${formatNumber(forms)}`,
    },
    {
      label: "archivos JS",
      value: formatNumber(nodes.reduce((total, node) => total + node.scripts, 0)),
    },
    {
      label: "cabeceras faltantes",
      value: formatNumber(missingHeaders || summary?.scope.missing_headers || 0),
    },
    {
      label: "hallazgos de riesgo",
      value: formatNumber(riskFindings || summary?.scope.risk_findings || 0),
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3">
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className="rounded border border-terminal-border bg-terminal-bg/60 p-3"
        >
          <p className="text-[10px] uppercase tracking-widest text-terminal-muted">
            {metric.label}
          </p>
          <p className="mt-1 text-lg text-terminal-accent">{metric.value}</p>
        </div>
      ))}
    </div>
  );
}
