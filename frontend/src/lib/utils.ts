import type { Severity } from "./types";

export type BadgeTone =
  | "neutral"
  | "signal"
  | "alert"
  | "accent"
  | "critical"
  | "high"
  | "medium"
  | "low"
  | "info";

export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("es-ES").format(value);
}

export function severityTone(severity: Severity): BadgeTone {
  switch (severity) {
    case "CRITICO":
      return "critical";
    case "ALTO":
      return "high";
    case "MEDIO":
      return "medium";
    case "BAJO":
      return "low";
    case "INFO":
      return "info";
  }
}
