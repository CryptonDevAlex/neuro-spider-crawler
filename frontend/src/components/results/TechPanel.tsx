"use client";

import { Badge } from "@/components/ui/Badge";
import { useScanStore } from "@/store/scan-store";

export function TechPanel() {
  const technologies = useScanStore((state) => state.technologies);
  const headers = useScanStore((state) => state.headers);
  const subdomains = useScanStore((state) => state.subdomains);
  const wafDetections = useScanStore((state) => state.wafDetections);
  const forms = useScanStore((state) => state.nodes.reduce((total, node) => total + node.forms, 0));

  return (
    <div className="space-y-4 rounded border border-terminal-border bg-terminal-bg/60 p-4">
      <div>
        <p className="text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
          tecnologías detectadas
        </p>
        <p className="mt-2 text-xs text-terminal-text">
          Servidor: {technologies.server ?? "no identificado"}
        </p>
        <div className="mt-2 flex flex-wrap gap-2">
          {technologies.frameworks.length > 0 ? (
            technologies.frameworks.map((framework) => (
              <Badge key={framework} tone="accent">
                {framework}
              </Badge>
            ))
          ) : (
            <span className="text-[11px] text-terminal-muted">frameworks no identificados</span>
          )}
        </div>
      </div>

      <div>
        <p className="text-[10px] uppercase tracking-[0.2em] text-terminal-muted">WAF/CDN</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {wafDetections.length > 0 ? (
            wafDetections.map((detection) => (
              <Badge key={detection.name} tone="accent">
                {detection.name}
              </Badge>
            ))
          ) : (
            <span className="text-[11px] text-terminal-muted">no identificado</span>
          )}
        </div>
        {wafDetections.length > 0 ? (
          <div className="mt-2 space-y-1">
            {wafDetections.map((detection) => (
              <p key={`${detection.name}-evidence`} className="text-[10px] text-terminal-muted">
                {detection.evidence}
              </p>
            ))}
          </div>
        ) : null}
      </div>

      <div>
        <p className="text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
          subdominios por certificate transparency ({subdomains.length})
        </p>
        <div className="mt-2 flex flex-wrap gap-2">
          {subdomains.length > 0 ? (
            subdomains.slice(0, 30).map((subdomain) => (
              <span key={subdomain} className="text-[10px] text-terminal-text">
                {subdomain}
              </span>
            ))
          ) : (
            <span className="text-[11px] text-terminal-muted">sin subdominios adicionales</span>
          )}
        </div>
      </div>

      {technologies.cookies.length > 0 ? (
        <div className="space-y-1">
          <p className="text-[10px] uppercase tracking-[0.2em] text-terminal-muted">cookies</p>
          {technologies.cookies.map((cookie) => (
            <p key={cookie.name} className="text-[11px] text-terminal-text">
              {cookie.name} · HttpOnly {cookie.http_only ? "sí" : "no"} · Secure{" "}
              {cookie.secure ? "sí" : "no"} · SameSite {cookie.same_site ?? "no declarado"}
            </p>
          ))}
        </div>
      ) : null}

      <div>
        <p className="text-[10px] uppercase tracking-[0.2em] text-terminal-muted">
          cabeceras de seguridad ({forms} formularios inventariados)
        </p>
        <div className="mt-2 grid gap-1">
          {headers.length > 0 ? (
            headers.map((header) => (
              <div
                key={header.name}
                className="flex items-center justify-between gap-3 text-[11px]"
              >
                <span className="truncate text-terminal-text">{header.name}</span>
                <Badge tone={header.present ? "signal" : "alert"}>
                  {header.present ? "presente" : "ausente"}
                </Badge>
              </div>
            ))
          ) : (
            <span className="text-[11px] text-terminal-muted">
              Las cabeceras se mostrarán al finalizar el análisis.
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
