"use client";

import { create } from "zustand";

import {
  fetchCurrentUser,
  login as loginRequest,
  logout as logoutRequest,
  register as registerRequest,
} from "@/lib/api";
import type { AuthUser, LoginRequest, RegisterRequest } from "@/lib/types";

type AuthStatus = "checking" | "authenticated" | "anonymous";

interface AuthState {
  user: AuthUser | null;
  status: AuthStatus;
  error: string | null;
  hydrate: () => Promise<void>;
  signIn: (payload: LoginRequest) => Promise<void>;
  signUp: (payload: RegisterRequest) => Promise<void>;
  signOut: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  status: "checking",
  error: null,

  hydrate: async () => {
    try {
      const user = await fetchCurrentUser();
      set({ user, status: "authenticated", error: null });
    } catch {
      set({ user: null, status: "anonymous", error: null });
    }
  },

  signIn: async (payload) => {
    set({ error: null });
    try {
      await loginRequest(payload);
      const user = await fetchCurrentUser();
      set({ user, status: "authenticated", error: null });
    } catch (cause) {
      set({
        user: null,
        status: "anonymous",
        error: cause instanceof Error ? cause.message : "No se pudo iniciar sesión",
      });
      throw cause;
    }
  },

  signUp: async (payload) => {
    set({ error: null });
    try {
      await registerRequest(payload);
      const user = await fetchCurrentUser();
      set({ user, status: "authenticated", error: null });
    } catch (cause) {
      set({
        user: null,
        status: "anonymous",
        error: cause instanceof Error ? cause.message : "No se pudo crear la cuenta",
      });
      throw cause;
    }
  },

  signOut: async () => {
    try {
      await logoutRequest();
    } finally {
      set({ user: null, status: "anonymous", error: null });
    }
  },
}));
