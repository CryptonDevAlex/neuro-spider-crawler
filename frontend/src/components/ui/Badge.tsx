import type { ReactNode } from "react";

import { cn, type BadgeTone } from "@/lib/utils";

interface BadgeProps {
  children: ReactNode;
  tone?: BadgeTone;
}

const tones: Record<BadgeTone, string> = {
  neutral: "border-terminal-border text-terminal-muted",
  signal: "border-terminal-signal/50 text-terminal-signal",
  alert: "border-terminal-alert/50 text-terminal-alert",
  accent: "border-terminal-accent/50 text-terminal-accent",
  critical: "border-rose-400/70 bg-rose-500/10 text-rose-300",
  high: "border-orange-400/60 bg-orange-500/10 text-orange-300",
  medium: "border-amber-400/60 bg-amber-500/10 text-amber-300",
  low: "border-cyan-400/50 bg-cyan-500/10 text-cyan-300",
  info: "border-slate-400/50 bg-slate-500/10 text-slate-300",
};

export function Badge({ children, tone = "neutral" }: BadgeProps) {
  return (
    <span
      className={cn(
        "rounded-full border px-2 py-0.5 text-[10px] uppercase tracking-widest",
        tones[tone],
      )}
    >
      {children}
    </span>
  );
}
