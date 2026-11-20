"use client";

import { Badge } from "@/components/ui/Badge";
import type { Severity } from "@/lib/types";
import { formatNumber, severityTone } from "@/lib/utils";
import { useScanStore } from "@/store/scan-store";

const SEVERITIES: Severity[] = ["CRITICO", "ALTO", "MEDIO", "BAJO", "INFO"];

export function SummaryCard() {
  const summary = useScanStore((state) => state.summary);

  if (!summary) {
    return (
      <div className="rounded border border-dashed border-terminal-border p-4 text-xs text-terminal-muted">
        El diagnóstico ejecutivo aparecerá cuando finalice el análisis pasivo.
      </div>
    );
  }

  return (
    <div className="space-y-4 rounded border border-terminal-border bg-terminal-bg/60 p-4">
      <div className="flex flex-wrap gap-2">
        {SEVERITIES.map((severity) => (
          <Badge key={severity} tone={severityTone(severity)}>
            {severity}: {formatNumber(summary.severity_counts[severity] ?? 0)}
          </Badge>
        ))}
      </div>
      <div>
        <p className="text-[10px] uppercase tracking-[0.2em] text-terminal-signal">
          diagnóstico ejecutivo de seguridad pasiva
        </p>
        <p className="mt-2 text-sm leading-relaxed text-terminal-text">
          {summary.executive_diagnosis}
        </p>
      </div>
      {summary.remediation_priorities.length > 0 ? (
        <div>
          <p className="text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
            prioridades de remediación
          </p>
          <ol className="mt-2 space-y-1 text-xs text-terminal-text">
            {summary.remediation_priorities.map((priority, index) => (
              <li key={priority} className="flex gap-2">
                <span className="text-terminal-accent">{index + 1}.</span>
                {priority}
              </li>
            ))}
          </ol>
        </div>
      ) : null}
    </div>
  );
}
