import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

interface BadgeProps {
  children: ReactNode;
  tone?: "neutral" | "signal" | "alert" | "accent";
}

const tones = {
  neutral: "border-terminal-border text-terminal-muted",
  signal: "border-terminal-signal/50 text-terminal-signal",
  alert: "border-terminal-alert/50 text-terminal-alert",
  accent: "border-terminal-accent/50 text-terminal-accent",
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
