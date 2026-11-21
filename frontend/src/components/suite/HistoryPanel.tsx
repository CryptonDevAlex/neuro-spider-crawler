"use client";

import { useCallback, useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Panel } from "@/components/ui/Panel";
import {
  compareStoredScans,
  deleteStoredScan,
  fetchReport,
  fetchScanHistory,
  fetchStoredScan,
} from "@/lib/api";
import type { ScanComparison, ScanComparisonFinding, ScanHistoryItem } from "@/lib/types";
import { formatNumber, severityTone, type BadgeTone } from "@/lib/utils";
import { useScanStore } from "@/store/scan-store";
import { useUiStore } from "@/store/ui-store";

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function FindingList({
  title,
  items,
  tone,
}: {
  title: string;
  items: ScanComparisonFinding[];
  tone: BadgeTone;
}) {
  return (
    <div className="rounded border border-terminal-border bg-terminal-bg/60 p-3">
      <div className="mb-2 flex items-center justify-between gap-2">
        <p className="text-[10px] uppercase tracking-[0.2em] text-terminal-muted">{title}</p>
        <Badge tone={tone}>{items.length}</Badge>
      </div>
      <div className="space-y-2">
        {items.length > 0 ? (
          items.map((item) => (
            <div key={item.id} className="flex items-start justify-between gap-3">
              <div>
                <p className="text-[11px] text-terminal-text">{item.title}</p>
                <p className="text-[10px] text-terminal-muted">{item.category}</p>
              </div>
              <Badge tone={severityTone(item.severity)}>{item.severity}</Badge>
            </div>
          ))
        ) : (
          <p className="text-[11px] text-terminal-muted">sin cambios</p>
        )}
      </div>
    </div>
  );
}

