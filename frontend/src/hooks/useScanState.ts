"use client";

import { useScanStore } from "@/store/scan-store";

export function useScanState() {
  return useScanStore();
}
