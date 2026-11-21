"use client";

import { type FormEvent, useState } from "react";

import { Button } from "@/components/ui/Button";
import { googleLoginUrl } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";

type AuthMode = "login" | "register";

export function LoginScreen() {
  const signIn = useAuthStore((state) => state.signIn);
  const signUp = useAuthStore((state) => state.signUp);
  const error = useAuthStore((state) => state.error);
  const [mode, setMode] = useState<AuthMode>("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("admin@neurospider.local");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    try {
      if (mode === "login") {
        await signIn({ email, password });
      } else {
        await signUp({ full_name: fullName, email, password });
      }
    } catch {
      return;
    } finally {
      setLoading(false);
    }
  };

  const handleGoogle = () => {
    window.location.assign(googleLoginUrl());
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-terminal-bg p-6">
      <div className="grid w-full max-w-4xl overflow-hidden rounded-lg border border-terminal-border bg-terminal-panel/80 shadow-2xl shadow-black/60 md:grid-cols-2">
        <section className="relative hidden flex-col justify-between overflow-hidden border-r border-terminal-border bg-[#080d16] p-8 md:flex">
          <div className="absolute inset-0 opacity-30 [background-image:linear-gradient(rgba(34,211,238,0.12)_1px,transparent_1px),linear-gradient(90deg,rgba(34,211,238,0.12)_1px,transparent_1px)] [background-size:28px_28px]" />
          <div className="relative">
            <p className="text-[10px] uppercase tracking-[0.35em] text-terminal-accent">
              neurospider / secure access
            </p>
            <h1 className="mt-8 text-3xl font-bold leading-tight tracking-tight text-terminal-text">
              Panel de operaciones
              <span className="block text-terminal-accent">Red Team / OSINT</span>
            </h1>
            <p className="mt-4 text-xs leading-relaxed text-terminal-muted">
              Cada cuenta conserva su propio historial, comparador y vigilancia en SQLite. El
              acceso se valida con JWT y cookies httpOnly.
            </p>
          </div>
          <div className="relative mt-10 space-y-2 text-[10px] uppercase tracking-widest text-terminal-muted">
            <p className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-terminal-signal" />
              cuentas locales + Google OIDC
            </p>
            <p className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-terminal-accent" />
              datos privados por user_id
            </p>
          </div>
        </section>

        <section className="p-8">
          <div className="mb-6">
            <div className="flex h-10 w-10 items-center justify-center rounded border border-terminal-accent/40 bg-terminal-accent/10 text-sm font-bold text-terminal-accent">
              NS
            </div>
            <h2 className="mt-6 text-lg font-semibold tracking-wide text-terminal-text">
              {mode === "login" ? "INICIAR SESIÓN" : "CREAR CUENTA"}
            </h2>
            <p className="mt-1 text-[11px] text-terminal-muted">
              {mode === "login"
                ? "Acceso restringido a operadores autorizados."
                : "Registro local: tus auditorías serán privadas."}
            </p>
          </div>

          <form onSubmit={(event) => void handleSubmit(event)} className="space-y-4">
            {mode === "register" ? (
              <label className="block space-y-1">
                <span className="text-[10px] uppercase tracking-widest text-terminal-muted">
                  nombre completo
                </span>
                <input
                  type="text"
                  required
                  autoComplete="name"
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm text-terminal-text outline-none placeholder:text-terminal-muted focus:border-terminal-accent"
                  placeholder="Operador Alpha"
                />
              </label>
            ) : null}
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
                className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm text-terminal-text outline-none placeholder:text-terminal-muted focus:border-terminal-accent"
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
                minLength={mode === "register" ? 8 : 1}
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm text-terminal-text outline-none placeholder:text-terminal-muted focus:border-terminal-accent"
                placeholder="••••••••"
              />
            </label>
            {error ? <p className="text-[11px] text-terminal-alert">{error}</p> : null}
            <Button type="submit" disabled={loading} className="w-full">
              {loading ? "verificando..." : mode === "login" ? "entrar al panel" : "registrar cuenta"}
            </Button>
          </form>

          <div className="my-5 flex items-center gap-3">
            <span className="h-px flex-1 bg-terminal-border" />
            <span className="text-[9px] uppercase tracking-widest text-terminal-muted">o</span>
            <span className="h-px flex-1 bg-terminal-border" />
          </div>

          <Button variant="ghost" onClick={handleGoogle} className="w-full">
            iniciar sesión / registrarse con google
          </Button>

          <button
            type="button"
            onClick={() => setMode(mode === "login" ? "register" : "login")}
            className="mt-5 text-[10px] uppercase tracking-widest text-terminal-accent hover:underline"
          >
            {mode === "login" ? "crear cuenta" : "volver al inicio de sesión"}
          </button>

          <p className="mt-6 text-[10px] leading-relaxed text-terminal-muted">
            Usuario inicial: <span className="text-terminal-text">admin@neurospider.local</span> ·{" "}
            <span className="text-terminal-text">admin1234</span>. Cambia estas credenciales en
            producción.
          </p>
        </section>
      </div>
    </main>
  );
}