export function HistoryPanel() {
  const [items, setItems] = useState<ScanHistoryItem[]>([]);
  const [baseId, setBaseId] = useState("");
  const [targetId, setTargetId] = useState("");
  const [comparison, setComparison] = useState<ScanComparison | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const loadResult = useScanStore((state) => state.loadResult);
  const setView = useUiStore((state) => state.setView);

  const loadHistory = useCallback(async () => {
    setBusy(true);
    setError(null);
    try {
      const history = await fetchScanHistory();
      setItems(history);
      const ids = new Set(history.map((item) => item.scan_id));
      setBaseId((current) =>
        current && ids.has(current)
          ? current
          : history[1]?.scan_id || history[0]?.scan_id || "",
      );
      setTargetId((current) =>
        current && ids.has(current) ? current : history[0]?.scan_id || "",
      );
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo cargar el historial");
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    const frame = requestAnimationFrame(() => {
      void loadHistory();
    });
    return () => cancelAnimationFrame(frame);
  }, [loadHistory]);

  const handleLoad = async (scanId: string) => {
    setBusy(true);
    setError(null);
    try {
      loadResult(await fetchStoredScan(scanId));
      setView("recon");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo cargar el escaneo");
    } finally {
      setBusy(false);
    }
  };

  const handlePdf = async (scanId: string) => {
    setError(null);
    try {
      const blob = await fetchReport(scanId, "pdf");
      downloadBlob(blob, `neurospider-audit-${scanId}.pdf`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo descargar el PDF");
    }
  };

  const handleDelete = async (item: ScanHistoryItem) => {
    const confirmed = window.confirm(
      `¿Eliminar la auditoría de ${item.domain} del ${new Date(item.created_at).toLocaleString("es-ES")}? Esta acción no se puede deshacer.`,
    );
    if (!confirmed) {
      return;
    }

    setBusy(true);
    setError(null);
    try {
      await deleteStoredScan(item.scan_id);
      setComparison(null);
      setBaseId("");
      setTargetId("");
      await loadHistory();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo eliminar la auditoría");
    } finally {
      setBusy(false);
    }
  };

  const handleCompare = async () => {
    if (!baseId || !targetId) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      setComparison(await compareStoredScans(baseId, targetId));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo comparar");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid min-h-0 flex-1 gap-4 p-4 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
      <Panel
        title="Historial de auditorías"
        subtitle="Escaneos persistidos en SQLite local"
        actions={
          <Button variant="ghost" disabled={busy} onClick={() => void loadHistory()}>
            ACTUALIZAR
          </Button>
        }
      >
        {error ? <p className="mb-3 text-[11px] text-terminal-alert">{error}</p> : null}
        <div className="space-y-2">
          {items.length > 0 ? (
            items.map((item) => (
              <div
                key={item.scan_id}
                className="rounded border border-terminal-border bg-terminal-bg/60 p-3"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-xs text-terminal-text">{item.domain}</p>
                    <p className="text-[10px] text-terminal-muted">
                      {new Date(item.created_at).toLocaleString("es-ES")} · {item.engine_ia}
                    </p>
                  </div>
                  <Badge tone={item.status === "completed" ? "signal" : "alert"}>
                    {item.status}
                  </Badge>
                </div>
                <p className="mt-2 text-[10px] text-terminal-muted">
                  {formatNumber(item.findings_total)} hallazgos · {item.subdomains_total}{" "}
                  subdominios
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Button disabled={busy} onClick={() => void handleLoad(item.scan_id)}>
                    CARGAR EN PANTALLA
                  </Button>
                  <Button variant="ghost" onClick={() => void handlePdf(item.scan_id)}>
                    PDF
                  </Button>
                  <Button
                    variant="danger"
                    disabled={busy}
                    onClick={() => void handleDelete(item)}
                  >
                    ELIMINAR
                  </Button>
                </div>
              </div>
            ))
          ) : (
            <p className="text-[11px] text-terminal-muted">
              Aún no hay auditorías guardadas en la base local.
            </p>
          )}
        </div>
      </Panel>

      <Panel
        title="Comparador antes vs. después"
        subtitle="Riesgos mitigados, nuevos y persistentes entre dos auditorías"
      >
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="space-y-1">
            <span className="text-[10px] uppercase tracking-widest text-terminal-muted">
              línea base
            </span>
            <select
              value={baseId}
              onChange={(event) => setBaseId(event.target.value)}
              className="w-full rounded border border-terminal-border bg-terminal-bg px-2 py-2 text-[11px] text-terminal-text"
            >
              <option value="">seleccionar escaneo</option>
              {items.map((item) => (
                <option key={item.scan_id} value={item.scan_id}>
                  {item.domain} · {new Date(item.created_at).toLocaleDateString("es-ES")}
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-1">
            <span className="text-[10px] uppercase tracking-widest text-terminal-muted">
              escaneo actual
            </span>
            <select
              value={targetId}
              onChange={(event) => setTargetId(event.target.value)}
              className="w-full rounded border border-terminal-border bg-terminal-bg px-2 py-2 text-[11px] text-terminal-text"
            >
              <option value="">seleccionar escaneo</option>
              {items.map((item) => (
                <option key={item.scan_id} value={item.scan_id}>
                  {item.domain} · {new Date(item.created_at).toLocaleDateString("es-ES")}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="mt-3">
          <Button disabled={busy || !baseId || !targetId} onClick={() => void handleCompare()}>
            COMPARAR RIESGOS
          </Button>
        </div>

        {comparison ? (
          <div className="mt-4 space-y-3">
            <p className="text-[10px] text-terminal-muted">
              {comparison.domain} · {comparison.counts.resolved} mitigados ·{" "}
              {comparison.counts.new} nuevos · {comparison.counts.persistent} persistentes
            </p>
            <FindingList title="riesgos mitigados" items={comparison.resolved} tone="signal" />
            <FindingList title="riesgos nuevos" items={comparison.new} tone="alert" />
            <FindingList
              title="riesgos persistentes"
              items={comparison.persistent}
              tone="accent"
            />
          </div>
        ) : (
          <p className="mt-4 text-[11px] text-terminal-muted">
            Selecciona dos auditorías del mismo dominio para ver el progreso del cliente.
          </p>
        )}
      </Panel>
    </div>
  );
}
