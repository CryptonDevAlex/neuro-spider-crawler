import type { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  children: ReactNode;
}

export function Button({ className, variant = "primary", children, ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "rounded border px-4 py-2 text-xs font-semibold uppercase tracking-widest transition-colors disabled:cursor-not-allowed disabled:opacity-40",
        variant === "primary"
          ? "border-terminal-accent bg-terminal-accent/10 text-terminal-accent hover:bg-terminal-accent/20"
          : variant === "secondary"
            ? "border-terminal-signal bg-terminal-signal/10 text-terminal-signal hover:bg-terminal-signal/20"
            : variant === "danger"
              ? "border-terminal-alert bg-terminal-alert/10 text-terminal-alert hover:bg-terminal-alert/20"
              : "border-terminal-border bg-transparent text-terminal-muted hover:text-terminal-text",
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}
