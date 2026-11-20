"use client";

import { create } from "zustand";

export type SuiteView = "recon" | "history" | "monitoring";

interface UiState {
  view: SuiteView;
  setView: (view: SuiteView) => void;
}

export const useUiStore = create<UiState>((set) => ({
  view: "recon",
  setView: (view) => set({ view }),
}));
