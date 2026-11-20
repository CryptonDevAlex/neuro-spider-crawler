"use client";

import { useCallback, useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Panel } from "@/components/ui/Panel";
import {
  createMonitoredTarget,
  deleteMonitoredTarget,
  fetchMonitoredTargets,
  updateMonitoredTarget,
} from "@/lib/api";
import type { MonitoredTarget, MonitoringFrequency } from "@/lib/types";

export function MonitoringPanel() {
  const [targets, setTargets] = useState<MonitoredTarget[]>([]);
  const [domain, setDomain] = useState("");
  const [frequency, setFrequency] = useState<MonitoringFrequency>("daily");
  const [webhookUrl, setWebhookUrl] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const loadTargets = useCallback(async () => {
    setBusy(true);
    setError(null);
    try {
      setTargets(await fetchMonitoredTargets());
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo cargar la vigilancia");
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    const frame = requestAnimationFrame(() => {
      void loadTargets();
    });
    return () => cancelAnimationFrame(frame);
  }, [loadTargets]);

  const handleCreate = async () => {
    if (!domain.trim()) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await createMonitoredTarget(domain, frequency, webhookUrl);
      setDomain("");
      setWebhookUrl("");
      setTargets(await fetchMonitoredTargets());
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo registrar el dominio");
    } finally {
      setBusy(false);
    }
  };

  const handleToggle = async (target: MonitoredTarget) => {
    setBusy(true);
    setError(null);
    try {
      await updateMonitoredTarget(target.id, !target.active);
      setTargets(await fetchMonitoredTargets());
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo actualizar el dominio");
    } finally {
      setBusy(false);
    }
  };

  const handleDelete = async (target: MonitoredTarget) => {
    setBusy(true);
    setError(null);
    try {
      await deleteMonitoredTarget(target.id);
      setTargets(await fetchMonitoredTargets());
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo eliminar el dominio");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid min-h-0 flex-1 gap-4 p-4 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
      <Panel
        title="Vigilancia 24/7"
        subtitle="Re-escaneo pasivo diario o semanal con alertas webhook"
      >
        {error ? <p className="mb-3 text-[11px] text-terminal-alert">{error}</p> : null}
        <div className="space-y-3">
          <label className="block space-y-1">
            <span className="text-[10px] uppercase tracking-widest text-terminal-muted">
              dominio vigilado
            </span>
            <input
              value={domain}
              onChange={(event) => setDomain(event.target.value)}
              placeholder="ejemplo.com"
              className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-xs text-terminal-text"
            />
          </label>
          <label className="block space-y-1">
            <span className="text-[10px] uppercase tracking-widest text-terminal-muted">
              frecuencia
            </span>
            <select
              value={frequency}
              onChange={(event) => setFrequency(event.target.value as MonitoringFrequency)}
              className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-xs text-terminal-text"
            >
              <option value="daily">diaria</option>
              <option value="weekly">semanal</option>
            </select>
          </label>
          <label className="block space-y-1">
            <span className="text-[10px] uppercase tracking-widest text-terminal-muted">
              webhook opcional (Discord / Slack / Telegram)
            </span>
            <input
              value={webhookUrl}
              onChange={(event) => setWebhookUrl(event.target.value)}
              placeholder="https://..."
              className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-xs text-terminal-text"
            />
          </label>
          <Button disabled={busy || !domain.trim()} onClick={() => void handleCreate()}>
            ACTIVAR VIGILANCIA
          </Button>
        </div>
      </Panel>

      <Panel
        title="Dominios monitorizados"
        subtitle="Activa, pausa o retira cada objetivo autorizado"
        actions={
          <Button variant="ghost" disabled={busy} onClick={() => void loadTargets()}>
            ACTUALIZAR
          </Button>
        }
      >
        <div className="space-y-2">
          {targets.length > 0 ? (
            targets.map((target) => (
              <div
                key={target.id}
                className="rounded border border-terminal-border bg-terminal-bg/60 p-3"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-xs text-terminal-text">{target.domain}</p>
                    <p className="text-[10px] text-terminal-muted">
                      {target.frequency} ·{" "}
                      {target.last_run_at
                        ? `último ${new Date(target.last_run_at).toLocaleString("es-ES")}`
                        : "sin ejecuciones"}
                    </p>
                  </div>
                  <Badge tone={target.active ? "signal" : "neutral"}>
                    {target.active ? "activo" : "pausado"}
                  </Badge>
                </div>
                <p className="mt-2 truncate text-[10px] text-terminal-muted">
                  {target.webhook_url ?? "webhook global de .env"}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Button variant="ghost" disabled={busy} onClick={() => void handleToggle(target)}>
                    {target.active ? "PAUSAR" : "ACTIVAR"}
                  </Button>
                  <Button variant="ghost" disabled={busy} onClick={() => void handleDelete(target)}>
                    ELIMINAR
                  </Button>
                </div>
              </div>
            ))
          ) : (
            <p className="text-[11px] text-terminal-muted">
              No hay dominios en vigilancia continua.
            </p>
          )}
        </div>
      </Panel>
    </div>
  );
}
