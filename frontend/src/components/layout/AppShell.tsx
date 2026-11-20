import type { ReactNode } from "react";

import { StatusBar } from "./StatusBar";
import { TopBar } from "./TopBar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen flex-col overflow-hidden">
      <TopBar />
      <main className="flex min-h-0 flex-1 flex-col">{children}</main>
      <StatusBar />
    </div>
  );
}
