"use client";

import { Badge } from "@/components/ui/Badge";
import type { Severity } from "@/lib/types";
import { severityTone } from "@/lib/utils";
import { useScanStore } from "@/store/scan-store";

const SEVERITY_ORDER: Severity[] = ["CRITICO", "ALTO", "MEDIO", "BAJO", "INFO"];

export function FindingsReport() {
  const findings = useScanStore((state) => state.findings);

  if (findings.length === 0) {
    return (
      <div className="rounded border border-dashed border-terminal-border p-4 text-xs text-terminal-muted">
        Los hallazgos de seguridad aparecerán en tiempo real durante el reconocimiento.
      </div>
    );
  }

  const ordered = [...findings].sort(
    (left, right) =>
      SEVERITY_ORDER.indexOf(left.severity) - SEVERITY_ORDER.indexOf(right.severity),
  );

  return (
    <div className="space-y-3">
      {ordered.map((finding) => (
        <article
          key={finding.id}
          className="rounded border border-terminal-border bg-terminal-bg/60 p-3"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone={severityTone(finding.severity)}>{finding.severity}</Badge>
                <span className="text-[10px] uppercase tracking-widest text-terminal-muted">
                  {finding.category}
                </span>
              </div>
              <h3 className="mt-2 break-words text-xs font-semibold text-terminal-text">
                {finding.title}
              </h3>
            </div>
          </div>
          <p className="mt-2 text-[11px] leading-relaxed text-terminal-muted">
            {finding.description}
          </p>
          <p className="mt-2 break-all rounded bg-terminal-panel px-2 py-1 text-[10px] text-terminal-accent">
            {finding.evidence}
          </p>
          <p className="mt-2 text-[11px] leading-relaxed text-terminal-text">
            <span className="text-terminal-signal">recomendación: </span>
            {finding.remediation}
          </p>
          <p className="mt-2 truncate text-[10px] text-terminal-muted">
            fuente: {finding.source ?? finding.target}
          </p>
        </article>
      ))}
    </div>
  );
}
