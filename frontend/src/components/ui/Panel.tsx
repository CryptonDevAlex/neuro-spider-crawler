import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

interface PanelProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  className?: string;
  children: ReactNode;
}

export function Panel({ title, subtitle, actions, className, children }: PanelProps) {
  return (
    <section
      className={cn(
        "relative flex min-h-0 flex-col overflow-hidden rounded-lg border border-terminal-border bg-terminal-panel/80",
        className,
      )}
    >
      <header className="flex items-center justify-between gap-3 border-b border-terminal-border px-4 py-3">
        <div>
          <h2 className="text-xs font-semibold uppercase tracking-[0.2em] text-terminal-text">
            {title}
          </h2>
          {subtitle ? <p className="mt-1 text-[10px] text-terminal-muted">{subtitle}</p> : null}
        </div>
        {actions}
      </header>
      <div className="min-h-0 flex-1 overflow-auto p-4">{children}</div>
      <div className="scanline absolute inset-0" />
    </section>
  );
}
