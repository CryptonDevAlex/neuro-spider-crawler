"use client";

import { type FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { useAuthStore } from "@/store/auth-store";

interface RegisterModalProps {
  onClose: () => void;
}

export function RegisterModal({ onClose }: RegisterModalProps) {
  const signUp = useAuthStore((state) => state.signUp);
  const storeError = useAuthStore((state) => state.error);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLocalError(null);

    if (password !== confirmPassword) {
      setLocalError("Las contraseñas no coinciden.");
      return;
    }

    setLoading(true);
    try {
      await signUp({
        full_name: fullName.trim(),
        email: email.trim(),
        password,
      });
      onClose();
    } catch (cause) {
      setLocalError(
        cause instanceof Error ? cause.message : "No se pudo crear la cuenta local.",
      );
    } finally {
      setLoading(false);
    }
  };

  const error = localError ?? storeError;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="register-title"
        aria-describedby="register-description"
        className="max-h-[90vh] w-full max-w-md overflow-y-auto rounded-lg border border-terminal-border bg-terminal-panel p-6 shadow-2xl shadow-black/70"
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-[10px] uppercase tracking-[0.3em] text-terminal-signal">
              cuenta local · sqlite
            </p>
            <h2 id="register-title" className="mt-2 text-lg font-semibold text-terminal-text">
              REGISTRARSE
            </h2>
            <p id="register-description" className="mt-1 text-[11px] text-terminal-muted">
              Tu cuenta se crea en la base local y entra al panel automáticamente.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Cerrar registro"
            className="rounded border border-transparent px-2 py-1 text-terminal-muted hover:border-terminal-border hover:text-terminal-text"
          >
            ×
          </button>
        </div>

        <form onSubmit={(event) => void handleSubmit(event)} className="mt-6 space-y-4">
          <label className="block space-y-1">
            <span className="text-[10px] uppercase tracking-widest text-terminal-muted">
              nombre completo
            </span>
            <input
              type="text"
              required
              autoFocus
              autoComplete="name"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm text-terminal-text outline-none focus:border-terminal-signal"
              placeholder="Operador Alpha"
            />
          </label>

          <label className="block space-y-1">
            <span className="text-[10px] uppercase tracking-widest text-terminal-muted">
              correo electrónico
            </span>
            <input
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm text-terminal-text outline-none focus:border-terminal-signal"
              placeholder="operador@empresa.com"
            />
          </label>

          <label className="block space-y-1">
            <span className="text-[10px] uppercase tracking-widest text-terminal-muted">
              contraseña
            </span>
            <input
              type="password"
              required
              minLength={8}
              autoComplete="new-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm text-terminal-text outline-none focus:border-terminal-signal"
              placeholder="Mínimo 8 caracteres"
            />
          </label>

          <label className="block space-y-1">
            <span className="text-[10px] uppercase tracking-widest text-terminal-muted">
              confirmar contraseña
            </span>
            <input
              type="password"
              required
              minLength={8}
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm text-terminal-text outline-none focus:border-terminal-signal"
              placeholder="Repite la contraseña"
            />
          </label>

          {error ? <p className="text-[11px] text-terminal-alert">{error}</p> : null}

          <div className="space-y-2 pt-2">
            <Button type="submit" disabled={loading} className="w-full">
              {loading ? "creando cuenta..." : "crear cuenta local"}
            </Button>
            <Button type="button" variant="secondary" onClick={onClose} className="w-full">
              volver a iniciar sesión
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
