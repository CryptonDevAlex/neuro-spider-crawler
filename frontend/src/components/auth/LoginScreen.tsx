"use client";

import { type FormEvent, useState } from "react";

import { RegisterModal } from "@/components/auth/RegisterModal";
import { Button } from "@/components/ui/Button";
import { checkGoogleAvailability, googleLoginUrl } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";

export function LoginScreen() {
  const signIn = useAuthStore((state) => state.signIn);
  const error = useAuthStore((state) => state.error);
  const [email, setEmail] = useState("admin@neurospider.local");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [googleNotice, setGoogleNotice] = useState<string | null>(null);

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setGoogleNotice(null);
    setLoading(true);
    try {
      await signIn({ email, password });
    } catch {
      return;
    } finally {
      setLoading(false);
    }
  };

  const handleGoogle = async () => {
    setGoogleNotice(null);
    setGoogleLoading(true);
    const availability = await checkGoogleAvailability();
    setGoogleLoading(false);

    if (availability.available) {
      window.location.assign(googleLoginUrl());
      return;
    }

    setGoogleNotice(availability.message);
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
              Cuenta local en SQLite o acceso corporativo con Google. Cada sesión conserva su
              historial, comparador y vigilancia de forma privada.
            </p>
          </div>
          <div className="relative mt-10 space-y-2 text-[10px] uppercase tracking-widest text-terminal-muted">
            <p className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-terminal-signal" />
              registro local en sqlite
            </p>
            <p className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-terminal-accent" />
              google oidc opcional
            </p>
          </div>
        </section>

        <section className="p-8">
          <div className="mb-6">
            <div className="flex h-10 w-10 items-center justify-center rounded border border-terminal-accent/40 bg-terminal-accent/10 text-sm font-bold text-terminal-accent">
              NS
            </div>
            <h2 className="mt-6 text-lg font-semibold tracking-wide text-terminal-text">
              INICIAR SESIÓN
            </h2>
            <p className="mt-1 text-[11px] text-terminal-muted">
              Introduce tus credenciales para entrar al panel.
            </p>
          </div>

          <form onSubmit={(event) => void handleLogin(event)} className="space-y-4">
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
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm text-terminal-text outline-none placeholder:text-terminal-muted focus:border-terminal-accent"
                placeholder="••••••••"
              />
            </label>

            {error ? <p className="text-[11px] text-terminal-alert">{error}</p> : null}

            <Button type="submit" disabled={loading} className="w-full">
              {loading ? "verificando..." : "entrar al panel"}
            </Button>
          </form>

          {googleNotice ? (
            <div
              role="status"
              className="mt-5 rounded border border-terminal-accent/40 bg-terminal-accent/5 p-3"
            >
              <div className="flex items-center justify-between gap-3">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-terminal-accent">
                  aviso
                </p>
                <button
                  type="button"
                  onClick={() => setGoogleNotice(null)}
                  aria-label="Cerrar aviso"
                  className="text-terminal-muted hover:text-terminal-text"
                >
                  ×
                </button>
              </div>
              <p className="mt-2 text-[11px] leading-relaxed text-terminal-text">{googleNotice}</p>
            </div>
          ) : null}

          <div className="mt-6 border-t border-terminal-border pt-5">
            <p className="mb-3 text-[10px] uppercase tracking-widest text-terminal-muted">
              otras formas de acceso
            </p>
            <div className="space-y-3">
              <div>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    setGoogleNotice(null);
                    setShowRegister(true);
                  }}
                  className="w-full"
                >
                  registrarse
                </Button>
                <p className="mt-1 text-[10px] text-terminal-muted">
                  Crea una cuenta local en SQLite y entra automáticamente.
                </p>
              </div>
              <div>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => void handleGoogle()}
                  disabled={googleLoading}
                  className="w-full"
                >
                  {googleLoading ? "verificando google..." : "continuar con google"}
                </Button>
                <p className="mt-1 text-[10px] text-terminal-muted">
                  OAuth2 corporativo; disponible si el servidor está configurado.
                </p>
              </div>
            </div>
          </div>

          <p className="mt-6 text-[10px] leading-relaxed text-terminal-muted">
            Usuario inicial: <span className="text-terminal-text">admin@neurospider.local</span> ·{" "}
            <span className="text-terminal-text">admin1234</span>. Cambia estas credenciales en
            producción.
          </p>
        </section>
      </div>

      {showRegister ? <RegisterModal onClose={() => setShowRegister(false)} /> : null}
    </main>
  );
}
